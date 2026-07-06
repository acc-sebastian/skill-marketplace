#!/usr/bin/env python3
"""
Auto-archive deprecated skills past their sunset_date (Roadmap Phase 4).

Moves each `deprecated` skill whose `sunset_date <= today` from skills/<id>/ to
archived/<id>/ and sets status to "archived". The build already excludes
archived skills from the site and catalog, so archiving removes them from
distribution while preserving provenance in the repo.

The workflow commits the moves on a branch and opens a PR. This script only
performs the filesystem moves + metadata edit (and prints what it did); it does
not touch git.

Flags:
    --dry-run   list what would be archived, change nothing
Outputs (to $GITHUB_OUTPUT if set): archived=<space-separated ids>
"""

import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
ARCHIVE_DIR = ROOT / "archived"


def main():
    dry = "--dry-run" in sys.argv
    today = datetime.date.today()
    archived = []

    for d in sorted(SKILLS_DIR.iterdir()):
        mf = d / "metadata.json"
        if not mf.exists():
            continue
        meta = json.loads(mf.read_text(encoding="utf-8"))
        if meta.get("status") != "deprecated":
            continue
        sunset = meta.get("sunset_date")
        if not sunset or datetime.date.fromisoformat(sunset) > today:
            continue

        print(f"  archive {meta['id']} (sunset {sunset})")
        archived.append(meta["id"])
        if dry:
            continue

        meta["status"] = "archived"
        mf.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ARCHIVE_DIR.mkdir(exist_ok=True)
        d.rename(ARCHIVE_DIR / d.name)

    if not archived:
        print("OK — nothing past its sunset date.")
    else:
        print(f"{'Would archive' if dry else 'Archived'}: {', '.join(archived)}")

    out = os.environ.get("GITHUB_OUTPUT")
    if out and not dry:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"archived={' '.join(archived)}\n")


if __name__ == "__main__":
    main()
