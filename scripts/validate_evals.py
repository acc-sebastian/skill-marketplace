#!/usr/bin/env python3
"""
Validate every skill's optional evals.json against schema/eval.schema.json
plus structural rules.

evals.json is OPTIONAL — a skill without one is fine (it just won't get an
"evaluated" badge). This validator only checks the files that exist, so it can
run in every PR (no API key needed — that's run_evals.py's job).

Rules beyond the schema:
  - skill_name must equal the folder name (and therefore the skill id)
  - eval ids must be unique within the file

Usage:
    python scripts/validate_evals.py

Exit code 0 = all valid (or none present), 1 = at least one violation.
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(2)

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "accilium-skills" / "skills"
SCHEMA_FILE = ROOT / "schema" / "eval.schema.json"


def find_evals_file(skill_dir):
    """Evals may live at <skill>/evals/evals.json (subfolder, keeps the skill
    root clean and lets fixtures sit alongside) or <skill>/evals.json."""
    for cand in (skill_dir / "evals" / "evals.json", skill_dir / "evals.json"):
        if cand.exists():
            return cand
    return None


def main():
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    errors = []
    checked = 0

    if not SKILLS_DIR.exists():
        print("OK — no skills directory, nothing to validate")
        return

    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        ef = find_evals_file(d)
        if not ef:
            continue  # evals are optional

        checked += 1
        label = d.name
        try:
            data = json.loads(ef.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{label}: evals.json is not valid JSON ({e})")
            continue

        for err in validator.iter_errors(data):
            path = ".".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{label}: schema violation at {path}: {err.message}")

        # skill_name must match the folder name
        sn = data.get("skill_name")
        if sn and sn != d.name:
            errors.append(f"{label}: skill_name '{sn}' != folder name '{d.name}'")

        # unique eval ids
        seen = set()
        for ev in data.get("evals", []):
            if not isinstance(ev, dict):
                continue
            eid = ev.get("id")
            if eid in seen:
                errors.append(f"{label}: duplicate eval id '{eid}'")
            seen.add(eid)

    if errors:
        print(f"FAIL — {len(errors)} problem(s) across {checked} evals file(s):\n")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    print(f"OK — {checked} evals file(s) valid against {SCHEMA_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
