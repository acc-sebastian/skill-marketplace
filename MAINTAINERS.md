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
