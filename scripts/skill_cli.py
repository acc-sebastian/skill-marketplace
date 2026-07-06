#!/usr/bin/env python3
"""
skill — install skills from the Skill Marketplace straight into your harness.

Reads the live catalog manifest, so it always sees the latest published skills.
No dependencies beyond the Python standard library.

Usage:
    python scripts/skill_cli.py list [--all]
    python scripts/skill_cli.py search <query>
    python scripts/skill_cli.py info <skill-id>
    python scripts/skill_cli.py install <skill-id> [--harness claude-code|copilot-studio|generic] [--dest DIR]

Examples:
    python scripts/skill_cli.py list
    python scripts/skill_cli.py install mom-generator
    python scripts/skill_cli.py install kpi-anomaly-check --dest ~/.claude/skills

Set SKILL_CATALOG_URL to point at a different marketplace.
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

# Make stdout UTF-8 where possible so output is stable across platforms
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CATALOG_URL = os.environ.get(
    "SKILL_CATALOG_URL",
    "https://acc-sebastian.github.io/skill-marketplace/catalog.json",
)

# Where each harness expects skill files (relative to the current project)
HARNESS_DEST = {
    "claude-code": ".claude/skills",
    "copilot-studio": "copilot-skills",
    "generic": "skills",
}


def fetch_catalog():
    try:
        with urllib.request.urlopen(CATALOG_URL, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        sys.exit(f"error: could not fetch catalog from {CATALOG_URL}\n  {e}")


def fetch_text(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")


def find(catalog, skill_id):
    for s in catalog["skills"]:
        if s["id"] == skill_id:
            return s
    return None


def cmd_list(catalog, args):
    skills = catalog["skills"]
    if not args.all:
        skills = [s for s in skills if s.get("status") == "published"]
    print(f"{len(skills)} skill(s) in {catalog.get('site', 'marketplace')}:\n")
    for s in sorted(skills, key=lambda s: s["id"]):
        flag = "" if s.get("status") == "published" else f"  [{s.get('status')}]"
        print(f"  {s['id']:<28} {s.get('name','')}{flag}")
        print(f"  {'':<28} {s.get('category','')} | v{s.get('version','')} | {', '.join(s.get('harnesses', []))}")


def cmd_search(catalog, args):
    q = args.query.lower()
    hits = [
        s for s in catalog["skills"]
        if q in s["id"].lower()
        or q in (s.get("name", "").lower())
        or q in (s.get("description", "").lower())
        or any(q in t.lower() for t in s.get("tags", []))
    ]
    if not hits:
        print(f"No skills match '{args.query}'.")
        return
    for s in hits:
        print(f"  {s['id']:<28} {s.get('name','')} — {s.get('description','')[:70]}")


def cmd_info(catalog, args):
    s = find(catalog, args.skill_id)
    if not s:
        sys.exit(f"error: no skill with id '{args.skill_id}' (try: list)")
    print(json.dumps(s, indent=2, ensure_ascii=False))


def cmd_install(catalog, args):
    s = find(catalog, args.skill_id)
    if not s:
        sys.exit(f"error: no skill with id '{args.skill_id}' (try: list)")

    if s.get("status") == "deprecated":
        succ = s.get("deprecated_by")
        print(f"warning: '{s['id']}' is DEPRECATED"
              + (f" — consider '{succ}' instead." if succ else "."))
    if args.harness not in s.get("harnesses", []):
        print(f"warning: '{s['id']}' is not tagged for harness '{args.harness}' "
              f"(supported: {', '.join(s.get('harnesses', []))}). Installing anyway.")

    dest = Path(args.dest) if args.dest else Path(HARNESS_DEST[args.harness])
    target_dir = dest / s["id"]
    target_dir.mkdir(parents=True, exist_ok=True)

    skill_md = fetch_text(s["download_url"])
    metadata = fetch_text(s["metadata_url"])
    (target_dir / "skill.md").write_text(skill_md, encoding="utf-8")
    (target_dir / "metadata.json").write_text(metadata, encoding="utf-8")

    print(f"OK: installed '{s['id']}' v{s.get('version')} -> {target_dir}")
    print(f"  harness: {args.harness}")
    if args.harness == "claude-code":
        print("  Restart Claude Code (or /reload) to activate the skill.")


def main():
    p = argparse.ArgumentParser(prog="skill", description="Install skills from the Skill Marketplace.")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list available skills")
    p_list.add_argument("--all", action="store_true", help="include draft/deprecated skills")

    p_search = sub.add_parser("search", help="search skills by keyword")
    p_search.add_argument("query")

    p_info = sub.add_parser("info", help="show full catalog entry for a skill")
    p_info.add_argument("skill_id")

    p_inst = sub.add_parser("install", help="download and install a skill")
    p_inst.add_argument("skill_id")
    p_inst.add_argument("--harness", choices=list(HARNESS_DEST), default="claude-code")
    p_inst.add_argument("--dest", help="override destination directory")

    args = p.parse_args()
    catalog = fetch_catalog()
    {
        "list": cmd_list,
        "search": cmd_search,
        "info": cmd_info,
        "install": cmd_install,
    }[args.cmd](catalog, args)


if __name__ == "__main__":
    main()
