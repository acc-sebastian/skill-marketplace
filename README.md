# Skill Marketplace

A curated library of AI skills (prompts + instructions) that plug into any LLM harness — Claude Code, Copilot Studio, or any chat-based AI. Browse and install from the **[live marketplace site](https://acc-sebastian.github.io/skill-marketplace/)**.

The site has two views: the **Skill Marketplace** (installable skills) and the **[Prompt Library](https://acc-sebastian.github.io/skill-marketplace/#prompts)** (copy-paste prompt templates) — see [Prompt Library](#prompt-library) below.

> 📍 See the **[Roadmap](ROADMAP.md)** for the 5-phase plan from PoC to a fully governed, automated marketplace.

## What is a "skill"?

A skill is a structured prompt file that turns your AI assistant into a specialist. Each skill includes:
- **Trigger conditions** — when the skill activates
- **Step-by-step instructions** — exactly how the AI should behave
- **Output templates** — consistent, professional results every time

## Available Skills

| Skill | Category | Description |
|-------|----------|-------------|
| [MOM Generator](plugins/accilium-skills/skills/mom-generator/) | Productivity | Transform meeting notes into structured minutes |
| [Action Item Tracker](plugins/accilium-skills/skills/action-item-tracker/) | Productivity | Manage, track, and send reminders for action items |
| [KPI Anomaly Check](plugins/accilium-skills/skills/kpi-anomaly-check/) | Analytics | Validate KPI data and flag threshold breaches |
| [Vendor Proposal Comparison](plugins/accilium-skills/skills/vendor-proposal-comparison/) | Procurement | Score and rank vendor proposals systematically |
| [Competitor Analysis](plugins/accilium-skills/skills/competitor-analysis/) | Strategy | Structured competitive intelligence reports |

## How to Install a Skill

### Claude Code plugin (recommended — get *all* skills, auto-updated)
Add the marketplace once and install the bundled `accilium-skills` plugin:
```
/plugin marketplace add acc-sebastian/skill-marketplace
/plugin install accilium-skills@accilium-skill-marketplace
```
You now have every published skill, and new ones arrive automatically on update.
**Organizations** can push this to all users automatically (zero user action) via
managed settings — see the **[Distribution Setup Guide](docs/enterprise-setup.md)**.

### CLI (single skills, any harness)
The `skill` CLI reads the live [catalog](https://acc-sebastian.github.io/skill-marketplace/catalog.json),
so it always sees the latest published skills. No dependencies beyond the Python standard library.
```bash
python scripts/skill_cli.py list
python scripts/skill_cli.py search kpi
python scripts/skill_cli.py install mom-generator                 # -> .claude/skills/
python scripts/skill_cli.py install mom-generator --harness generic --dest ./skills
```

### Claude Code (manual)
Copy the `SKILL.md` file into your `.claude/skills/` directory:
```bash
cp plugins/accilium-skills/skills/mom-generator/SKILL.md ~/.claude/skills/
# or into your project
cp plugins/accilium-skills/skills/mom-generator/SKILL.md .claude/skills/
```

You can also download a versioned package (`SKILL.md` + `metadata.json`) from the
[Releases](https://github.com/acc-sebastian/skill-marketplace/releases) page (tag `id@version`).

### Copilot Studio
1. Open the `SKILL.md` file for the skill you want
2. Copy the content after the frontmatter (below the `---` separator)
3. Paste it as a **System Prompt** in your Copilot Studio Topic, or as a **Generative AI plugin description**

### Any LLM / Chat Interface
1. Open the `SKILL.md` file
2. Copy the body (after the frontmatter) and paste it as a system prompt or first message
3. The AI will follow the structured instructions

## Prompt Library

Where skills are *installed* into a harness, prompts are *copy-paste templates* with
`{{PLACEHOLDER}}` variables for ad-hoc use in any AI chat — no installation, same governance
(schema, versioning, owner, lifecycle status, CI validation).

| Prompt | Category | Description |
|--------|----------|-------------|
| [Executive Summary Generator](prompts/executive-summary-generator/) | Communication | One-page C-level summary of any long document |
| [RFP Requirements Extractor](prompts/rfp-requirements-extractor/) | Procurement | Structured requirements table from an RFP/tender |
| [Stakeholder Update Drafter](prompts/stakeholder-update-drafter/) | Communication | Status emails with the right tone, including bad news |
| [Risk Register Builder](prompts/risk-register-builder/) | Compliance | Formal risk register from unstructured project notes |
| [KPI Management Commentary](prompts/kpi-management-commentary/) | Analytics | Board-ready commentary from a raw KPI table |

**Using a prompt:** open it in the [Prompt Library](https://acc-sebastian.github.io/skill-marketplace/#prompts),
fill in the variables in the form, and copy the finished prompt. Machine consumers can read the
[prompt catalog](https://acc-sebastian.github.io/skill-marketplace/prompt-catalog.json).

**Adding a prompt:** create `prompts/<id>/metadata.json` + `PROMPT.md` (validated against
[`schema/prompt.schema.json`](schema/prompt.schema.json) in CI — declared variables and
`{{PLACEHOLDERS}}` in the template must match).

## How to Add a Skill

1. Fork this repository
2. Create a new directory under `plugins/accilium-skills/skills/` with your skill's kebab-case name
3. Add `metadata.json` and `SKILL.md` (copy an existing skill as template)
4. Submit a pull request
5. Once merged, the skill automatically appears on the marketplace website within minutes

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and file format spec.

## Repository Structure

```
skill_marketplace/
├── .claude-plugin/
│   └── marketplace.json     # Claude Code plugin marketplace manifest
├── plugins/
│   └── accilium-skills/          # The Claude Code plugin (all skills)
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/          # Skill source files
│           └── <skill-name>/
│               ├── metadata.json    # Name, description, tags, category
│               └── SKILL.md         # The actual skill instructions
├── prompts/                 # Prompt Library source files
│   └── <prompt-name>/
│       ├── metadata.json
│       └── PROMPT.md
├── scripts/
│   └── build_site.py        # Generates docs/ from skills + prompts
├── docs/                    # GitHub Pages output (auto-generated)
│   └── index.html
├── .github/
│   └── workflows/
│       └── build-site.yml   # Auto-deploy on push
└── CONTRIBUTING.md
```

## Local Development

```bash
# Build the site locally
python scripts/build_site.py

# Open docs/index.html in your browser
```

Requires Python 3.9+ and no external dependencies.
