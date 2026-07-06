#!/usr/bin/env python3
"""
Stale-detection (Roadmap Phase 4). Flags published skills whose `last_reviewed`
is older than STALE_MONTHS and opens a "Review fällig" issue for the owner —
idempotently (skips if an open issue for that skill already exists).

Env:
    STALE_MONTHS   default 6
    GH_TOKEN       for `gh` (set in CI). Without it, runs read-only.
Flags:
    --dry-run      list stale skills, never touch issues (local testing)
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
STALE_MONTHS = int(os.environ.get("STALE_MONTHS", "6"))
LABEL = "review-due"
TITLE_PREFIX = "[Review fällig]"


def months_between(d, today):
    return (today.year - d.year) * 12 + (today.month - d.month) - (1 if today.day < d.day else 0)


def gh(*args, check=True):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def existing_open_titles():
    try:
        r = gh("issue", "list", "--state", "open", "--label", LABEL,
               "--json", "title", "--limit", "200", check=False)
        if r.returncode != 0:
            return set()
        return {i["title"] for i in json.loads(r.stdout or "[]")}
    except Exception:
        return set()


def main():
    dry = "--dry-run" in sys.argv
    today = datetime.date.today()

    stale = []
    for d in sorted(SKILLS_DIR.iterdir()):
        mf = d / "metadata.json"
        if not mf.exists():
            continue
        meta = json.loads(mf.read_text(encoding="utf-8"))
        if meta.get("status") != "published":
            continue
        lr = meta.get("last_reviewed")
        if not lr:
            continue
        reviewed = datetime.date.fromisoformat(lr)
        age = months_between(reviewed, today)
        if age >= STALE_MONTHS:
            stale.append((meta, age))

    if not stale:
        print(f"OK — no skills older than {STALE_MONTHS} month(s).")
        return

    print(f"{len(stale)} stale skill(s) (threshold {STALE_MONTHS} months):")
    open_titles = set() if dry else existing_open_titles()

    for meta, age in stale:
        title = f"{TITLE_PREFIX} {meta['id']}"
        print(f"  - {meta['id']}: last reviewed {meta['last_reviewed']} ({age} months ago)")
        if dry:
            continue
        if title in open_titles:
            print(f"    (issue already open, skipping)")
            continue
        owner = meta.get("owner", "")
        body = (
            f"The skill **{meta['id']}** was last reviewed on {meta['last_reviewed']} "
            f"({age} months ago), exceeding the {STALE_MONTHS}-month review window.\n\n"
            f"@{owner} — please re-verify the skill and either bump `last_reviewed` "
            f"or deprecate it.\n\n_Opened automatically by stale-detection._"
        )
        r = gh("issue", "create", "--title", title, "--label", LABEL,
               "--body", body, check=False)
        print(f"    {'created' if r.returncode == 0 else 'FAILED: ' + r.stderr.strip()}")


if __name__ == "__main__":
    main()
