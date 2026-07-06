#!/usr/bin/env python3
"""
Create a versioned GitHub Release per skill (tag = <id>@<version>) with
SKILL.md + metadata.json attached as assets. Idempotent: skips a skill whose
tag already exists, so it only ever publishes *new* versions.

Runs in CI (release.yml) with the `gh` CLI authenticated via GH_TOKEN.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"


def gh(*args, check=True):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def tag_exists(tag):
    # `gh release view` exits non-zero if the release doesn't exist
    return gh("release", "view", tag, check=False).returncode == 0


def main():
    created, skipped = [], []
    for d in sorted(SKILLS_DIR.iterdir()):
        mf = d / "metadata.json"
        sf = d / "SKILL.md"
        if not mf.exists():
            continue
        meta = json.loads(mf.read_text(encoding="utf-8"))

        # Never publish drafts or archived skills as releases
        if meta.get("status") in ("draft", "in-review", "archived"):
            skipped.append(f"{d.name} (status={meta.get('status')})")
            continue

        tag = f"{meta['id']}@{meta['version']}"
        if tag_exists(tag):
            skipped.append(f"{tag} (exists)")
            continue

        notes = f"**{meta.get('name')}** v{meta['version']}\n\n{meta.get('description','')}"
        cl = meta.get("changelog") or []
        if cl:
            notes += "\n\n### Changelog\n" + "\n".join(
                f"- `{c['version']}` ({c['date']}): {c['change']}" for c in cl
            )
        assets = [str(sf), str(mf)] if sf.exists() else [str(mf)]
        gh("release", "create", tag, *assets, "--title", f"{meta.get('name')} {meta['version']}", "--notes", notes)
        created.append(tag)

    print("Created releases:", ", ".join(created) if created else "(none)")
    print("Skipped:", ", ".join(skipped) if skipped else "(none)")


if __name__ == "__main__":
    main()
