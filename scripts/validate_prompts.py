#!/usr/bin/env python3
"""
Validate every prompt against schema/prompt.schema.json plus structural rules.

Beyond the schema, this enforces the prompt-specific quality gate:
every variable declared in metadata.json must appear as {{NAME}} in
PROMPT.md, and every {{NAME}} placeholder in PROMPT.md must be declared.

Usage:
    python scripts/validate_prompts.py

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
PROMPTS_DIR = ROOT / "prompts"
SCHEMA_FILE = ROOT / "schema" / "prompt.schema.json"

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def main():
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    errors = []
    seen_ids = {}
    all_ids = set()

    if not PROMPTS_DIR.exists():
        print("OK — no prompts/ directory yet, nothing to validate")
        return

    prompt_dirs = [d for d in sorted(PROMPTS_DIR.iterdir()) if d.is_dir()]

    # First pass: collect all IDs (needed for deprecated_by reference check)
    for d in prompt_dirs:
        mf = d / "metadata.json"
        if mf.exists():
            try:
                all_ids.add(json.loads(mf.read_text(encoding="utf-8")).get("id", ""))
            except json.JSONDecodeError:
                pass

    for d in prompt_dirs:
        label = d.name
        mf = d / "metadata.json"
        pf = d / "PROMPT.md"

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
        pid = meta.get("id")
        if pid and pid != d.name:
            errors.append(f"{label}: folder name != id ('{pid}')")

        # Unique IDs
        if pid:
            if pid in seen_ids:
                errors.append(f"{label}: duplicate id '{pid}' (also in {seen_ids[pid]})")
            seen_ids[pid] = d.name

        # deprecated_by must reference an existing prompt
        dep = meta.get("deprecated_by")
        if dep and dep not in all_ids:
            errors.append(f"{label}: deprecated_by '{dep}' does not reference an existing prompt id")

        # PROMPT.md checks
        if not pf.exists():
            errors.append(f"{label}: missing PROMPT.md")
        else:
            content = pf.read_text(encoding="utf-8")
            if not re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL):
                errors.append(f"{label}: PROMPT.md missing YAML frontmatter (--- block at top)")
            if len(content.strip()) < 200:
                errors.append(f"{label}: PROMPT.md suspiciously short (<200 chars)")

            # Variable consistency: declared <-> used
            declared = {v["name"] for v in meta.get("variables", []) if isinstance(v, dict) and "name" in v}
            used = set(PLACEHOLDER_RE.findall(content))
            for name in sorted(declared - used):
                errors.append(f"{label}: variable '{name}' declared in metadata.json but never used as {{{{{name}}}}} in PROMPT.md")
            for name in sorted(used - declared):
                errors.append(f"{label}: placeholder {{{{{name}}}}} used in PROMPT.md but not declared in metadata.json variables")

    n = len(prompt_dirs)
    if errors:
        print(f"FAIL — {len(errors)} problem(s) across {n} prompt(s):\n")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    print(f"OK — all {n} prompts valid against {SCHEMA_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
