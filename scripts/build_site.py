#!/usr/bin/env python3
"""
Build the Skill Marketplace static site + machine-readable catalog.

Reads:  skills/*/metadata.json + skills/*/SKILL.md
Writes: docs/index.html   (website)
        docs/catalog.json (machine-readable manifest for other harnesses/CLIs)

Run locally:
    python scripts/build_site.py
"""

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
DOCS_DIR = ROOT / "docs"

REPO = "acc-sebastian/skill-marketplace"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/skills"
SITE_URL = "https://acc-sebastian.github.io/skill-marketplace"
PROPOSE_URL = f"https://github.com/{REPO}/issues/new?template=new-skill.yml"


def load_skills():
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        meta_file = skill_dir / "metadata.json"
        skill_file = skill_dir / "SKILL.md"
        if not meta_file.exists():
            print(f"  SKIP {skill_dir.name} — no metadata.json")
            continue
        with open(meta_file, encoding="utf-8") as f:
            meta = json.load(f)
        skill_content = ""
        if skill_file.exists():
            with open(skill_file, encoding="utf-8") as f:
                skill_content = f.read()
        meta["skill_content"] = skill_content
        meta["folder"] = skill_dir.name
        skills.append(meta)
        print(f"  OK  {meta.get('name', skill_dir.name)}")
    return skills


def escape_js(s):
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")


def build_catalog(skills):
    """Machine-readable manifest so other harnesses can always query the
    latest state of all skills (no HTML parsing needed)."""
    entries = []
    for s in skills:
        entries.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "description": s.get("description"),
            "version": s.get("version"),
            "status": s.get("status", "published"),
            "category": s.get("category"),
            "tags": s.get("tags", []),
            "harnesses": s.get("harnesses", []),
            "complexity": s.get("complexity"),
            "owner": s.get("owner"),
            "author": s.get("author"),
            "last_reviewed": s.get("last_reviewed"),
            "deprecated_by": s.get("deprecated_by"),
            "sunset_date": s.get("sunset_date"),
            "emoji": s.get("emoji"),
            "download_url": f"{RAW_BASE}/{s['folder']}/SKILL.md",
            "metadata_url": f"{RAW_BASE}/{s['folder']}/metadata.json",
        })
    return {
        "$schema_note": "Catalog manifest of the Skill Marketplace. One entry per non-archived skill.",
        "catalog_version": 1,
        "site": SITE_URL,
        "repository": f"https://github.com/{REPO}",
        "skill_schema": f"{SITE_URL}/schema/skill.schema.json",
        "count": len(entries),
        "skills": entries,
    }


def build_html(skills):
    skills_json = json.dumps(skills, ensure_ascii=False, indent=2)

    categories = sorted(set(s.get("category", "Other") for s in skills))
    cat_buttons = "\n".join(
        f'<button class="filter-btn" data-filter="{c}">{c}</button>'
        for c in categories
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill Marketplace — accilium</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap">
<style>
  /* Palette adapted from sbo.at — Schoeller-Bleckmann Oilfield Equipment AG */
  :root {{
    --brand-dark: #111145;     /* SBO deep navy/indigo */
    --brand-blue: #da3025;     /* SBO signature red — primary action color */
    --brand-accent: #da3025;   /* SBO red accent */
    --brand-accent-2: #b3241b; /* darker red for gradients */
    --brand-light: #f8f3e5;    /* warm cream */
    --petrol: #36494d;         /* SBO azure-petrol */
    --mid-blue: #253e5c;       /* SBO middle-blue */
    --sand: #d6ceb9;           /* SBO warm sand */
    --bg: #f6f2ea;             /* warm paper background */
    --surface: #ffffff;
    --border: #e6ddcb;         /* warm border */
    --text: #1b1b1b;           /* SBO near-black */
    --text-muted: #6a6c6e;     /* SBO soft grey */
    --radius: 6px;             /* crisp corners for chips/inputs */
    --radius-lg: 14px;         /* modern cards/panels */
    --shadow: 0 1px 2px rgba(17,17,69,0.04), 0 4px 16px rgba(17,17,69,0.06);
    --shadow-hover: 0 18px 44px rgba(17,17,69,0.16);
    --ring: 0 0 0 4px rgba(218,48,37,0.14);
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}

  body {{
    font-family: "Be Vietnam Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }}
  img {{ max-width: 100%; }}
  ::selection {{ background: rgba(218,48,37,0.18); }}

  /* Custom scrollbar */
  ::-webkit-scrollbar {{ width: 11px; height: 11px; }}
  ::-webkit-scrollbar-thumb {{ background: #d9cfbb; border-radius: 8px; border: 3px solid var(--bg); }}
  ::-webkit-scrollbar-thumb:hover {{ background: #c7bca4; }}

  /* Wide, uppercase display treatment — echoes SBO's extended grotesk headings */
  .display {{ text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }}

  @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  @keyframes floatGlow {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(3%,4%); }} }}

  /* ── HEADER ───────────────────────────────────────── */
  header {{
    position: sticky; top: 0; z-index: 500;
    background: rgba(17,17,69,0.80);
    -webkit-backdrop-filter: saturate(160%) blur(12px);
    backdrop-filter: saturate(160%) blur(12px);
    color: #fff;
    padding: 0 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.10);
    transition: background .25s, box-shadow .25s, border-color .25s;
  }}
  header.scrolled {{
    background: rgba(17,17,69,0.94);
    box-shadow: 0 8px 30px rgba(0,0,0,0.28);
    border-bottom-color: rgba(255,255,255,0.06);
  }}
  .header-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.9rem 0;
  }}
  .logo {{ display: flex; align-items: center; gap: 0.7rem; text-decoration: none; color: #fff; }}
  .logo-mark {{
    width: 38px; height: 38px;
    background: linear-gradient(150deg, var(--brand-accent), var(--brand-accent-2));
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 800;
    box-shadow: 0 4px 14px rgba(218,48,37,0.4);
  }}
  .logo-text {{ font-size: 1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; line-height: 1.15; }}
  .logo-sub {{ font-size: 0.66rem; opacity: 0.65; display: block; text-transform: uppercase; letter-spacing: 0.16em; }}
  header nav {{ display: flex; align-items: center; gap: 0.4rem; }}
  header nav a {{
    color: rgba(255,255,255,0.82);
    text-decoration: none;
    font-size: 0.9rem; font-weight: 500;
    padding: 0.45rem 0.7rem; border-radius: 8px;
    position: relative;
    transition: color .2s, background .2s;
  }}
  header nav a.navlink::after {{
    content: ''; position: absolute; left: 0.7rem; right: 0.7rem; bottom: 0.28rem;
    height: 2px; background: var(--brand-accent); border-radius: 2px;
    transform: scaleX(0); transform-origin: left; transition: transform .22s ease;
  }}
  header nav a.navlink:hover {{ color: #fff; }}
  header nav a.navlink:hover::after {{ transform: scaleX(1); }}
  header nav a.nav-cta {{
    background: linear-gradient(150deg, var(--brand-accent), var(--brand-accent-2));
    color: #fff; font-weight: 600;
    box-shadow: 0 4px 14px rgba(218,48,37,0.35);
  }}
  header nav a.nav-cta:hover {{ transform: translateY(-1px); box-shadow: 0 6px 18px rgba(218,48,37,0.45); }}
  @media (max-width: 640px) {{
    header nav a.navlink:not(.nav-cta) {{ display: none; }}
  }}

  /* ── HERO ─────────────────────────────────────────── */
  .hero {{
    position: relative; overflow: hidden;
    background: linear-gradient(160deg, #0d0d38 0%, var(--brand-dark) 45%, var(--mid-blue) 100%);
    color: #fff;
    text-align: center;
    padding: 5rem 2rem 6.5rem;
  }}
  /* dot-grid texture, faded toward edges */
  .hero::before {{
    content: ''; position: absolute; inset: 0;
    background-image: radial-gradient(rgba(255,255,255,0.09) 1px, transparent 1px);
    background-size: 24px 24px;
    -webkit-mask-image: radial-gradient(ellipse 80% 70% at 50% 30%, #000 40%, transparent 100%);
    mask-image: radial-gradient(ellipse 80% 70% at 50% 30%, #000 40%, transparent 100%);
    pointer-events: none;
  }}
  /* soft red glow */
  .hero::after {{
    content: ''; position: absolute; width: 620px; height: 620px;
    top: -220px; left: 50%; margin-left: -310px;
    background: radial-gradient(circle, rgba(218,48,37,0.42) 0%, transparent 62%);
    filter: blur(20px); pointer-events: none;
    animation: floatGlow 14s ease-in-out infinite;
  }}
  .hero-inner {{ position: relative; z-index: 1; max-width: 780px; margin: 0 auto; }}
  .hero-badge {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.16);
    color: #fff; border-radius: 999px; padding: 0.4rem 0.9rem;
    font-size: 0.8rem; font-weight: 500; margin-bottom: 1.5rem;
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
    animation: fadeUp .6s ease both;
  }}
  .hero-badge .dot {{
    width: 8px; height: 8px; border-radius: 50%; background: #35d07f;
    box-shadow: 0 0 0 4px rgba(53,208,127,0.22);
  }}
  .hero h1 {{
    font-size: clamp(2.2rem, 5vw, 3.4rem); font-weight: 800;
    margin-bottom: 1.1rem; letter-spacing: -0.02em; line-height: 1.08;
    animation: fadeUp .6s ease .05s both;
  }}
  .hero h1 .accent {{
    background: linear-gradient(120deg, #ff5a4d, var(--brand-accent));
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }}
  .hero p {{
    font-size: 1.12rem; opacity: 0.85; max-width: 600px; margin: 0 auto 2rem;
    color: var(--brand-light); animation: fadeUp .6s ease .1s both;
  }}
  .hero-cta {{
    display: flex; gap: 0.85rem; justify-content: center; flex-wrap: wrap;
    animation: fadeUp .6s ease .15s both;
  }}
  .btn-hero {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.8rem 1.5rem; border-radius: 10px; font-size: 0.95rem; font-weight: 600;
    text-decoration: none; cursor: pointer; border: 1.5px solid transparent;
    transition: transform .18s, box-shadow .18s, background .2s;
  }}
  .btn-hero-primary {{
    background: linear-gradient(150deg, var(--brand-accent), var(--brand-accent-2));
    color: #fff; box-shadow: 0 8px 22px rgba(218,48,37,0.4);
  }}
  .btn-hero-primary:hover {{ transform: translateY(-2px); box-shadow: 0 12px 28px rgba(218,48,37,0.5); }}
  .btn-hero-ghost {{
    background: rgba(255,255,255,0.06); color: #fff; border-color: rgba(255,255,255,0.28);
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
  }}
  .btn-hero-ghost:hover {{ background: rgba(255,255,255,0.14); transform: translateY(-2px); }}
  .hero-stats {{
    display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;
    margin-top: 3rem; animation: fadeUp .6s ease .2s both;
  }}
  .stat {{
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px; padding: 1rem 1.6rem; min-width: 130px;
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
  }}
  .stat-num {{ font-size: 2rem; font-weight: 800; color: #fff; line-height: 1; }}
  .stat-label {{ font-size: 0.8rem; opacity: 0.72; margin-top: 0.35rem; }}

  /* ── TRUST BAND ───────────────────────────────────── */
  .trust-band {{
    max-width: 1200px; margin: 1.75rem auto 2.25rem; padding: 0 2rem;
    display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;
  }}
  .trust-item {{
    display: flex; align-items: center; gap: 0.55rem;
    font-size: 0.86rem; color: var(--text-muted); font-weight: 500;
  }}
  .trust-item svg {{ color: var(--brand-accent); flex-shrink: 0; }}
  .trust-sep {{ color: var(--border); align-self: center; }}
  @media (max-width: 640px) {{ .trust-sep {{ display: none; }} }}

  /* ── SEARCH + FILTERS ─────────────────────────────── */
  .controls {{
    max-width: 1200px;
    margin: -2rem auto 2rem;
    padding: 0 2rem;
    position: relative;
    z-index: 10;
  }}
  .search-box {{
    background: var(--surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    padding: 1.1rem 1.25rem;
    display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;
  }}
  .search-input-wrap {{ flex: 1; min-width: 220px; position: relative; }}
  .search-input-wrap svg {{
    position: absolute; left: 0.85rem; top: 50%; transform: translateY(-50%);
    color: var(--text-muted); pointer-events: none;
  }}
  #search {{
    width: 100%;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 0.7rem 0.85rem 0.7rem 2.4rem;
    font-size: 0.95rem; font-family: inherit;
    outline: none; background: #fdfcf9;
    transition: border-color .2s, box-shadow .2s, background .2s;
  }}
  #search:focus {{ border-color: var(--brand-accent); box-shadow: var(--ring); background: #fff; }}
  .filter-wrap {{ display: flex; gap: 0.45rem; flex-wrap: wrap; align-items: center; }}
  .filter-label {{ font-size: 0.85rem; color: var(--text-muted); white-space: nowrap; }}
  .filter-btn {{
    border: 1.5px solid var(--border);
    background: var(--surface);
    border-radius: 999px;
    padding: 0.38rem 0.95rem;
    font-size: 0.85rem; font-family: inherit; font-weight: 500;
    cursor: pointer;
    transition: all .18s;
    color: var(--text-muted);
  }}
  .filter-btn:hover {{ border-color: var(--brand-accent); color: var(--brand-accent); }}
  .filter-btn.active {{
    background: var(--brand-dark);
    border-color: var(--brand-dark);
    color: #fff;
  }}

  /* ── SKILL GRID ───────────────────────────────────── */
  .grid-wrap {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem 4rem; }}
  .result-count {{ color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.25rem; }}
  .skills-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.25rem;
  }}
  .skill-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    cursor: pointer;
    transition: transform .25s, box-shadow .25s, border-color .25s;
    display: flex; flex-direction: column; gap: 0.75rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow);
    animation: fadeUp .5s ease both;
  }}
  .skill-card::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--brand-accent), var(--brand-dark));
    transform: scaleX(0); transform-origin: left; transition: transform .3s ease;
  }}
  .skill-card:hover {{ box-shadow: var(--shadow-hover); border-color: rgba(218,48,37,0.35); transform: translateY(-4px); }}
  .skill-card:hover::before {{ transform: scaleX(1); }}
  .card-header {{ display: flex; align-items: flex-start; gap: 0.85rem; }}
  .card-emoji {{
    width: 46px; height: 46px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.55rem; line-height: 1;
    background: linear-gradient(150deg, var(--brand-light), #fffdf7);
    border: 1px solid var(--border); border-radius: 12px;
    transition: transform .25s;
  }}
  .skill-card:hover .card-emoji {{ transform: scale(1.06) rotate(-3deg); }}
  .card-meta {{ flex: 1; min-width: 0; }}
  .card-name {{ font-size: 1.08rem; font-weight: 700; color: var(--brand-dark); letter-spacing: -0.01em; }}
  .card-author {{ font-size: 0.8rem; color: var(--text-muted); }}
  .card-desc {{ font-size: 0.9rem; color: var(--text-muted); line-height: 1.55; }}
  .card-footer {{ display: flex; gap: 0.45rem; flex-wrap: wrap; align-items: center; margin-top: auto; }}
  .card-install-hint .arrow {{ display: inline-block; transition: transform .2s; }}
  .skill-card:hover .card-install-hint .arrow {{ transform: translateX(4px); }}
  .badge {{
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-flex; align-items: center; gap: 0.3rem;
  }}
  .badge-cat {{ background: var(--brand-light); color: var(--brand-dark); }}
  .badge-harness {{ background: #eef1f0; color: var(--petrol); border: 1px solid #d8e0de; }}
  .badge-complexity-beginner {{ background: #eef1f0; color: var(--petrol); }}
  .badge-complexity-intermediate {{ background: #f5efdd; color: #8a6d1f; }}
  .badge-complexity-advanced {{ background: #fbeae8; color: var(--brand-accent); }}
  .badge-status-draft {{ background: #f5efdd; color: #8a6d1f; border: 1px solid #e6d9b5; }}
  .badge-status-in-review {{ background: #eaf0f6; color: var(--mid-blue); border: 1px solid #d3dfea; }}
  .badge-status-deprecated {{ background: #fbeae8; color: var(--brand-accent); border: 1px solid #f2cdc8; }}
  .badge-status-published {{ background: #ecf3ec; color: #2e7d32; border: 1px solid #cfe4d0; }}
  .skill-card.is-deprecated {{ opacity: 0.72; }}
  .skill-card.is-deprecated:hover {{ opacity: 1; }}
  .deprecation-banner {{
    background: #fbeae8; border: 1px solid #f2cdc8; color: #7a1f16;
    border-radius: var(--radius); padding: 0.85rem 1rem; margin-bottom: 1.25rem;
    font-size: 0.88rem; line-height: 1.5;
  }}
  .deprecation-banner strong {{ color: var(--brand-accent); }}
  .deprecation-banner a {{ color: var(--brand-accent); font-weight: 600; }}
  .card-install-hint {{
    font-size: 0.8rem; color: var(--brand-accent); font-weight: 600;
    margin-top: 0.25rem;
  }}

  .no-results {{
    text-align: center; padding: 4rem 2rem; color: var(--text-muted);
  }}
  .no-results-emoji {{ font-size: 3rem; margin-bottom: 1rem; }}

  /* ── MODAL ────────────────────────────────────────── */
  .modal-overlay {{
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: none; align-items: center; justify-content: center;
    padding: 1rem;
  }}
  .modal-overlay.open {{ display: flex; }}
  .modal {{
    background: var(--surface);
    border-radius: 16px;
    width: 100%; max-width: 780px;
    max-height: 90vh;
    display: flex; flex-direction: column;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    overflow: hidden;
  }}
  .modal-header {{
    background: linear-gradient(135deg, var(--brand-dark), var(--mid-blue));
    color: #fff;
    padding: 1.5rem;
    display: flex; gap: 1rem; align-items: flex-start;
    flex-shrink: 0;
  }}
  .modal-emoji {{ font-size: 2.5rem; }}
  .modal-title-wrap {{ flex: 1; }}
  .modal-title {{ font-size: 1.4rem; font-weight: 800; }}
  .modal-subtitle {{ font-size: 0.9rem; opacity: 0.8; margin-top: 0.25rem; }}
  .modal-close {{
    background: rgba(255,255,255,0.15);
    border: none; border-radius: 8px;
    color: #fff; font-size: 1.2rem;
    width: 32px; height: 32px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    transition: background .2s;
  }}
  .modal-close:hover {{ background: rgba(255,255,255,0.3); }}
  .modal-body {{ flex: 1; overflow-y: auto; padding: 1.5rem; }}
  .modal-tags {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }}
  .modal-desc {{ color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.95rem; }}

  /* Install tabs */
  .tabs {{ border-bottom: 2px solid var(--border); display: flex; gap: 0; margin-bottom: 1.25rem; }}
  .tab-btn {{
    padding: 0.6rem 1.1rem;
    border: none; background: none; cursor: pointer;
    font-size: 0.9rem; font-weight: 600; color: var(--text-muted);
    border-bottom: 2px solid transparent; margin-bottom: -2px;
    transition: all .2s;
  }}
  .tab-btn.active {{ color: var(--brand-blue); border-bottom-color: var(--brand-blue); }}
  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}
  .install-steps {{ list-style: none; counter-reset: step; }}
  .install-steps li {{
    counter-increment: step;
    padding: 0.6rem 0 0.6rem 2.5rem;
    position: relative;
    font-size: 0.9rem;
    border-bottom: 1px solid var(--bg);
  }}
  .install-steps li::before {{
    content: counter(step);
    position: absolute; left: 0; top: 0.6rem;
    background: var(--brand-blue); color: #fff;
    width: 22px; height: 22px; border-radius: 50%;
    font-size: 0.75rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
  }}
  .code-block {{
    background: var(--brand-dark); color: #e6e6f5;
    border-radius: 8px; padding: 1rem 1.25rem;
    font-family: "SF Mono", "Fira Code", monospace; font-size: 0.85rem;
    overflow-x: auto; margin: 0.75rem 0;
    position: relative;
  }}
  .copy-btn {{
    position: absolute; top: 0.5rem; right: 0.5rem;
    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
    color: #94a3b8; border-radius: 6px; padding: 0.3rem 0.6rem;
    font-size: 0.75rem; cursor: pointer; transition: all .2s;
  }}
  .copy-btn:hover {{ background: rgba(255,255,255,0.2); color: #fff; }}
  .copy-btn.copied {{ background: var(--brand-accent); color: #fff; border-color: var(--brand-accent); }}

  .skill-content-area {{
    background: #faf7f0;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-family: "SF Mono", "Fira Code", monospace; font-size: 0.82rem;
    white-space: pre-wrap; word-break: break-word;
    max-height: 320px; overflow-y: auto;
    margin: 0.75rem 0;
    line-height: 1.6;
    color: var(--text);
  }}
  .download-btn {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: var(--brand-blue); color: #fff;
    border: none; border-radius: 8px;
    padding: 0.65rem 1.25rem; font-size: 0.9rem; font-weight: 600;
    cursor: pointer; text-decoration: none;
    transition: background .2s;
    margin-top: 0.75rem;
  }}
  .download-btn:hover {{ background: var(--brand-dark); }}
  .download-btn-ghost {{
    background: transparent; border: 1.5px solid var(--brand-blue); color: var(--brand-blue);
  }}
  .download-btn-ghost:hover {{ background: var(--brand-light); }}
  .btn-row {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem; }}

  /* ── HOW TO CONTRIBUTE ────────────────────────────── */
  .contribute-section {{
    background: var(--brand-dark);
    color: #fff;
    padding: 4rem 2rem;
    text-align: center;
  }}
  .contribute-inner {{ max-width: 700px; margin: 0 auto; }}
  .contribute-inner h2 {{ font-size: 2rem; font-weight: 800; letter-spacing: -0.01em; margin-bottom: 0.75rem; }}
  .contribute-inner p {{ opacity: 0.8; margin-bottom: 1.5rem; color: var(--brand-light); }}
  .contribute-steps {{
    display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;
    margin: 2rem 0;
  }}
  .c-step {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 1.5rem 1.25rem;
    flex: 1; min-width: 160px; max-width: 220px;
    text-align: center;
    transition: transform .2s, background .2s, border-color .2s;
  }}
  .c-step:hover {{ transform: translateY(-4px); background: rgba(255,255,255,0.10); border-color: rgba(218,48,37,0.5); }}
  .c-step-num {{
    width: 40px; height: 40px; margin: 0 auto 0.85rem;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem; font-weight: 800; color: #fff;
    background: linear-gradient(150deg, var(--brand-accent), var(--brand-accent-2));
    border-radius: 50%;
    box-shadow: 0 6px 16px rgba(218,48,37,0.4);
  }}
  .c-step p {{ font-size: 0.85rem; opacity: 0.82; }}
  .contribute-eyebrow {{
    display: inline-block; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--brand-accent); margin-bottom: 0.75rem;
  }}
  .cta-btn {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: var(--brand-accent); color: #fff;
    border-radius: 8px; padding: 0.75rem 1.5rem;
    font-weight: 700; text-decoration: none; font-size: 0.95rem;
    transition: opacity .2s;
  }}
  .cta-btn:hover {{ opacity: 0.9; }}
  .cta-btn-ghost {{
    background: transparent;
    border: 1.5px solid rgba(255,255,255,0.4);
    color: #fff;
  }}
  .cta-btn-ghost:hover {{ border-color: #fff; opacity: 1; }}

  /* ── FOOTER ───────────────────────────────────────── */
  footer {{
    background: #0c0c2e;
    color: rgba(255,255,255,0.6);
    border-top: 1px solid rgba(255,255,255,0.08);
  }}
  .footer-top {{
    max-width: 1200px; margin: 0 auto; padding: 3rem 2rem 2rem;
    display: grid; grid-template-columns: 1.6fr 1fr 1fr; gap: 2rem;
  }}
  .footer-brand .logo-mark {{ margin-bottom: 0.85rem; }}
  .footer-brand p {{ font-size: 0.86rem; max-width: 340px; line-height: 1.6; }}
  .footer-col h4 {{
    color: #fff; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.12em;
    margin-bottom: 0.9rem; font-weight: 700;
  }}
  .footer-col a {{
    display: block; color: rgba(255,255,255,0.6); text-decoration: none;
    font-size: 0.88rem; padding: 0.28rem 0; transition: color .2s;
  }}
  .footer-col a:hover {{ color: var(--brand-accent); }}
  .footer-bottom {{
    border-top: 1px solid rgba(255,255,255,0.08);
    padding: 1.1rem 2rem; text-align: center; font-size: 0.8rem;
    color: rgba(255,255,255,0.45);
  }}
  .footer-bottom code {{ color: rgba(255,255,255,0.6); }}
  @media (max-width: 640px) {{ .footer-top {{ grid-template-columns: 1fr; gap: 1.5rem; }} }}

  /* ── RESPONSIVE ───────────────────────────────────── */
  @media (max-width: 600px) {{
    .hero {{ padding: 2.5rem 1rem 3.5rem; }}
    .controls {{ margin-top: -1rem; padding: 0 1rem; }}
    .grid-wrap {{ padding: 0 1rem 3rem; }}
    .skills-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header id="site-header">
  <div class="header-inner">
    <a class="logo" href="#">
      <div class="logo-mark">S</div>
      <div>
        <span class="logo-text">Skill Marketplace</span>
        <span class="logo-sub">by accilium</span>
      </div>
    </a>
    <nav>
      <a class="navlink" href="#skills">Browse</a>
      <a class="navlink" href="#contribute">Contribute</a>
      <a class="navlink" href="https://github.com/acc-sebastian/skill-marketplace" target="_blank">GitHub ↗</a>
      <a class="navlink nav-cta" href="{PROPOSE_URL}" target="_blank">💡 Skill vorschlagen</a>
    </nav>
  </div>
</header>

<div class="hero">
  <div class="hero-inner">
    <span class="hero-badge"><span class="dot"></span> Live &amp; auto-updated for Claude Code</span>
    <h1>AI Skills, Ready to <span class="accent">Deploy</span></h1>
    <p>Plug-and-play skills that turn any AI assistant into a specialist. Governed, versioned, and installable in under a minute.</p>
    <div class="hero-cta">
      <a class="btn-hero btn-hero-primary" href="#skills">Browse skills</a>
      <a class="btn-hero btn-hero-ghost" href="https://github.com/acc-sebastian/skill-marketplace/blob/main/docs/enterprise-setup.md" target="_blank">⚡ Install as plugin</a>
    </div>
    <div class="hero-stats">
      <div class="stat"><div class="stat-num" id="stat-skills">—</div><div class="stat-label">Skills available</div></div>
      <div class="stat"><div class="stat-num" id="stat-cats">—</div><div class="stat-label">Categories</div></div>
      <div class="stat"><div class="stat-num">3</div><div class="stat-label">Harnesses supported</div></div>
    </div>
  </div>
</div>

<div class="controls" id="skills">
  <div class="search-box">
    <div class="search-input-wrap">
      <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
      <input type="text" id="search" placeholder="Search skills, tags, descriptions…">
    </div>
    <div class="filter-wrap">
      <span class="filter-label">Category:</span>
      <button class="filter-btn active" data-filter="all">All</button>
      {cat_buttons}
    </div>
  </div>
</div>

<div class="trust-band">
  <span class="trust-item"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/></svg> Reviewed via pull requests</span>
  <span class="trust-sep">•</span>
  <span class="trust-item"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="9"/></svg> Semantic versioning &amp; releases</span>
  <span class="trust-sep">•</span>
  <span class="trust-item"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/></svg> Auto-updated for everyone</span>
  <span class="trust-sep">•</span>
  <span class="trust-item"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg> Works across harnesses</span>
</div>

<div class="grid-wrap">
  <p class="result-count" id="result-count"></p>
  <div class="skills-grid" id="skills-grid"></div>
  <div class="no-results" id="no-results" style="display:none">
    <div class="no-results-emoji">🔍</div>
    <strong>No skills found</strong>
    <p>Try a different search term or category filter.</p>
  </div>
</div>

<!-- CONTRIBUTE SECTION -->
<section class="contribute-section" id="contribute">
  <div class="contribute-inner">
    <span class="contribute-eyebrow">Open contribution model</span>
    <h2>Add Your Own Skill</h2>
    <p>Create a skill once — share it with the entire team. Once merged, it's live on this page within minutes.</p>
    <div class="contribute-steps">
      <div class="c-step"><div class="c-step-num">1</div><p>Fork the GitHub repo</p></div>
      <div class="c-step"><div class="c-step-num">2</div><p>Add <code>metadata.json</code> + <code>SKILL.md</code></p></div>
      <div class="c-step"><div class="c-step-num">3</div><p>Open a pull request</p></div>
      <div class="c-step"><div class="c-step-num">4</div><p>It's live! 🚀</p></div>
    </div>
    <p style="font-size:0.9rem;opacity:0.7;margin-bottom:1rem">Kein Git? Kein Problem — über das Formular geht's ganz ohne.</p>
    <div style="display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap">
      <a class="cta-btn" href="{PROPOSE_URL}" target="_blank">
        💡 Neue Skill vorschlagen
      </a>
      <a class="cta-btn cta-btn-ghost" href="https://github.com/acc-sebastian/skill-marketplace/blob/main/CONTRIBUTING.md" target="_blank">
        📖 Contributor Guide (per PR)
      </a>
    </div>
  </div>
</section>

<!-- MODAL -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModalOnOverlay(event)">
  <div class="modal" id="modal">
    <div class="modal-header">
      <span class="modal-emoji" id="modal-emoji"></span>
      <div class="modal-title-wrap">
        <div class="modal-title" id="modal-title"></div>
        <div class="modal-subtitle" id="modal-subtitle"></div>
      </div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div id="modal-deprecation"></div>
      <div class="modal-tags" id="modal-tags"></div>
      <p class="modal-desc" id="modal-desc"></p>

      <div class="tabs">
        <button class="tab-btn active" onclick="switchTab(event,'claude-code')">Claude Code</button>
        <button class="tab-btn" onclick="switchTab(event,'copilot')">Copilot Studio</button>
        <button class="tab-btn" onclick="switchTab(event,'generic')">Any LLM</button>
        <button class="tab-btn" onclick="switchTab(event,'preview')">Skill Preview</button>
      </div>

      <div class="tab-panel active" id="tab-claude-code">
        <div class="deprecation-banner" style="background:#eef3fb;border-color:#d3dfea;color:var(--mid-blue)">
          ⭐ <strong>Recommended:</strong> install the whole marketplace as a plugin — you get <em>every</em> skill and stay auto-updated:
          <div class="code-block" style="position:relative;margin-top:0.5rem">
            <span>/plugin marketplace add acc-sebastian/skill-marketplace</span><br>
            <span>/plugin install sbo-skills@sbo-skill-marketplace</span>
            <button class="copy-btn" onclick="copyCode(this, '/plugin marketplace add acc-sebastian/skill-marketplace')">Copy</button>
          </div>
          Enterprises can push this to all users automatically — see the <a href="https://github.com/acc-sebastian/skill-marketplace/blob/main/docs/enterprise-setup.md" target="_blank">setup guide</a>.
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.5rem">Or install just this one skill manually:</p>
        <ol class="install-steps">
          <li>Download <code>SKILL.md</code> from the button below.</li>
          <li>Place it in a skill folder in your Claude Code skills directory:<br>
            <div class="code-block" style="position:relative">
              <span># Project-level (recommended)</span><br>
              <span>mkdir -p .claude/skills/SKILL_ID &amp;&amp; mv SKILL.md .claude/skills/SKILL_ID/</span><br><br>
              <span># Or global (applies to all projects)</span><br>
              <span>mkdir -p ~/.claude/skills/SKILL_ID &amp;&amp; mv SKILL.md ~/.claude/skills/SKILL_ID/</span>
              <button class="copy-btn" onclick="copyCode(this, 'mkdir -p .claude/skills/SKILL_ID &amp;&amp; mv SKILL.md .claude/skills/SKILL_ID/')">Copy</button>
            </div>
          </li>
          <li>Restart Claude Code (or run <code>/reload</code>). The skill is now active.</li>
          <li>Trigger it by saying one of the trigger phrases listed in the skill description.</li>
        </ol>
        <div class="btn-row">
          <button class="download-btn" id="btn-download-claude" onclick="downloadSkill()">⬇ Download SKILL.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">📋 Copy to clipboard</button>
        </div>
      </div>

      <div class="tab-panel" id="tab-copilot">
        <ol class="install-steps">
          <li>Download <code>SKILL.md</code> and open it in a text editor.</li>
          <li>Skip the frontmatter (the section between <code>---</code> markers at the top).</li>
          <li>Copy everything after the second <code>---</code> line.</li>
          <li>In Copilot Studio, open your Copilot and navigate to <strong>Topics → System</strong>.</li>
          <li>Paste the skill content into the <strong>System Prompt</strong> of a new Topic, or add it as a <strong>Generative Answers</strong> plugin description.</li>
          <li>Save and publish your Copilot.</li>
        </ol>
        <div class="btn-row">
          <button class="download-btn" onclick="downloadSkill()">⬇ Download SKILL.md</button>
        </div>
      </div>

      <div class="tab-panel" id="tab-generic">
        <ol class="install-steps">
          <li>Download <code>SKILL.md</code> or copy the content below.</li>
          <li>Remove the frontmatter block at the top (the section between <code>---</code> markers).</li>
          <li>Paste the remaining content as a <strong>system prompt</strong> in your AI tool of choice (ChatGPT, Gemini, Azure OpenAI, etc.).</li>
          <li>Alternatively, paste it as the first message in a new conversation.</li>
          <li>The AI will follow the structured role, process, and output format defined in the skill.</li>
        </ol>
        <div class="btn-row">
          <button class="download-btn" onclick="downloadSkill()">⬇ Download SKILL.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">📋 Copy to clipboard</button>
        </div>
      </div>

      <div class="tab-panel" id="tab-preview">
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.75rem">Full content of <code>SKILL.md</code> — this is what gets installed in your AI harness.</p>
        <div class="skill-content-area" id="modal-skill-content"></div>
        <div class="btn-row">
          <button class="download-btn" onclick="downloadSkill()">⬇ Download SKILL.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">📋 Copy to clipboard</button>
        </div>
      </div>
    </div>
  </div>
</div>

<footer>
  <div class="footer-top">
    <div class="footer-brand">
      <div class="logo-mark">S</div>
      <p>A curated, governed library of AI skills that plug into Claude Code, Copilot Studio, or any LLM — always up to date.</p>
    </div>
    <div class="footer-col">
      <h4>Product</h4>
      <a href="#skills">Browse skills</a>
      <a href="{PROPOSE_URL}" target="_blank">Propose a skill</a>
      <a href="https://github.com/acc-sebastian/skill-marketplace/releases" target="_blank">Releases</a>
      <a href="{SITE_URL}/catalog.json" target="_blank">Catalog API</a>
    </div>
    <div class="footer-col">
      <h4>Resources</h4>
      <a href="https://github.com/acc-sebastian/skill-marketplace/blob/main/docs/enterprise-setup.md" target="_blank">Enterprise setup</a>
      <a href="https://github.com/acc-sebastian/skill-marketplace/blob/main/CONTRIBUTING.md" target="_blank">Contributor guide</a>
      <a href="https://github.com/acc-sebastian/skill-marketplace/blob/main/ROADMAP.md" target="_blank">Roadmap</a>
      <a href="https://github.com/acc-sebastian/skill-marketplace" target="_blank">GitHub ↗</a>
    </div>
  </div>
  <div class="footer-bottom">
    Built with ♥ by accilium &nbsp;·&nbsp; Auto-generated by <code>scripts/build_site.py</code>
  </div>
</footer>

<script>
const SKILLS = {skills_json};

let activeFilter = 'all';
let searchQuery = '';

function renderCards() {{
  const grid = document.getElementById('skills-grid');
  const noRes = document.getElementById('no-results');
  const count = document.getElementById('result-count');

  const filtered = SKILLS.filter(s => {{
    const matchCat = activeFilter === 'all' || s.category === activeFilter;
    const q = searchQuery.toLowerCase();
    const matchSearch = !q ||
      (s.name || '').toLowerCase().includes(q) ||
      (s.description || '').toLowerCase().includes(q) ||
      (s.tags || []).some(t => t.toLowerCase().includes(q)) ||
      (s.category || '').toLowerCase().includes(q) ||
      (s.author || '').toLowerCase().includes(q);
    return matchCat && matchSearch;
  }});

  grid.innerHTML = '';
  if (filtered.length === 0) {{
    noRes.style.display = 'block';
    count.textContent = '';
    return;
  }}
  noRes.style.display = 'none';
  count.textContent = `Showing ${{filtered.length}} of ${{SKILLS.length}} skills`;

  filtered.forEach((skill, idx) => {{
    const card = document.createElement('div');
    const status = skill.status || 'published';
    card.className = 'skill-card' + (status === 'deprecated' ? ' is-deprecated' : '');
    card.style.animationDelay = (idx * 0.05) + 's';
    card.onclick = () => openModal(skill);

    const harnessBadges = (skill.harnesses || []).slice(0,2).map(h => {{
      const labels = {{'claude-code':'Claude Code','copilot-studio':'Copilot Studio','generic':'Any LLM'}};
      return `<span class="badge badge-harness">${{labels[h] || h}}</span>`;
    }}).join('');

    const complexityClass = `badge-complexity-${{skill.complexity || 'beginner'}}`;
    const complexityLabel = (skill.complexity || 'beginner').charAt(0).toUpperCase() + (skill.complexity||'beginner').slice(1);

    const statusBadge = statusBadgeHtml(status);

    card.innerHTML = `
      <div class="card-header">
        <span class="card-emoji">${{skill.emoji || '🔧'}}</span>
        <div class="card-meta">
          <div class="card-name">${{skill.name || skill.id}}</div>
          <div class="card-author">by ${{skill.author || 'Unknown'}}</div>
        </div>
      </div>
      <p class="card-desc">${{(skill.description || '').substring(0, 130)}}${{(skill.description||'').length > 130 ? '…' : ''}}</p>
      <div class="card-footer">
        <span class="badge badge-cat">${{skill.category || 'Other'}}</span>
        <span class="badge ${{complexityClass}}">${{complexityLabel}}</span>
        ${{statusBadge}}${{harnessBadges}}
      </div>
      <div class="card-install-hint">View &amp; install <span class="arrow">→</span></div>
    `;
    grid.appendChild(card);
  }});
}}

// Status badge is shown for every status except plain "published"
function statusBadgeHtml(status) {{
  if (!status || status === 'published') return '';
  const labels = {{'draft':'Draft','in-review':'In Review','deprecated':'Deprecated'}};
  return `<span class="badge badge-status-${{status}}">${{labels[status] || status}}</span>`;
}}

function openModal(skill) {{
  currentSkill = skill;
  document.getElementById('modal-emoji').textContent = skill.emoji || '🔧';
  document.getElementById('modal-title').textContent = skill.name || skill.id;
  document.getElementById('modal-subtitle').textContent = `${{skill.category}} · v${{skill.version}} · by ${{skill.author}}`;
  document.getElementById('modal-desc').textContent = skill.description || '';
  document.getElementById('modal-skill-content').textContent = skill.skill_content || '(No SKILL.md content found)';

  // Deprecation banner
  const depEl = document.getElementById('modal-deprecation');
  if ((skill.status || 'published') === 'deprecated') {{
    const successor = SKILLS.find(s => s.id === skill.deprecated_by);
    const successorLink = successor
      ? `<a href="#" onclick="event.preventDefault(); openModal(SKILLS.find(s => s.id==='${{successor.id}}'))">${{successor.name}}</a>`
      : (skill.deprecated_by || 'a newer skill');
    const sunset = skill.sunset_date ? ` It will be removed on <strong>${{skill.sunset_date}}</strong>.` : '';
    depEl.innerHTML = `<div class="deprecation-banner">⚠️ <strong>Deprecated.</strong> This skill is superseded by ${{successorLink}}.${{sunset}} Please migrate.</div>`;
  }} else {{
    depEl.innerHTML = '';
  }}

  const tags = document.getElementById('modal-tags');
  tags.innerHTML = '';
  (skill.tags || []).forEach(t => {{
    const b = document.createElement('span');
    b.className = 'badge badge-cat';
    b.textContent = '#' + t;
    tags.appendChild(b);
  }});
  (skill.harnesses || []).forEach(h => {{
    const labels = {{'claude-code':'Claude Code','copilot-studio':'Copilot Studio','generic':'Any LLM'}};
    const b = document.createElement('span');
    b.className = 'badge badge-harness';
    b.textContent = labels[h] || h;
    tags.appendChild(b);
  }});

  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
  switchTab(null, 'claude-code');
}}

let currentSkill = null;

function closeModal() {{
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}}
function closeModalOnOverlay(e) {{
  if (e.target === document.getElementById('modal-overlay')) closeModal();
}}
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});

function switchTab(e, tabId) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  if (e) e.currentTarget.classList.add('active');
  else {{
    document.querySelectorAll('.tab-btn').forEach(b => {{
      if (b.getAttribute('onclick').includes(tabId)) b.classList.add('active');
    }});
  }}
  const panel = document.getElementById('tab-' + tabId);
  if (panel) panel.classList.add('active');
}}

function downloadSkill() {{
  if (!currentSkill) return;
  const blob = new Blob([currentSkill.skill_content || ''], {{type: 'text/markdown'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'SKILL.md';
  a.click();
  URL.revokeObjectURL(a.href);
}}

function copySkillContent() {{
  if (!currentSkill) return;
  navigator.clipboard.writeText(currentSkill.skill_content || '');
}}

function copyCode(btn, text) {{
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy'; btn.classList.remove('copied'); }}, 2000);
  }});
}}

// Filters
document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    renderCards();
  }});
}});

// Search
document.getElementById('search').addEventListener('input', e => {{
  searchQuery = e.target.value;
  renderCards();
}});

// Stats
document.getElementById('stat-skills').textContent = SKILLS.length;
const cats = new Set(SKILLS.map(s => s.category));
document.getElementById('stat-cats').textContent = cats.size;

// Sticky header shadow on scroll
const _hdr = document.getElementById('site-header');
const _onScroll = () => {{ _hdr.classList.toggle('scrolled', window.scrollY > 8); }};
window.addEventListener('scroll', _onScroll, {{ passive: true }});
_onScroll();

// Init
renderCards();
</script>
</body>
</html>
"""


def main():
    DOCS_DIR.mkdir(exist_ok=True)
    print("Loading skills...")
    skills = load_skills()

    # Archived skills stay in the repo for provenance but leave site + catalog
    visible = [s for s in skills if s.get("status") != "archived"]
    hidden = len(skills) - len(visible)
    if hidden:
        print(f"  ({hidden} archived skill(s) excluded)")

    print(f"\nBuilding site with {len(visible)} skills...")
    html = build_html(visible)
    out = DOCS_DIR / "index.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done! -> {out}")
    size_kb = out.stat().st_size / 1024
    print(f"Site size: {size_kb:.1f} KB")

    catalog = build_catalog(visible)
    cat_out = DOCS_DIR / "catalog.json"
    with open(cat_out, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Catalog -> {cat_out} ({catalog['count']} skills)")

    # Publish the skill schema alongside the site so catalog consumers can validate
    schema_src = ROOT / "schema" / "skill.schema.json"
    if schema_src.exists():
        schema_dir = DOCS_DIR / "schema"
        schema_dir.mkdir(exist_ok=True)
        (schema_dir / "skill.schema.json").write_text(
            schema_src.read_text(encoding="utf-8"), encoding="utf-8"
        )
        print(f"Schema  -> {schema_dir / 'skill.schema.json'}")


if __name__ == "__main__":
    main()
