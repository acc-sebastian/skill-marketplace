#!/usr/bin/env python3
"""
Eval harness — LLM-as-judge regression check for skills.

For each published skill that ships an evals.json, run every runnable eval
(SKILL.md body as system prompt, the eval's `prompt` as the user message)
against the current Claude model, then have a judge model grade the response
against the eval's assertions. Writes a machine-readable eval-results.json that
build_site.py turns into an "evaluated" badge on the card and in the modal.

This is a model-drift guard: run on a schedule, it re-proves each skill still
behaves as specified against whatever model is current, and surfaces the result
on the site instead of leaving it buried in a CI log.

Gracefully SKIPS (exit 0) when ANTHROPIC_API_KEY is not set, so it never blocks
contributors who don't have a key — same contract as smoke_test.py.

Env:
    ANTHROPIC_API_KEY   required to actually run (else skip)
    EVAL_MODEL          model under test (default claude-opus-4-8)
    EVAL_JUDGE_MODEL    grader model (default = EVAL_MODEL)
    EVAL_DATE           ISO date to stamp results with (default: today)

Exit code: 0 on success (all runnable evals passed, or skipped-without-key),
1 if any runnable eval failed — so a scheduled run turns red on real drift.
"""

import datetime
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "accilium-skills" / "skills"
RESULTS_FILE = ROOT / "eval-results.json"

EVAL_MODEL = os.environ.get("EVAL_MODEL", "claude-opus-4-8")
JUDGE_MODEL = os.environ.get("EVAL_JUDGE_MODEL", EVAL_MODEL)

FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def strip_frontmatter(md):
    return FRONTMATTER.sub("", md, count=1).strip()


def find_evals_file(skill_dir):
    """Evals may live at <skill>/evals/evals.json or <skill>/evals.json."""
    for cand in (skill_dir / "evals" / "evals.json", skill_dir / "evals.json"):
        if cand.exists():
            return cand
    return None


def is_runnable(ev, skill_dir):
    """An eval is runnable if it needs no fixture files, or all listed files
    are real paths inside the skill folder. Placeholder descriptions (wrapped
    in <angle brackets>) mean 'no real file provided' -> not runnable yet."""
    files = ev.get("files") or []
    for f in files:
        if f.strip().startswith("<"):
            return False, "needs fixture file (placeholder only)"
        if not (skill_dir / f).exists():
            return False, f"fixture file not found: {f}"
    return True, None


def judge(client, output, expected, assertions):
    """Grade the response against each assertion. Returns a list aligned to
    `assertions`: [{"pass": bool, "reason": str}, ...]."""
    numbered = "\n".join(f"{i+1}. {a['text']}" for i, a in enumerate(assertions))
    prompt = (
        "You are grading an AI assistant's response against a checklist of "
        "assertions. Be strict but fair: mark an assertion pass only if the "
        "response clearly satisfies it.\n\n"
        f"RESPONSE TO GRADE:\n<response>\n{output}\n</response>\n\n"
        f"WHAT A GOOD RESPONSE LOOKS LIKE:\n{expected or '(not specified)'}\n\n"
        "For each assertion, decide pass or fail. Reply with ONLY a JSON array, "
        "one object per assertion IN ORDER, no prose:\n"
        '[{"pass": true, "reason": "<=20 words"}, ...]\n\n'
        f"ASSERTIONS:\n{numbered}"
    )
    resp = client.messages.create(
        model=JUDGE_MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        raise ValueError(f"judge returned no JSON array: {text[:120]}")
    verdicts = json.loads(m.group(0))
    if len(verdicts) != len(assertions):
        raise ValueError(f"judge returned {len(verdicts)} verdicts for {len(assertions)} assertions")
    return verdicts


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("SKIP — ANTHROPIC_API_KEY not set; evals not run.")
        return

    try:
        import anthropic
    except ImportError:
        sys.exit("error: anthropic SDK not installed (pip install anthropic)")

    client = anthropic.Anthropic()
    today = os.environ.get("EVAL_DATE") or datetime.date.today().isoformat()

    results = {}
    any_fail = False

    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        mf, sf, ef = d / "metadata.json", d / "SKILL.md", find_evals_file(d)
        if not (mf.exists() and sf.exists() and ef):
            continue
        meta = json.loads(mf.read_text(encoding="utf-8"))
        if meta.get("status") != "published":
            continue

        try:
            evals = json.loads(ef.read_text(encoding="utf-8")).get("evals", [])
        except json.JSONDecodeError as e:
            print(f"  SKIP {d.name} (evals.json invalid: {e})")
            continue

        system = strip_frontmatter(sf.read_text(encoding="utf-8"))
        print(f"\n{d.name} — {len(evals)} eval(s)")

        eval_results = []
        passed = failed = skipped = 0
        for ev in evals:
            runnable, why = is_runnable(ev, d)
            if not runnable:
                skipped += 1
                eval_results.append({"id": ev.get("id"), "ran": False, "skip_reason": why})
                print(f"  skip #{ev.get('id')} ({why})")
                continue
            try:
                resp = client.messages.create(
                    model=EVAL_MODEL, max_tokens=4096, system=system,
                    messages=[{"role": "user", "content": ev["prompt"]}],
                )
                output = "".join(b.text for b in resp.content if b.type == "text").strip()
                verdicts = judge(client, output, ev.get("expected_output"), ev["assertions"])
            except Exception as e:
                failed += 1
                any_fail = True
                eval_results.append({"id": ev.get("id"), "ran": True, "passed": False,
                                     "error": str(e)})
                print(f"  FAIL #{ev.get('id')} (error: {e})")
                continue

            asserts = [{"text": a["text"], "pass": bool(v.get("pass")),
                        "reason": v.get("reason", "")}
                       for a, v in zip(ev["assertions"], verdicts)]
            ev_passed = all(a["pass"] for a in asserts)
            eval_results.append({"id": ev.get("id"), "ran": True,
                                 "passed": ev_passed, "assertions": asserts})
            if ev_passed:
                passed += 1
                print(f"  OK   #{ev.get('id')} ({len(asserts)}/{len(asserts)} assertions)")
            else:
                failed += 1
                any_fail = True
                n_ok = sum(a["pass"] for a in asserts)
                print(f"  FAIL #{ev.get('id')} ({n_ok}/{len(asserts)} assertions)")

        ran = passed + failed
        if ran == 0:
            status = "unverified"       # only skipped evals — nothing proven
        elif failed:
            status = "fail"
        elif skipped:
            status = "partial"          # everything that ran passed, some skipped
        else:
            status = "pass"

        results[meta["id"]] = {
            "version": meta.get("version"),
            "status": status,
            "passed": passed, "failed": failed, "skipped": skipped, "total": len(evals),
            "evals": eval_results,
        }

    payload = {
        "generated": today,
        "eval_model": EVAL_MODEL,
        "judge_model": JUDGE_MODEL,
        "skills": results,
    }
    RESULTS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(f"\nWrote {RESULTS_FILE.relative_to(ROOT)} — {len(results)} skill(s) evaluated.")
    if any_fail:
        print("At least one runnable eval failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
