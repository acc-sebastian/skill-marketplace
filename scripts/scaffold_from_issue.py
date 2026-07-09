#!/usr/bin/env python3
"""
Turn a "Neue Skill vorschlagen" issue-form submission into a scaffolded skill
folder (metadata.json + SKILL.md). Business users never touch Git — this runs
in CI (scaffold-skill.yml) and the result becomes a pull request.

Reads from environment:
    ISSUE_BODY, ISSUE_NUMBER, ISSUE_AUTHOR
Writes:
    skills/<slug>/metadata.json, skills/<slug>/SKILL.md
Emits (to stdout and $GITHUB_OUTPUT): slug, name
"""

import datetime
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "sbo-skills" / "skills"

VALID_HARNESSES = {"claude-code", "copilot-studio", "generic"}
VALID_CATEGORIES = {"Productivity", "Analytics", "Strategy", "Procurement",
                    "Finance", "Compliance", "Communication", "Other"}
VALID_COMPLEXITY = {"beginner", "intermediate", "advanced"}


def parse_form(body):
    """GitHub issue forms render as '### <label>\\n\\n<value>' blocks."""
    sections, current, buf = {}, None, []
    for line in body.splitlines():
        m = re.match(r"^###\s+(.*)", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def get(sections, needle, default=""):
    for label, value in sections.items():
        if needle.lower() in label.lower():
            return "" if value == "_No response_" else value.strip()
    return default


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def main():
    body = os.environ.get("ISSUE_BODY", "")
    issue_no = os.environ.get("ISSUE_NUMBER", "0")
    author = os.environ.get("ISSUE_AUTHOR", "").strip()
    sections = parse_form(body)

    name = get(sections, "Skill-Name")
    description = get(sections, "Was soll die Skill")
    instructions = get(sections, "Anweisungen")
    if not (name and description and instructions):
        sys.exit("error: missing required fields (name, description, instructions). "
                 "Is this really a new-skill form submission?")

    slug = slugify(name)
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", slug):
        sys.exit(f"error: could not derive a valid id from name '{name}'")
    if (SKILLS_DIR / slug).exists():
        sys.exit(f"error: skill '{slug}' already exists")

    category = get(sections, "Kategorie") or "Other"
    if category not in VALID_CATEGORIES:
        category = "Other"

    complexity = (get(sections, "Komplexität") or "beginner").lower()
    if complexity not in VALID_COMPLEXITY:
        complexity = "beginner"

    raw_harnesses = get(sections, "Harnesses")
    harnesses = [h.strip() for h in re.split(r"[,\n]", raw_harnesses) if h.strip() in VALID_HARNESSES]
    harnesses = list(dict.fromkeys(harnesses)) or ["generic"]

    owner_raw = get(sections, "Owner")
    owner = owner_raw.lstrip("@") if re.match(r"^@?[A-Za-z0-9-]+$", owner_raw or "") else author
    owner = owner or author or "unknown"

    example_input = get(sections, "Beispiel-Input")

    triggers = [t.strip() for t in get(sections, "Trigger-Phrasen").splitlines() if t.strip()][:10]

    # tags: category + meaningful slug words, deduped, valid pattern
    tags = [category.lower()] + [w for w in slug.split("-") if len(w) > 2]
    tags = list(dict.fromkeys(t for t in tags if re.match(r"^[a-z0-9]+([-_][a-z0-9]+)*$", t)))[:8] or ["skill"]

    today = datetime.date.today().isoformat()

    meta = {
        "id": slug,
        "name": name[:60],
        "description": description,
        "author": author or owner,
        "owner": owner,
        "version": "1.0.0",
        "created": today,
        "last_reviewed": today,
        "status": "draft",
        "category": category,
        "tags": tags,
        "harnesses": harnesses,
        "complexity": complexity,
        "trigger_phrases": triggers,
        "emoji": "🧩",
        "changelog": [{"version": "1.0.0", "date": today,
                       "change": f"Scaffolded from issue #{issue_no}"}],
    }
    if len(example_input) >= 10:
        meta["example_input"] = example_input

    target = SKILLS_DIR / slug
    target.mkdir(parents=True, exist_ok=True)
    (target / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    trigger_block = "\n".join(f"- {t}" for t in triggers) if triggers else "- [TODO: add trigger phrases]"
    skill_md = f"""---
name: {slug}
description: {description[:300]}
---

## Role
[TODO: one sentence — what expert role does the AI take?]

## Trigger
Activate when the user asks for this. Example phrases:
{trigger_block}

## Input
[TODO: what does the user provide?]

## Process
{instructions}

## Output Format
[TODO: define the exact output structure — tables, headers, etc.]

## Rules
1. [TODO: constraints and edge-case handling]

<!-- Scaffolded from issue #{issue_no}. A maintainer should refine the TODO
     sections and flip status from "draft" to "published" before release. -->
"""
    (target / "SKILL.md").write_text(skill_md, encoding="utf-8")

    print(f"scaffolded plugins/sbo-skills/skills/{slug}/ (name={name!r}, owner={owner}, status=draft)")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"slug={slug}\n")
            f.write(f"name={name}\n")


if __name__ == "__main__":
    main()
