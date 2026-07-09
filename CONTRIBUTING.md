# Contributing to the Skill Marketplace

Thank you for contributing! Each merged skill becomes immediately available to everyone on the marketplace.

## Two ways to contribute

### 🅰 No Git required — propose via web form
Fill out the **["Neue Skill vorschlagen" form](https://github.com/acc-sebastian/skill-marketplace/issues/new?template=new-skill.yml)**
(also linked from the website). A maintainer turns your proposal into a skill.
You never touch Git.

### 🅱 Via pull request (for Git users)

1. **Fork** this repo
2. **Create** a folder: `plugins/sbo-skills/skills/<your-skill-name>/` (use kebab-case, e.g. `budget-variance-report`)
3. **Add two files**: `metadata.json` and `SKILL.md`
4. **Validate locally**: `python scripts/validate_skills.py`
5. **Submit a pull request** — the PR template walks you through the checklist

The GitHub Actions workflow auto-rebuilds the site (and `docs/catalog.json`) on merge.

---

## Skill Lifecycle

Every skill carries a `status` field and moves through defined phases:

```
Draft → In Review → Published → (Maintained) → Deprecated → Archived
```

| Status | Meaning | Who sets it |
|--------|---------|-------------|
| `draft` | Work in progress, not ready for use | Contributor |
| `in-review` | PR open, under CODEOWNER review | Contributor/Maintainer |
| `published` | Live on the marketplace | Maintainer (at merge) |
| `deprecated` | Still visible, but superseded — `deprecated_by` + `sunset_date` required | Skill owner |
| `archived` | Retired; hidden from site & catalog, kept in repo for provenance | Maintainer/automation |

**Maintenance:** every skill has an `owner` who keeps it up to date. The
`last_reviewed` date drives automatic stale-detection — if a skill hasn't been
reviewed for too long, the owner gets a review-due issue (Roadmap Phase 4).

**Versioning:** SemVer. A breaking change to the prompt's behavior or output
format bumps MAJOR; additive improvements bump MINOR; typo fixes bump PATCH.
Every version gets a `changelog` entry.

---

## File Formats

### `metadata.json`

The authoritative definition is **[`schema/skill.schema.json`](schema/skill.schema.json)** —
CI validates every PR against it (Roadmap Phase 2).

```json
{
  "id": "your-skill-name",
  "name": "Human Readable Name",
  "description": "What does this skill do and when is it useful? (30-400 chars)",
  "author": "Your Name",
  "owner": "your-github-handle",
  "version": "1.0.0",
  "created": "YYYY-MM-DD",
  "last_reviewed": "YYYY-MM-DD",
  "status": "draft",
  "category": "Productivity",
  "tags": ["tag1", "tag2"],
  "harnesses": ["claude-code", "copilot-studio", "generic"],
  "complexity": "beginner",
  "trigger_phrases": ["trigger phrase 1", "trigger phrase 2"],
  "emoji": "📋",
  "changelog": [
    { "version": "1.0.0", "date": "YYYY-MM-DD", "change": "Initial release" }
  ],
  "example_input": "A realistic example input for automated smoke-testing."
}
```

**Field reference:**

| Field | Required | Values |
|-------|----------|--------|
| `id` | ✅ | kebab-case, matches folder name |
| `name` | ✅ | Display name, 3–60 chars |
| `description` | ✅ | 30–400 chars |
| `author` | ✅ | Original author (person or org) |
| `owner` | ✅ | GitHub handle responsible for upkeep (synced with CODEOWNERS) |
| `version` | ✅ | SemVer, start at `1.0.0` |
| `created` | ✅ | ISO date `YYYY-MM-DD` |
| `last_reviewed` | ✅ | ISO date — update whenever you re-verify the skill |
| `status` | ✅ | `draft`, `in-review`, `published`, `deprecated`, `archived` |
| `category` | ✅ | See categories below (enum in schema; new ones need taxonomy-owner approval) |
| `tags` | ✅ | Array, 1–8 lowercase tags |
| `harnesses` | ✅ | `claude-code`, `copilot-studio`, `generic` |
| `complexity` | ✅ | `beginner`, `intermediate`, `advanced` |
| `changelog` | ✅ | One entry per version, newest first |
| `trigger_phrases` | optional | Up to 10 example phrases that activate the skill |
| `emoji` | optional | Single emoji for the skill card |
| `example_input` | recommended | Realistic input for automated smoke-tests (Phase 4) |
| `deprecated_by` | if deprecated | ID of the successor skill |
| `sunset_date` | if deprecated | Planned retirement date |

**Available categories:**
- `Productivity` — Meeting tools, reminders, scheduling
- `Analytics` — Data analysis, KPIs, reporting
- `Procurement` — Vendor evaluation, RFQs, contracts
- `Strategy` — Competitive intelligence, market analysis
- `Finance` — Budgeting, reconciliation, expense management
- `Compliance` — Audit, policy checks, risk assessment
- `Communication` — Emails, reports, stakeholder updates

### `SKILL.md`

```markdown
---
name: your-skill-name
description: Trigger description — when should this skill activate? Write this so the AI can decide when to invoke the skill.
---

## Role
[One sentence: what expert role does the AI take?]

## Trigger
[Explain what user inputs or phrases should activate this skill.]

## Input
[What does the user provide? List all possible inputs.]

## Process
[Step-by-step instructions for the AI. Be explicit and unambiguous.]

## Output Format
[Exact output structure — use markdown tables, headers, etc. as templates.]

## Rules
[Numbered list of constraints and edge case handling.]
```

---

## Quality Standards

A good skill:
- **Is specific** — solves one well-defined problem, not "be a general assistant"
- **Has clear triggers** — the AI (and user) can tell when to use it
- **Produces consistent output** — includes a concrete output template
- **Handles edge cases** — tells the AI what to do when input is incomplete
- **Is harness-agnostic** — works in Claude Code, Copilot Studio, or any LLM chat

---

## Review Checklist

Before submitting a PR, confirm:

- [ ] `python scripts/validate_skills.py` passes (schema + structural checks)
- [ ] Folder name matches `metadata.json` `id` field
- [ ] `owner` is set and added to `.github/CODEOWNERS`
- [ ] `SKILL.md` has valid YAML frontmatter
- [ ] `SKILL.md` body includes Role, Trigger, Input, Process, Output, and Rules sections
- [ ] Skill was manually tested in at least one harness
- [ ] No sensitive data or PII in files

---

## Questions?

Open an issue in this repository.
