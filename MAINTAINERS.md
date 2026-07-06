# Maintainers & Governance

## Roles

| Role | Who | Responsibility |
|------|-----|----------------|
| **Repo Maintainer** | @acc-sebastian | Merge rights, branch protection, release management, CI health |
| **Taxonomy Owner** | @acc-sebastian | Owns the category & tag structure — approves new categories, consolidates tags, prevents taxonomy sprawl |
| **Skill Owner** | see `owner` field in each skill's `metadata.json` | Keeps "their" skill accurate and up to date, responds to review-due issues and bug reports |

## Ground rules

1. **Every skill has exactly one owner.** The `owner` field in `metadata.json`
   and the corresponding line in `.github/CODEOWNERS` must stay in sync.
2. **New categories require Taxonomy Owner approval.** The allowed category
   list lives in `schema/skill.schema.json` (`category` enum) — extending it is
   a deliberate schema change, not a drive-by edit.
3. **Owners respond to review-due flags.** When stale-detection (Phase 4)
   opens a "Review fällig" issue, the owner either re-validates the skill
   (bump `last_reviewed`) or deprecates it.
4. **Nobody merges their own skill unreviewed.** Branch protection requires
   at least one CODEOWNER approval.

## Lifecycle at a glance

```
Draft → In Review → Published → (Maintained) → Deprecated → Archived
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full lifecycle definition and
[ROADMAP.md](ROADMAP.md) for when each automation lands.

## Governance at scale (Roadmap Phase 5)

As the catalog grows, the Taxonomy Owner runs a lightweight recurring review so
structure and quality don't drift:

- **Category owners.** Each category has a reviewer who vets new skills in it
  for quality and correct categorization. Until a category has enough volume to
  warrant a dedicated owner, the Taxonomy Owner covers it.

  | Category | Owner |
  |----------|-------|
  | Productivity · Analytics · Strategy · Procurement · Finance · Compliance · Communication · Other | @acc-sebastian *(interim — split out as volume grows)* |

- **Quarterly taxonomy review.** The Taxonomy Owner: consolidates near-duplicate
  tags, checks each category still earns its place (merge/retire thin ones), and
  confirms every published skill is in the right category. New categories are
  added only here, as a deliberate `schema/skill.schema.json` enum change.
- **Data-driven prioritization.** The monthly [insights report](.github/workflows/insights.yml)
  (and the live **Insights** panel on the site) rank skills by popularity ×
  open bugs × review age. Maintainers work the top of that list first.
- **Quality signals.** A skill with repeated bug reports, or high downloads but a
  stale `last_reviewed`, is a priority for review or ownership reassignment.
