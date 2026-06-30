# Contributing to the Skill Marketplace

Thank you for contributing! Each merged skill becomes immediately available to everyone on the marketplace.

## Quick Start

1. **Fork** this repo
2. **Create** a folder: `skills/<your-skill-name>/` (use kebab-case, e.g. `budget-variance-report`)
3. **Add two files**: `metadata.json` and `skill.md`
4. **Submit a pull request**

That's it. The GitHub Actions workflow auto-rebuilds the site on merge.

---

## File Formats

### `metadata.json`

```json
{
  "id": "your-skill-name",
  "name": "Human Readable Name",
  "description": "One sentence: what does this skill do and when is it useful?",
  "author": "Your Name",
  "version": "1.0.0",
  "created": "YYYY-MM-DD",
  "category": "Productivity",
  "tags": ["tag1", "tag2"],
  "harnesses": ["claude-code", "copilot-studio", "generic"],
  "complexity": "beginner",
  "trigger_phrases": ["trigger phrase 1", "trigger phrase 2"],
  "emoji": "📋"
}
```

**Field reference:**

| Field | Required | Values |
|-------|----------|--------|
| `id` | ✅ | kebab-case, matches folder name |
| `name` | ✅ | Display name (title case) |
| `description` | ✅ | Max 200 chars |
| `author` | ✅ | Your name or GitHub handle |
| `version` | ✅ | semver, start at `1.0.0` |
| `created` | ✅ | ISO date `YYYY-MM-DD` |
| `category` | ✅ | See categories below |
| `tags` | ✅ | Array, 2-5 lowercase tags |
| `harnesses` | ✅ | `claude-code`, `copilot-studio`, `generic` |
| `complexity` | ✅ | `beginner`, `intermediate`, `advanced` |
| `trigger_phrases` | ✅ | 2-5 example phrases that activate the skill |
| `emoji` | optional | Single emoji for the skill card |

**Available categories:**
- `Productivity` — Meeting tools, reminders, scheduling
- `Analytics` — Data analysis, KPIs, reporting
- `Procurement` — Vendor evaluation, RFQs, contracts
- `Strategy` — Competitive intelligence, market analysis
- `Finance` — Budgeting, reconciliation, expense management
- `Compliance` — Audit, policy checks, risk assessment
- `Communication` — Emails, reports, stakeholder updates

### `skill.md`

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

- [ ] `metadata.json` validates as valid JSON
- [ ] All required fields in `metadata.json` are present
- [ ] Folder name matches `metadata.json` `id` field
- [ ] `skill.md` has valid YAML frontmatter
- [ ] `skill.md` body includes Role, Trigger, Input, Process, Output, and Rules sections
- [ ] Skill was manually tested in at least one harness
- [ ] No sensitive data or PII in files
- [ ] Description is under 200 characters

---

## Questions?

Open an issue in this repository.
