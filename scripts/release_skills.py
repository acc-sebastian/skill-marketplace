#!/usr/bin/env python3
"""
Create a versioned GitHub Release per skill (tag = <id>@<version>) with
SKILL.md + metadata.json + a full skill zip attached as assets. Idempotent:
skips creating a release for a skill whose tag already exists, so it only
ever publishes *new* versions.

The zip asset is what the marketplace site's "Download skill (.zip)" button
links to — GitHub tracks download_count on release assets (unlike plain
files served from GitHub Pages, which have no download analytics at all),
and Insights reads that count. The zip is only uploaded once per release
(never re-uploaded once present) so re-running this script never resets an
already-accumulated download count.

Runs in CI (release.yml) with the `gh` CLI authenticated via GH_TOKEN.
"""

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "accilium-skills" / "skills"


def gh(*args, check=True):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def tag_exists(tag):
    # `gh release view` exits non-zero if the release doesn't exist
    return gh("release", "view", tag, check=False).returncode == 0


def release_has_asset(tag, filename):
    r = gh("release", "view", tag, "--json", "assets", check=False)
    if r.returncode != 0:
        return False
    try:
        assets = json.loads(r.stdout).get("assets", [])
    except json.JSONDecodeError:
        return False
    return any(a.get("name") == filename for a in assets)


def build_zip_asset(skill_dir, skill_id, dest_path):
    """SKILL.md plus any supporting files/subfolders, zipped as <skill_id>/...
    metadata.json is excluded — it's marketplace bookkeeping, not part of
    what Claude reads."""
    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file() and f.name != "metadata.json":
                zf.write(f, arcname=f"{skill_id}/{f.relative_to(skill_dir)}")


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
        is_new = not tag_exists(tag)

        if is_new:
            notes = f"**{meta.get('name')}** v{meta['version']}\n\n{meta.get('description','')}"
            cl = meta.get("changelog") or []
            if cl:
                notes += "\n\n### Changelog\n" + "\n".join(
                    f"- `{c['version']}` ({c['date']}): {c['change']}" for c in cl
                )
            assets = [str(sf), str(mf)] if sf.exists() else [str(mf)]
            gh("release", "create", tag, *assets, "--title", f"{meta.get('name')} {meta['version']}", "--notes", notes)
            created.append(tag)
        else:
            skipped.append(f"{tag} (exists)")

        # Backfill the zip asset for releases that predate this feature, and
        # attach it for newly created ones. Never re-upload once present.
        zip_name = f"{meta['id']}.zip"
        if not release_has_asset(tag, zip_name):
            with tempfile.TemporaryDirectory() as tmp:
                zip_path = Path(tmp) / zip_name
                build_zip_asset(d, meta["id"], zip_path)
                gh("release", "upload", tag, str(zip_path))

    print("Created releases:", ", ".join(created) if created else "(none)")
    print("Skipped:", ", ".join(skipped) if skipped else "(none)")


if __name__ == "__main__":
    main()
