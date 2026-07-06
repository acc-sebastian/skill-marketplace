# Skill Marketplace

A curated library of AI skills (prompts + instructions) that plug into any LLM harness — Claude Code, Copilot Studio, or any chat-based AI. Browse and install from the **[live marketplace site](https://acc-sebastian.github.io/skill-marketplace/)**.

> 📍 See the **[Roadmap](ROADMAP.md)** for the 5-phase plan from PoC to a fully governed, automated marketplace.

## What is a "skill"?

A skill is a structured prompt file that turns your AI assistant into a specialist. Each skill includes:
- **Trigger conditions** — when the skill activates
- **Step-by-step instructions** — exactly how the AI should behave
- **Output templates** — consistent, professional results every time

## Available Skills

| Skill | Category | Description |
|-------|----------|-------------|
| [MOM Generator](skills/mom-generator/) | Productivity | Transform meeting notes into structured minutes |
| [Action Item Tracker](skills/action-item-tracker/) | Productivity | Manage, track, and send reminders for action items |
| [KPI Anomaly Check](skills/kpi-anomaly-check/) | Analytics | Validate KPI data and flag threshold breaches |
| [Vendor Proposal Comparison](skills/vendor-proposal-comparison/) | Procurement | Score and rank vendor proposals systematically |
| [Competitor Analysis](skills/competitor-analysis/) | Strategy | Structured competitive intelligence reports |

## How to Install a Skill

### CLI (recommended)
The `skill` CLI reads the live [catalog](https://acc-sebastian.github.io/skill-marketplace/catalog.json),
so it always sees the latest published skills. No dependencies beyond the Python standard library.
```bash
python scripts/skill_cli.py list
python scripts/skill_cli.py search kpi
python scripts/skill_cli.py install mom-generator                 # -> .claude/skills/
python scripts/skill_cli.py install mom-generator --harness generic --dest ./skills
```

### Claude Code (manual)
Copy the `skill.md` file into your `.claude/skills/` directory:
```bash
cp skills/mom-generator/skill.md ~/.claude/skills/
# or into your project
cp skills/mom-generator/skill.md .claude/skills/
```

You can also download a versioned package (`skill.md` + `metadata.json`) from the
[Releases](https://github.com/acc-sebastian/skill-marketplace/releases) page (tag `id@version`).

### Copilot Studio
1. Open the `skill.md` file for the skill you want
2. Copy the content after the frontmatter (below the `---` separator)
3. Paste it as a **System Prompt** in your Copilot Studio Topic, or as a **Generative AI plugin description**

### Any LLM / Chat Interface
1. Open the `skill.md` file
2. Copy the body (after the frontmatter) and paste it as a system prompt or first message
3. The AI will follow the structured instructions

## How to Add a Skill

1. Fork this repository
2. Create a new directory under `skills/` with your skill's kebab-case name
3. Add `metadata.json` and `skill.md` (copy an existing skill as template)
4. Submit a pull request
5. Once merged, the skill automatically appears on the marketplace website within minutes

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and file format spec.

## Repository Structure

```
skill_marketplace/
├── skills/                  # Skill source files
│   └── <skill-name>/
│       ├── metadata.json    # Name, description, tags, category
│       └── skill.md         # The actual skill instructions
├── scripts/
│   └── build_site.py        # Generates docs/ from skills/
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
