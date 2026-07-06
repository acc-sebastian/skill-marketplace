#!/usr/bin/env python3
"""
LLM smoke-test / model-drift check (Roadmap Phase 4).

For each published skill with an `example_input`, run the skill (its SKILL.md
body as the system prompt) against the current Claude model and check the model
produces a usable, non-refused response. Run on a schedule, this doubles as a
model-drift check: it re-verifies skills against whatever model is current.

Gracefully SKIPS (exit 0) when ANTHROPIC_API_KEY is not set, so it never blocks
contributors who don't have a key.

Env:
    ANTHROPIC_API_KEY   required to actually run (else skip)
    SMOKE_MODEL         default claude-opus-4-8
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
MODEL = os.environ.get("SMOKE_MODEL", "claude-opus-4-8")

FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def strip_frontmatter(md):
    return FRONTMATTER.sub("", md, count=1).strip()


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("SKIP — ANTHROPIC_API_KEY not set; smoke-test not run.")
        return

    try:
        import anthropic
    except ImportError:
        sys.exit("error: anthropic SDK not installed (pip install anthropic)")

    client = anthropic.Anthropic()

    tested = passed = 0
    failures = []
    for d in sorted(SKILLS_DIR.iterdir()):
        mf, sf = d / "metadata.json", d / "SKILL.md"
        if not (mf.exists() and sf.exists()):
            continue
        meta = json.loads(mf.read_text(encoding="utf-8"))
        if meta.get("status") != "published":
            continue
        example = meta.get("example_input")
        if not example:
            print(f"  skip {meta['id']} (no example_input)")
            continue

        system = strip_frontmatter(sf.read_text(encoding="utf-8"))
        tested += 1
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": example}],
            )
        except Exception as e:
            failures.append(f"{meta['id']}: API error — {e}")
            print(f"  FAIL {meta['id']} (API error: {e})")
            continue

        if resp.stop_reason == "refusal":
            failures.append(f"{meta['id']}: model refused")
            print(f"  FAIL {meta['id']} (refusal)")
            continue
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        if len(text) < 20:
            failures.append(f"{meta['id']}: empty/short output ({len(text)} chars)")
            print(f"  FAIL {meta['id']} (output too short)")
            continue
        passed += 1
        print(f"  OK   {meta['id']} ({len(text)} chars, {resp.usage.output_tokens} out-tokens)")

    print(f"\nSmoke-test against {MODEL}: {passed}/{tested} passed.")
    if failures:
        print("Failures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
