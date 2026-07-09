#!/usr/bin/env python3
"""
Validate every skill against schema/skill.schema.json plus structural rules.

Usage:
    python scripts/validate_skills.py

Exit code 0 = all valid, 1 = at least one violation (CI-friendly).
"""

import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(2)

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "sbo-skills" / "skills"
SCHEMA_FILE = ROOT / "schema" / "skill.schema.json"


def main():
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    errors = []
    seen_ids = {}
    all_ids = set()

    skill_dirs = [d for d in sorted(SKILLS_DIR.iterdir()) if d.is_dir()]

    # First pass: collect all IDs (needed for deprecated_by reference check)
    for d in skill_dirs:
        mf = d / "metadata.json"
        if mf.exists():
            try:
                all_ids.add(json.loads(mf.read_text(encoding="utf-8")).get("id", ""))
            except json.JSONDecodeError:
                pass

    for d in skill_dirs:
        label = d.name
        mf = d / "metadata.json"
        sf = d / "SKILL.md"

        if not mf.exists():
            errors.append(f"{label}: missing metadata.json")
            continue

        try:
            meta = json.loads(mf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{label}: metadata.json is not valid JSON ({e})")
            continue

        # Schema validation
        for err in validator.iter_errors(meta):
            path = ".".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{label}: schema violation at {path}: {err.message}")

        # Folder name must equal id
        sid = meta.get("id")
        if sid and sid != d.name:
            errors.append(f"{label}: folder name != id ('{sid}')")

        # Unique IDs
        if sid:
            if sid in seen_ids:
                errors.append(f"{label}: duplicate id '{sid}' (also in {seen_ids[sid]})")
            seen_ids[sid] = d.name

        # deprecated_by must reference an existing skill
        dep = meta.get("deprecated_by")
        if dep and dep not in all_ids:
            errors.append(f"{label}: deprecated_by '{dep}' does not reference an existing skill id")

        # SKILL.md checks
        if not sf.exists():
            errors.append(f"{label}: missing SKILL.md")
        else:
            content = sf.read_text(encoding="utf-8")
            if not re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL):
                errors.append(f"{label}: SKILL.md missing YAML frontmatter (--- block at top)")
            if len(content.strip()) < 200:
                errors.append(f"{label}: SKILL.md suspiciously short (<200 chars)")

            # Broken-link check: relative markdown links must resolve on disk;
            # URLs must be well-formed http(s). (No network calls — CI-stable.)
            for text, target in re.findall(r"\[([^\]]*)\]\(([^)\s]+)\)", content):
                if target.startswith(("#", "mailto:")):
                    continue
                if target.startswith(("http://", "https://")):
                    if not re.match(r"^https?://[\w.-]+(:\d+)?(/\S*)?$", target):
                        errors.append(f"{label}: malformed URL in SKILL.md: {target}")
                else:
                    rel = (d / target).resolve()
                    if not rel.exists():
                        errors.append(f"{label}: broken relative link in SKILL.md: {target}")

    n = len(skill_dirs)
    if errors:
        print(f"FAIL — {len(errors)} problem(s) across {n} skill(s):\n")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    print(f"OK — all {n} skills valid against {SCHEMA_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
