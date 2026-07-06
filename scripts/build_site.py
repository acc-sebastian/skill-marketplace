#!/usr/bin/env python3
"""
Build the Skill Marketplace static site + machine-readable catalog.

Reads:  skills/*/metadata.json + skills/*/skill.md
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
        skill_file = skill_dir / "skill.md"
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
            "download_url": f"{RAW_BASE}/{s['folder']}/skill.md",
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
    --brand-light: #f8f3e5;    /* warm cream */
    --petrol: #36494d;         /* SBO azure-petrol */
    --mid-blue: #253e5c;       /* SBO middle-blue */
    --sand: #d6ceb9;           /* SBO warm sand */
    --bg: #f6f2ea;             /* warm paper background */
    --surface: #ffffff;
    --border: #e6ddcb;         /* warm border */
    --text: #1b1b1b;           /* SBO near-black */
    --text-muted: #6a6c6e;     /* SBO soft grey */
    --radius: 4px;             /* SBO uses crisp, low-radius corners */
    --shadow: 0 2px 14px rgba(17,17,69,0.08);
    --shadow-hover: 0 10px 34px rgba(17,17,69,0.16);
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: "Be Vietnam Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }}

  /* Wide, uppercase display treatment — echoes SBO's extended grotesk headings */
  .display {{ text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }}

  /* ── HEADER ───────────────────────────────────────── */
  header {{
    background: var(--brand-dark);
    color: #fff;
    padding: 0 2rem;
    border-bottom: 3px solid var(--brand-accent);
  }}
  .header-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 0;
  }}
  .logo {{ display: flex; align-items: center; gap: 0.75rem; text-decoration: none; color: #fff; }}
  .logo-mark {{
    width: 36px; height: 36px;
    background: var(--brand-accent);
    border-radius: 3px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 800;
  }}
  .logo-text {{ font-size: 1.05rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; }}
  .logo-sub {{ font-size: 0.7rem; opacity: 0.7; display: block; text-transform: uppercase; letter-spacing: 0.16em; }}
  header nav a {{
    color: rgba(255,255,255,0.85);
    text-decoration: none;
    font-size: 0.9rem;
    margin-left: 1.5rem;
    transition: color .2s;
  }}
  header nav a:hover {{ color: #fff; }}

  /* ── HERO ─────────────────────────────────────────── */
  .hero {{
    background: linear-gradient(135deg, var(--brand-dark) 0%, var(--mid-blue) 100%);
    color: #fff;
    text-align: center;
    padding: 4.5rem 2rem 5.5rem;
  }}
  .hero h1 {{
    font-size: clamp(2rem, 4.5vw, 3.1rem); font-weight: 800;
    margin-bottom: 1rem; letter-spacing: -0.01em; line-height: 1.1;
  }}
  .hero h1 .accent {{ color: var(--brand-accent); }}
  .hero p {{ font-size: 1.1rem; opacity: 0.82; max-width: 580px; margin: 0 auto 2rem; color: var(--brand-light); }}
  .hero-stats {{
    display: flex; gap: 2rem; justify-content: center; flex-wrap: wrap;
    margin-top: 2.5rem;
  }}
  .stat {{ text-align: center; }}
  .stat-num {{ font-size: 2rem; font-weight: 800; color: var(--brand-accent); }}
  .stat-label {{ font-size: 0.85rem; opacity: 0.8; }}

  /* ── SEARCH + FILTERS ─────────────────────────────── */
  .controls {{
    max-width: 1200px;
    margin: -1.5rem auto 2rem;
    padding: 0 2rem;
    position: relative;
    z-index: 10;
  }}
  .search-box {{
    background: var(--surface);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 1.25rem 1.5rem;
    display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;
  }}
  .search-input-wrap {{ flex: 1; min-width: 220px; position: relative; }}
  .search-input-wrap svg {{
    position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%);
    color: var(--text-muted); pointer-events: none;
  }}
  #search {{
    width: 100%;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.75rem 0.6rem 2.25rem;
    font-size: 0.95rem;
    outline: none;
    transition: border-color .2s;
  }}
  #search:focus {{ border-color: var(--brand-accent); }}
  .filter-wrap {{ display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }}
  .filter-label {{ font-size: 0.85rem; color: var(--text-muted); white-space: nowrap; }}
  .filter-btn {{
    border: 1.5px solid var(--border);
    background: var(--surface);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all .2s;
    color: var(--text-muted);
  }}
  .filter-btn:hover, .filter-btn.active {{
    background: var(--brand-blue);
    border-color: var(--brand-blue);
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
    border: 1.5px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    cursor: pointer;
    transition: all .25s;
    display: flex; flex-direction: column; gap: 0.75rem;
    position: relative;
    overflow: hidden;
  }}
  .skill-card::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--brand-accent), var(--brand-dark));
    opacity: 0; transition: opacity .25s;
  }}
  .skill-card:hover {{ box-shadow: var(--shadow-hover); border-color: var(--brand-accent); transform: translateY(-2px); }}
  .skill-card:hover::before {{ opacity: 1; }}
  .card-header {{ display: flex; align-items: flex-start; gap: 0.75rem; }}
  .card-emoji {{ font-size: 2rem; line-height: 1; flex-shrink: 0; }}
  .card-meta {{ flex: 1; min-width: 0; }}
  .card-name {{ font-size: 1.05rem; font-weight: 700; color: var(--brand-dark); }}
  .card-author {{ font-size: 0.8rem; color: var(--text-muted); }}
  .card-desc {{ font-size: 0.9rem; color: var(--text-muted); line-height: 1.5; }}
  .card-footer {{ display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; margin-top: auto; }}
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
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    padding: 1.25rem;
    flex: 1; min-width: 160px; max-width: 220px;
    text-align: center;
  }}
  .c-step-num {{
    font-size: 1.5rem; font-weight: 800; color: var(--brand-accent);
    margin-bottom: 0.5rem;
  }}
  .c-step p {{ font-size: 0.85rem; opacity: 0.8; }}
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
    background: var(--brand-dark);
    color: rgba(255,255,255,0.55);
    text-align: center;
    padding: 1.5rem;
    font-size: 0.82rem;
    border-top: 3px solid var(--brand-accent);
  }}

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

<header>
  <div class="header-inner">
    <a class="logo" href="#">
      <div class="logo-mark">S</div>
      <div>
        <span class="logo-text">Skill Marketplace</span>
        <span class="logo-sub">by accilium</span>
      </div>
    </a>
    <nav>
      <a href="#skills">Browse</a>
      <a href="#contribute">Contribute</a>
      <a href="{PROPOSE_URL}" target="_blank">💡 Skill vorschlagen</a>
      <a href="https://github.com/acc-sebastian/skill-marketplace" target="_blank">GitHub ↗</a>
    </nav>
  </div>
</header>

<div class="hero">
  <h1>AI Skills, Ready to <span class="accent">Deploy</span></h1>
  <p>Plug-and-play prompts that turn any AI assistant into a specialist. Browse, download, and install in under a minute.</p>
  <div class="hero-stats">
    <div class="stat"><div class="stat-num" id="stat-skills">—</div><div class="stat-label">Skills available</div></div>
    <div class="stat"><div class="stat-num" id="stat-cats">—</div><div class="stat-label">Categories</div></div>
    <div class="stat"><div class="stat-num">3</div><div class="stat-label">Harnesses supported</div></div>
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
    <h2>Add Your Own Skill</h2>
    <p>Create a skill once — share it with the entire team. Once merged, it's live on this page within minutes.</p>
    <div class="contribute-steps">
      <div class="c-step"><div class="c-step-num">1</div><p>Fork the GitHub repo</p></div>
      <div class="c-step"><div class="c-step-num">2</div><p>Add <code>metadata.json</code> + <code>skill.md</code></p></div>
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
        <ol class="install-steps">
          <li>Download <code>skill.md</code> from the button below.</li>
          <li>Copy the file into your Claude Code skills directory:<br>
            <div class="code-block" style="position:relative">
              <span># Project-level (recommended)</span><br>
              <span>cp skill.md .claude/skills/</span><br><br>
              <span># Or global (applies to all projects)</span><br>
              <span>cp skill.md ~/.claude/skills/</span>
              <button class="copy-btn" onclick="copyCode(this, 'cp skill.md .claude/skills/')">Copy</button>
            </div>
          </li>
          <li>Restart Claude Code (or run <code>/reload</code>). The skill is now active.</li>
          <li>Trigger it by saying one of the trigger phrases listed in the skill description.</li>
        </ol>
        <div class="btn-row">
          <button class="download-btn" id="btn-download-claude" onclick="downloadSkill()">⬇ Download skill.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">📋 Copy to clipboard</button>
        </div>
      </div>

      <div class="tab-panel" id="tab-copilot">
        <ol class="install-steps">
          <li>Download <code>skill.md</code> and open it in a text editor.</li>
          <li>Skip the frontmatter (the section between <code>---</code> markers at the top).</li>
          <li>Copy everything after the second <code>---</code> line.</li>
          <li>In Copilot Studio, open your Copilot and navigate to <strong>Topics → System</strong>.</li>
          <li>Paste the skill content into the <strong>System Prompt</strong> of a new Topic, or add it as a <strong>Generative Answers</strong> plugin description.</li>
          <li>Save and publish your Copilot.</li>
        </ol>
        <div class="btn-row">
          <button class="download-btn" onclick="downloadSkill()">⬇ Download skill.md</button>
        </div>
      </div>

      <div class="tab-panel" id="tab-generic">
        <ol class="install-steps">
          <li>Download <code>skill.md</code> or copy the content below.</li>
          <li>Remove the frontmatter block at the top (the section between <code>---</code> markers).</li>
          <li>Paste the remaining content as a <strong>system prompt</strong> in your AI tool of choice (ChatGPT, Gemini, Azure OpenAI, etc.).</li>
          <li>Alternatively, paste it as the first message in a new conversation.</li>
          <li>The AI will follow the structured role, process, and output format defined in the skill.</li>
        </ol>
        <div class="btn-row">
          <button class="download-btn" onclick="downloadSkill()">⬇ Download skill.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">📋 Copy to clipboard</button>
        </div>
      </div>

      <div class="tab-panel" id="tab-preview">
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.75rem">Full content of <code>skill.md</code> — this is what gets installed in your AI harness.</p>
        <div class="skill-content-area" id="modal-skill-content"></div>
        <div class="btn-row">
          <button class="download-btn" onclick="downloadSkill()">⬇ Download skill.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">📋 Copy to clipboard</button>
        </div>
      </div>
    </div>
  </div>
</div>

<footer>
  Built with ♥ by accilium &mdash; <a href="https://github.com/acc-sebastian/skill-marketplace" style="color:inherit">GitHub</a>
  &nbsp;·&nbsp; Auto-generated by <code>scripts/build_site.py</code>
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

  filtered.forEach(skill => {{
    const card = document.createElement('div');
    const status = skill.status || 'published';
    card.className = 'skill-card' + (status === 'deprecated' ? ' is-deprecated' : '');
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
      <div class="card-install-hint">Click to install →</div>
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
  document.getElementById('modal-skill-content').textContent = skill.skill_content || '(No skill.md content found)';

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
  a.download = 'skill.md';
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
