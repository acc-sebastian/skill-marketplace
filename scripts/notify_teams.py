#!/usr/bin/env python3
"""
Post a Microsoft Teams notification when skills are added/updated (Roadmap
Phase 4). Reads the changed skill IDs from argv; posts a MessageCard to the
TEAMS_WEBHOOK_URL secret. Skips cleanly (exit 0) when the secret is absent.

Usage (in CI):
    python scripts/notify_teams.py <skill-id> [<skill-id> ...]
Env:
    TEAMS_WEBHOOK_URL   Incoming Webhook URL (else skip)
Flags:
    --dry-run           print the payload instead of posting
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "accilium-skills" / "skills"
SITE = "https://acc-sebastian.github.io/skill-marketplace"


def load(skill_id):
    mf = SKILLS_DIR / skill_id / "metadata.json"
    if mf.exists():
        return json.loads(mf.read_text(encoding="utf-8"))
    return {"id": skill_id, "name": skill_id}


def build_card(ids):
    facts = []
    for sid in ids:
        m = load(sid)
        facts.append({"name": m.get("name", sid),
                      "value": f"v{m.get('version', '?')} · {m.get('category', '')} · {m.get('status', '')}"})
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "da3025",
        "summary": "Skill Marketplace updated",
        "sections": [{
            "activityTitle": "🧩 Skill Marketplace updated",
            "activitySubtitle": f"{len(ids)} skill(s) added or updated on main",
            "facts": facts,
            "markdown": True,
        }],
        "potentialAction": [{
            "@type": "OpenUri",
            "name": "Open marketplace",
            "targets": [{"os": "default", "uri": SITE}],
        }],
    }


def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    if not args:
        print("No changed skills passed; nothing to notify.")
        return

    url = os.environ.get("TEAMS_WEBHOOK_URL")
    card = build_card(args)

    if dry or not url:
        if not url and not dry:
            print("SKIP — TEAMS_WEBHOOK_URL not set.")
        print(json.dumps(card, indent=2, ensure_ascii=False))
        return

    req = urllib.request.Request(url, data=json.dumps(card).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"Posted to Teams -> HTTP {r.status}")


if __name__ == "__main__":
    main()
