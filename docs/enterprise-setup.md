# Claude Code Distribution — Setup Guide

How to get the accilium Skill Marketplace into Claude Code so that **every user always
has all current skills, automatically**.

The repo is a **Claude Code plugin marketplace**: `.claude-plugin/marketplace.json`
declares one plugin, `accilium-skills`, that bundles **all published skills**. Because it's
one plugin, any newly merged skill flows to users on the next update — nobody has to
enable skills one by one.

> **Why always up to date?** The plugin pins to the repository's commit SHA (no fixed
> `version` in the manifest). Every merge to `main` is a new SHA, so with auto-update
> on, Claude Code pulls the latest skills at startup and on its hourly check.

---

## Option A — Org-wide, fully automatic (Claude for Teams / Enterprise)

**Best for rolling out to everyone.** No end-user action required.

1. Open **claude.ai → Admin settings → Claude Code → Managed settings**.
2. Paste this configuration (merge with any existing managed settings):

```json
{
  "extraKnownMarketplaces": {
    "accilium-skill-marketplace": {
      "source": { "source": "github", "repo": "acc-sebastian/skill-marketplace" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "accilium-skills@accilium-skill-marketplace": true
  }
}
```

3. Save. On each user's next Claude Code start (settings are fetched on auth and
   refreshed hourly), the marketplace is registered and the `accilium-skills` plugin is
   enabled automatically. All skills become available to the model with no further
   steps.

**Optional hardening:**
- `"pluginSuggestionMarketplaces": ["accilium-skill-marketplace"]` — let Claude Code suggest these skills.
- `"strictKnownMarketplaces": true` — restrict users to approved marketplaces only.

**Requirements:** Claude for Teams (client v2.1.38+) or Enterprise (v2.1.30+).
Managed settings are **not** available when using Amazon Bedrock, Google Vertex,
Azure Foundry, or a custom `ANTHROPIC_BASE_URL`.

---

## Option B — Individual setup (Pro / single accounts)

For users without managed settings — a one-time setup directly in the Claude chat
window. Auto-update still applies afterward.

1. Click **+** → **Plugins** → **Manage Plugins**.
2. Click **Add** → **Add Marketplace**.
3. Enter `acc-sebastian/skill-marketplace` (or the full GitHub URL) and click **Sync**.
4. All published skills are now available directly in the chat window.

That's it. New skills arrive automatically on later updates. To force a refresh,
open **Manage Plugins** and click **Sync** again on the marketplace entry.

---

## What gets distributed

- Only skills that live in `plugins/accilium-skills/skills/` on `main` are shipped.
- **Operating rule:** keep only `published` skills on `main`. Drafts live on PR
  branches until published; `archived` skills are moved out of the skills folder
  (Roadmap Phase 4 auto-archive), so they leave the plugin as well.
- Every skill is a folder `plugins/accilium-skills/skills/<id>/` containing `SKILL.md`
  (the instructions Claude Code loads) and `metadata.json`.

## How a new skill reaches everyone

```
Author/propose skill  →  PR  →  validate gate (green)  →  merge to main
   →  new commit SHA on main
   →  Claude Code auto-update (startup + hourly)  →  every user has the new skill
```

No manual distribution step. The marketplace repo is the single source of truth.
