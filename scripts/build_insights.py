#!/usr/bin/env python3
"""
Maintenance-priority report (Roadmap Phase 5).

Pulls per-skill release download counts and open feedback/bug issues from the
GitHub API, combines them with review age into a priority score, and prints a
ranked report. Run on a schedule (insights.yml) so maintainers get a monthly
"what to look at first" list in the Actions log — no commit to main, so it
doesn't fight branch protection.

Auth: uses GH_TOKEN if present (higher rate limit); works unauthenticated too.
Reads skills from the local checkout for names/last_reviewed.
"""

import datetime
import json
import os
import re
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "sbo-skills" / "skills"
REPO = "acc-sebastian/skill-marketplace"
TITLE_RE = re.compile(r"\[(?:Feedback|Bug)\]\s+([a-z0-9-]+)", re.I)


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "insights"},
    )
    tok = os.environ.get("GH_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  (API {path} -> HTTP {e.code})")
        return []


def months_since(iso, today):
    if not iso:
        return 0
    d = datetime.date.fromisoformat(iso)
    return max(0, (today.year - d.year) * 12 + (today.month - d.month))


def main():
    today = datetime.date.today()
    downloads, feedback, bugs = {}, {}, {}

    for rel in api(f"/repos/{REPO}/releases?per_page=100") or []:
        sid = (rel.get("tag_name") or "").split("@")[0]
        dl = sum(a.get("download_count", 0) for a in rel.get("assets", []))
        downloads[sid] = downloads.get(sid, 0) + dl

    for i in api(f"/repos/{REPO}/issues?state=all&per_page=100") or []:
        if i.get("pull_request"):
            continue
        m = TITLE_RE.match(i.get("title", "").strip())
        if not m:
            continue
        sid = m.group(1)
        names = [l["name"] for l in i.get("labels", [])]
        if "bug" in names:
            bugs[sid] = bugs.get(sid, 0) + 1
        elif "feedback" in names:
            feedback[sid] = feedback.get(sid, 0) + 1

    rows = []
    for d in sorted(SKILLS_DIR.iterdir()):
        mf = d / "metadata.json"
        if not mf.exists():
            continue
        meta = json.loads(mf.read_text(encoding="utf-8"))
        sid = meta["id"]
        dl, fb, bg = downloads.get(sid, 0), feedback.get(sid, 0), bugs.get(sid, 0)
        age = months_since(meta.get("last_reviewed"), today)
        score = dl * 1 + bg * 40 + age * 8 + fb * 3
        rows.append((score, sid, dl, fb, bg, age))

    rows.sort(reverse=True)
    print(f"\nMaintenance priority report — {today.isoformat()}")
    print(f"{'rank':<5}{'skill':<30}{'dl':>6}{'fb':>5}{'bug':>5}{'age':>5}{'score':>8}")
    for rank, (score, sid, dl, fb, bg, age) in enumerate(rows, 1):
        print(f"{rank:<5}{sid:<30}{dl:>6}{fb:>5}{bg:>5}{age:>5}{score:>8}")
    print(f"\nTotal downloads: {sum(r[2] for r in rows)}")


if __name__ == "__main__":
    main()
