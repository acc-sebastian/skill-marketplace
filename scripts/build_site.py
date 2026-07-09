#!/usr/bin/env python3
"""
Build the Skill Marketplace static site + machine-readable catalogs.

Reads:  skills/*/metadata.json  + skills/*/SKILL.md
        prompts/*/metadata.json + prompts/*/PROMPT.md
Writes: docs/index.html          (website: Skill Marketplace + Prompt Library)
        docs/catalog.json        (machine-readable skill manifest)
        docs/prompt-catalog.json (machine-readable prompt manifest)

Run locally:
    python scripts/build_site.py
"""

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
PROMPTS_DIR = ROOT / "prompts"
DOCS_DIR = ROOT / "docs"

REPO = "acc-sebastian/skill-marketplace"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/skills"
RAW_PROMPTS_BASE = f"https://raw.githubusercontent.com/{REPO}/main/prompts"
SITE_URL = "https://acc-sebastian.github.io/skill-marketplace"
PROPOSE_URL = f"https://github.com/{REPO}/issues/new?template=new-skill.yml"
PROPOSE_PROMPT_URL = f"https://github.com/{REPO}/issues/new?template=new-prompt.yml"


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


FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def strip_frontmatter(text):
    return FRONTMATTER_RE.sub("", text, count=1).lstrip("\n")


def load_prompts():
    prompts = []
    if not PROMPTS_DIR.exists():
        return prompts
    for prompt_dir in sorted(PROMPTS_DIR.iterdir()):
        if not prompt_dir.is_dir():
            continue
        meta_file = prompt_dir / "metadata.json"
        prompt_file = prompt_dir / "PROMPT.md"
        if not meta_file.exists():
            print(f"  SKIP {prompt_dir.name} — no metadata.json")
            continue
        with open(meta_file, encoding="utf-8") as f:
            meta = json.load(f)
        raw = ""
        if prompt_file.exists():
            with open(prompt_file, encoding="utf-8") as f:
                raw = f.read()
        meta["prompt_content"] = raw                      # full file, for download
        meta["prompt_template"] = strip_frontmatter(raw)  # copy/fill payload
        meta["folder"] = prompt_dir.name
        prompts.append(meta)
        print(f"  OK  {meta.get('name', prompt_dir.name)}")
    return prompts


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


def build_prompt_catalog(prompts):
    """Machine-readable manifest of the Prompt Library (no HTML parsing needed)."""
    entries = []
    for p in prompts:
        entries.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "description": p.get("description"),
            "version": p.get("version"),
            "status": p.get("status", "published"),
            "category": p.get("category"),
            "tags": p.get("tags", []),
            "complexity": p.get("complexity"),
            "owner": p.get("owner"),
            "author": p.get("author"),
            "last_reviewed": p.get("last_reviewed"),
            "deprecated_by": p.get("deprecated_by"),
            "sunset_date": p.get("sunset_date"),
            "variables": [
                {"name": v.get("name"), "required": v.get("required", False)}
                for v in p.get("variables", [])
            ],
            "download_url": f"{RAW_PROMPTS_BASE}/{p['folder']}/PROMPT.md",
            "metadata_url": f"{RAW_PROMPTS_BASE}/{p['folder']}/metadata.json",
        })
    return {
        "$schema_note": "Catalog manifest of the Prompt Library. One entry per non-archived prompt.",
        "catalog_version": 1,
        "site": SITE_URL,
        "repository": f"https://github.com/{REPO}",
        "prompt_schema": f"{SITE_URL}/schema/prompt.schema.json",
        "count": len(entries),
        "prompts": entries,
    }


def build_html(skills, prompts):
    # strip the (now-unused) emoji field so the page carries no emoji at all
    skills_json = json.dumps(
        [{k: v for k, v in s.items() if k != "emoji"} for s in skills],
        ensure_ascii=False, indent=2,
    )
    prompts_json = json.dumps(prompts, ensure_ascii=False, indent=2)

    categories = sorted(set(s.get("category", "Other") for s in skills))
    cat_buttons = "\n".join(
        f'<button class="filter-btn" data-filter="{c}">{c}</button>'
        for c in categories
    )
    prompt_categories = sorted(set(p.get("category", "Other") for p in prompts))
    prompt_cat_buttons = "\n".join(
        f'<button class="filter-btn p-filter-btn" data-filter="{c}">{c}</button>'
        for c in prompt_categories
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill Marketplace — accilium</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">
<script>
  // Set theme before paint to avoid a flash of the wrong theme
  (function() {{
    try {{
      var t = localStorage.getItem('theme');
      if (t !== 'light' && t !== 'dark') {{
        t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }}
      document.documentElement.setAttribute('data-theme', t);
    }} catch (e) {{}}
  }})();
</script>
<style>
  /* Palette adapted from accilium/aIQ-blog — minimal, neutral, one teal accent.
     LIGHT (near-white, default) + DARK (near-black). Accent flips per theme:
     #00677F (light) / #5EC5D6 (dark). Inter + JetBrains Mono. */
  :root {{
    color-scheme: light;
    /* fonts + shape (theme-independent) */
    --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    --radius: 8px;
    --radius-lg: 12px;
    --max-width: 820px;

    /* ─ LIGHT theme ─ */
    --brand-accent: #00677F;   /* teal */
    --brand-accent-2: #00505f; /* darker teal for gradients/hover */
    --brand-blue: #00677F;     /* action-color alias (kept for existing rules) */
    --brand-dark: #18181b;     /* neutral near-black (code blocks, modal header) */
    --brand-light: #e7f1f3;    /* soft teal tint */
    --accent-soft: rgba(0,103,127,0.12);
    --petrol: #4b6b73;
    --mid-blue: #26262b;
    --sand: #e5e7eb;
    --on-accent: #ffffff;      /* text/icon color on top of the accent */
    --danger: #c0362c;         /* semantic red (advanced / deprecated / high priority) */
    --ring: 0 0 0 4px rgba(0,103,127,0.16);

    --bg: #fdfdfc;
    --surface: #ffffff;
    --surface-2: #f5f5f3;
    --border: #ececec;
    --border-strong: #d4d4d8;
    --text: #18181b;
    --text-muted: #71717a;
    --subtle: #a1a1aa;
    --fg-soft: #27272a;
    --heading: #18181b;
    --scrollbar: #d4d4d8;
    --shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.06);
    --shadow-hover: 0 18px 44px rgba(0,0,0,0.12);

    --header-bg: rgba(253,253,252,0.80);
    --header-bg-scrolled: rgba(253,253,252,0.95);
    --header-text: #18181b;
    --header-muted: #52525b;
    --header-border: #ececec;

    --feature-bg-a: #ffffff;
    --feature-bg-b: #f5f5f3;
    --feature-text: #18181b;
    --feature-muted: #52525b;
    --feature-dot: rgba(0,0,0,0.05);
    --hero-glow: rgba(0,103,127,0.14);
    --glass-bg: rgba(0,103,127,0.05);
    --glass-border: rgba(0,0,0,0.10);
    --chip-active-bg: #00677F;

    --footer-bg: #f5f5f3;
    --footer-text: #52525b;
    --footer-heading: #18181b;
    --footer-border: #ececec;
  }}

  /* ─ DARK theme ─ */
  [data-theme="dark"] {{
    color-scheme: dark;
    --brand-accent: #5EC5D6;   /* bright cyan */
    --brand-accent-2: #3aa9bb;
    --brand-blue: #5EC5D6;
    --brand-dark: #08080a;     /* near-black for code blocks / modal header */
    --brand-light: rgba(94,197,214,0.14);
    --accent-soft: rgba(94,197,214,0.16);
    --petrol: #8fb7be;
    --mid-blue: #131316;
    --sand: #2e2e33;
    --on-accent: #08080a;      /* dark text on the bright cyan accent */
    --danger: #ff8f85;         /* semantic red for dark theme */
    --ring: 0 0 0 4px rgba(94,197,214,0.22);

    --bg: #0b0b0d;
    --surface: #131316;
    --surface-2: #1a1a1e;
    --border: #1f1f23;
    --border-strong: #2e2e33;
    --text: #fafafa;
    --text-muted: #a1a1aa;
    --subtle: #71717a;
    --fg-soft: #e4e4e7;
    --heading: #fafafa;
    --scrollbar: #2e2e33;
    --shadow: 0 1px 2px rgba(0,0,0,0.4), 0 6px 20px rgba(0,0,0,0.34);
    --shadow-hover: 0 22px 50px rgba(0,0,0,0.5);

    --header-bg: rgba(11,11,13,0.80);
    --header-bg-scrolled: rgba(11,11,13,0.94);
    --header-text: #fafafa;
    --header-muted: #a1a1aa;
    --header-border: #1f1f23;

    --feature-bg-a: #0b0b0d;
    --feature-bg-b: #131316;
    --feature-text: #fafafa;
    --feature-muted: #a1a1aa;
    --feature-dot: rgba(255,255,255,0.06);
    --hero-glow: rgba(94,197,214,0.20);
    --glass-bg: rgba(255,255,255,0.05);
    --glass-border: rgba(255,255,255,0.12);
    --chip-active-bg: #5EC5D6;

    --footer-bg: #0b0b0d;
    --footer-text: #a1a1aa;
    --footer-heading: #fafafa;
    --footer-border: #1f1f23;
  }}

  html {{ background: var(--bg); }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}

  body {{
    font-family: var(--font-sans);
    background: var(--bg);
    color: var(--text);
    font-size: 16px;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    font-feature-settings: "cv02","cv03","cv04","cv11";
    transition: background .3s ease, color .3s ease;
  }}
  img {{ max-width: 100%; }}
  ::selection {{ background: rgba(0,103,127,0.18); }}
  /* shared narrow content column (aIQ-blog editorial width) */
  .wrap {{ max-width: var(--max-width); margin: 0 auto; padding: 0 1.5rem; width: 100%; }}
  /* tiny uppercase section eyebrow */
  .eyebrow {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--subtle); font-weight: 600; }}

  /* Custom scrollbar */
  ::-webkit-scrollbar {{ width: 11px; height: 11px; }}
  ::-webkit-scrollbar-thumb {{ background: var(--scrollbar); border-radius: 8px; border: 3px solid var(--bg); }}
  ::-webkit-scrollbar-thumb:hover {{ filter: brightness(0.92); }}

  /* Wide, uppercase display treatment — echoes SBO's extended grotesk headings */
  .display {{ text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }}

  @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  @keyframes floatGlow {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(3%,4%); }} }}

  /* ── HEADER ───────────────────────────────────────── */
  header {{
    position: sticky; top: 0; z-index: 500;
    background: var(--header-bg);
    -webkit-backdrop-filter: saturate(160%) blur(12px);
    backdrop-filter: saturate(160%) blur(12px);
    color: var(--header-text);
    padding: 0 2rem;
    border-bottom: 1px solid var(--header-border);
    transition: background .25s, box-shadow .25s, border-color .25s;
  }}
  header.scrolled {{
    background: var(--header-bg-scrolled);
    box-shadow: 0 8px 30px rgba(0,0,0,0.16);
  }}
  .header-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.9rem 0;
  }}
  .logo {{ display: flex; align-items: center; gap: 0.7rem; text-decoration: none; color: var(--header-text); }}
  .logo-text {{ font-size: 0.95rem; font-weight: 600; letter-spacing: -0.01em; }}

  /* View switcher (Skill Marketplace | Prompt Library) in the logo position */
  .view-switch {{ display: flex; align-items: center; gap: 0.6rem; }}
  .view-btn {{
    background: none; border: none; cursor: pointer; font-family: inherit;
    font-size: 0.95rem; font-weight: 600; letter-spacing: -0.01em;
    color: var(--header-muted); padding: 0.2rem 0; position: relative;
    text-decoration: none; transition: color .2s;
  }}
  .view-btn:hover {{ color: var(--header-text); }}
  .view-btn.active {{ color: var(--header-text); }}
  .view-btn.active::after {{
    content: ''; position: absolute; left: 0; right: 0; bottom: -0.22rem; height: 2px;
    background: var(--brand-accent); border-radius: 2px;
  }}
  .view-sep {{ color: var(--border-strong); font-weight: 400; user-select: none; }}
  header nav {{ display: flex; align-items: center; gap: 0.4rem; }}
  header nav a {{
    color: var(--header-muted);
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
  header nav a.navlink:hover {{ color: var(--header-text); }}
  header nav a.navlink:hover::after {{ transform: scaleX(1); }}
  .theme-toggle {{
    flex-shrink: 0; font-family: inherit;
    font-size: 0.8rem; font-weight: 500; letter-spacing: 0.02em;
    padding: 0.4rem 0.75rem;
    background: transparent; border: 1px solid var(--border-strong);
    color: var(--header-muted); border-radius: 999px; cursor: pointer;
    transition: color .2s, border-color .2s;
  }}
  .theme-toggle:hover {{ color: var(--header-text); border-color: var(--brand-accent); }}
  @media (max-width: 640px) {{
    .header-inner {{ flex-wrap: wrap; gap: 0.3rem 0.5rem; }}
    header nav {{ flex-wrap: wrap; }}
  }}

  /* ── PAGE INTRO (utilitarian, left-aligned) ───────── */
  .page-intro {{ max-width: 1200px; margin: 0 auto; padding: 2.5rem 2rem 0.25rem; }}
  .page-intro h1 {{ font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em; color: var(--heading); margin-bottom: 0.4rem; }}
  .page-intro p {{ color: var(--text-muted); max-width: 68ch; font-size: 0.96rem; }}

  /* ── SEARCH + FILTERS ─────────────────────────────── */
  .controls {{
    max-width: 1200px;
    margin: 1.5rem auto 1.5rem;
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
  #search {{
    width: 100%;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    font-size: 0.95rem; font-family: inherit;
    outline: none; background: var(--surface-2); color: var(--text);
    transition: border-color .2s, box-shadow .2s, background .2s;
  }}
  #search::placeholder {{ color: var(--text-muted); }}
  #search:focus {{ border-color: var(--brand-accent); box-shadow: var(--ring); background: var(--surface); }}
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
    background: var(--chip-active-bg);
    border-color: var(--chip-active-bg);
    color: var(--on-accent);
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
    background: linear-gradient(90deg, var(--brand-accent), var(--brand-accent-2));
    transform: scaleX(0); transform-origin: left; transition: transform .3s ease;
  }}
  .skill-card:hover {{ box-shadow: var(--shadow-hover); border-color: var(--brand-accent); transform: translateY(-4px); }}
  .skill-card:hover::before {{ transform: scaleX(1); }}
  .card-header {{ display: flex; align-items: flex-start; gap: 0.85rem; }}
  .card-emoji {{
    width: 46px; height: 46px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.55rem; line-height: 1;
    background: var(--surface-2);
    border: 1px solid var(--border); border-radius: 12px;
    transition: transform .25s;
  }}
  .skill-card:hover .card-emoji {{ transform: scale(1.06) rotate(-3deg); }}
  .card-meta {{ flex: 1; min-width: 0; }}
  .card-name {{ font-size: 1.08rem; font-weight: 700; color: var(--heading); letter-spacing: -0.01em; }}
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
  .badge-complexity-advanced {{ background: #fbeae8; color: var(--danger); }}
  .badge-status-draft {{ background: #f5efdd; color: #8a6d1f; border: 1px solid #e6d9b5; }}
  .badge-status-in-review {{ background: #eaf0f6; color: var(--mid-blue); border: 1px solid #d3dfea; }}
  .badge-status-deprecated {{ background: #fbeae8; color: var(--danger); border: 1px solid #f2cdc8; }}
  .badge-status-published {{ background: #ecf3ec; color: #2e7d32; border: 1px solid #cfe4d0; }}
  /* dark-theme badge variants */
  [data-theme="dark"] .badge-cat {{ background: rgba(255,255,255,0.09); color: #dfe0f2; }}
  [data-theme="dark"] .badge-harness {{ background: rgba(255,255,255,0.06); color: #a7bcbc; border-color: rgba(255,255,255,0.12); }}
  [data-theme="dark"] .badge-complexity-beginner {{ background: rgba(255,255,255,0.06); color: #a7bcbc; }}
  [data-theme="dark"] .badge-complexity-intermediate {{ background: rgba(221,184,0,0.16); color: #e8c85a; }}
  [data-theme="dark"] .badge-complexity-advanced {{ background: rgba(218,48,37,0.20); color: #ff8f85; }}
  [data-theme="dark"] .badge-status-draft {{ background: rgba(221,184,0,0.16); color: #e8c85a; border-color: rgba(221,184,0,0.3); }}
  [data-theme="dark"] .badge-status-in-review {{ background: rgba(120,160,210,0.16); color: #9fbde6; border-color: rgba(120,160,210,0.3); }}
  [data-theme="dark"] .badge-status-deprecated {{ background: rgba(218,48,37,0.20); color: #ff8f85; border-color: rgba(218,48,37,0.35); }}
  [data-theme="dark"] .badge-status-published {{ background: rgba(53,208,127,0.16); color: #6fd39e; border-color: rgba(53,208,127,0.3); }}
  [data-theme="dark"] .deprecation-banner {{ background: rgba(218,48,37,0.14); border-color: rgba(218,48,37,0.35); color: #ffb3ab; }}
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

  /* ── PROMPT LIST (top-to-bottom rows) ─────────────── */
  .prompt-list {{
    display: flex; flex-direction: column;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
  }}
  .prompt-row {{
    display: flex; align-items: center; gap: 1.25rem;
    padding: 1.05rem 1.4rem;
    border-bottom: 1px solid var(--border);
    cursor: pointer; position: relative;
    transition: background .15s;
    animation: fadeUp .4s ease both;
  }}
  .prompt-row:last-child {{ border-bottom: none; }}
  .prompt-row::before {{
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: linear-gradient(180deg, var(--brand-accent), var(--brand-accent-2));
    transform: scaleY(0); transition: transform .2s ease;
  }}
  .prompt-row:hover {{ background: var(--surface-2); }}
  .prompt-row:hover::before {{ transform: scaleY(1); }}
  .prompt-row.is-deprecated {{ opacity: 0.72; }}
  .prompt-row.is-deprecated:hover {{ opacity: 1; }}
  .prompt-row-main {{ flex: 1; min-width: 0; }}
  .prompt-row-top {{ display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.2rem; }}
  .prompt-row-name {{ font-size: 0.98rem; font-weight: 700; color: var(--heading); letter-spacing: -0.01em; }}
  .prompt-row-desc {{
    font-size: 0.86rem; color: var(--text-muted); line-height: 1.5;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .prompt-row-action {{
    flex-shrink: 0; font-size: 0.82rem; font-weight: 600; color: var(--brand-accent);
    white-space: nowrap;
  }}
  .prompt-row-action .arrow {{ display: inline-block; transition: transform .2s; }}
  .prompt-row:hover .prompt-row-action .arrow {{ transform: translateX(4px); }}
  @media (max-width: 640px) {{
    .prompt-row {{ padding: 0.9rem 1rem; }}
    .prompt-row-action {{ display: none; }}
    .prompt-row-desc {{ white-space: normal; }}
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
  .modal-desc {{ color: var(--text-muted); margin-bottom: 1.25rem; font-size: 0.95rem; }}
  .modal-feedback {{
    display: flex; align-items: center; gap: 0.7rem; flex-wrap: wrap;
    font-size: 0.85rem; color: var(--text-muted);
    margin-bottom: 1.25rem; padding-bottom: 1.1rem;
    border-bottom: 1px solid var(--border);
  }}
  .modal-feedback a {{ color: var(--brand-accent); text-decoration: none; font-weight: 600; }}
  .modal-feedback a:hover {{ text-decoration: underline; }}
  .modal-feedback .fb-spacer {{ flex: 1; }}

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
    background: var(--brand-blue); color: var(--on-accent);
    width: 22px; height: 22px; border-radius: 50%;
    font-size: 0.75rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
  }}
  .code-block {{
    background: var(--brand-dark); color: #e6e6f5;
    border-radius: 8px; padding: 1rem 1.25rem;
    font-family: var(--font-mono); font-size: 0.85rem;
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
  .copy-btn.copied {{ background: var(--brand-accent); color: var(--on-accent); border-color: var(--brand-accent); }}

  .skill-content-area {{
    background: var(--surface-2);
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-family: var(--font-mono); font-size: 0.82rem;
    white-space: pre-wrap; word-break: break-word;
    max-height: 320px; overflow-y: auto;
    margin: 0.75rem 0;
    line-height: 1.6;
    color: var(--text);
  }}

  /* ── PROMPT MODAL: variable form + live preview ───── */
  .var-section-label {{
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em;
    font-weight: 600; color: var(--text-muted); margin: 1.1rem 0 0.6rem;
  }}
  .var-form {{ display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 0.5rem; }}
  .var-field label {{
    font-family: var(--font-mono); font-size: 0.82rem; font-weight: 600;
    color: var(--heading); display: block; margin-bottom: 0.15rem;
  }}
  .var-req {{ color: var(--danger); margin-left: 0.15rem; }}
  .var-hint {{ font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.3rem; }}
  .var-field textarea {{
    width: 100%; border: 1.5px solid var(--border); border-radius: 8px;
    padding: 0.5rem 0.7rem; font-size: 0.88rem; font-family: inherit;
    resize: vertical; min-height: 40px;
    background: var(--surface-2); color: var(--text); outline: none;
    transition: border-color .2s, box-shadow .2s, background .2s;
  }}
  .var-field textarea:focus {{ border-color: var(--brand-accent); box-shadow: var(--ring); background: var(--surface); }}
  mark.var-missing {{
    background: var(--accent-soft); color: var(--brand-accent);
    font-weight: 600; border-radius: 4px; padding: 0 3px;
  }}
  mark.var-filled {{ background: transparent; color: var(--brand-accent); }}
  .prompt-copy-note {{ font-size: 0.8rem; color: var(--danger); min-height: 1.2em; margin-top: 0.4rem; }}
  .download-btn {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: var(--brand-blue); color: var(--on-accent);
    border: none; border-radius: 8px;
    padding: 0.65rem 1.25rem; font-size: 0.9rem; font-weight: 600;
    cursor: pointer; text-decoration: none;
    transition: background .2s;
    margin-top: 0.75rem;
  }}
  .download-btn:hover {{ background: var(--brand-accent-2); }}
  .download-btn-ghost {{
    background: transparent; border: 1.5px solid var(--brand-blue); color: var(--brand-blue);
  }}
  .download-btn-ghost:hover {{ background: var(--brand-light); }}
  .btn-row {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem; }}

  /* ── INSIGHTS ─────────────────────────────────────── */
  .insights-note {{ font-size: 0.82rem; color: var(--text-muted); margin-bottom: 1rem; }}
  .insights-table {{ width: 100%; border-collapse: collapse; font-size: 0.86rem; }}
  .insights-table th, .insights-table td {{
    text-align: left; padding: 0.55rem 0.6rem; border-bottom: 1px solid var(--border);
  }}
  .insights-table th {{ color: var(--text-muted); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; }}
  .insights-table td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .insights-table tr.pri-high td:first-child {{ box-shadow: inset 3px 0 0 var(--brand-accent); }}
  .insights-skill {{ font-weight: 600; color: var(--heading); }}
  .pri-badge {{ font-size: 0.72rem; font-weight: 700; padding: 0.1rem 0.5rem; border-radius: 999px; }}
  .pri-high {{ }}
  .pri-badge.high {{ background: #fbeae8; color: var(--danger); }}
  .pri-badge.med {{ background: #f5efdd; color: #8a6d1f; }}
  .pri-badge.low {{ background: #eef1f0; color: var(--petrol); }}
  [data-theme="dark"] .pri-badge.high {{ background: rgba(218,48,37,0.2); color: #ff8f85; }}
  [data-theme="dark"] .pri-badge.med {{ background: rgba(221,184,0,0.16); color: #e8c85a; }}
  [data-theme="dark"] .pri-badge.low {{ background: rgba(255,255,255,0.06); color: #a7bcbc; }}

  /* ── HOW TO CONTRIBUTE (utilitarian) ──────────────── */
  .contribute-section {{
    border-top: 1px solid var(--border);
    padding: 2.5rem 2rem 3rem;
  }}
  .contribute-inner {{ max-width: 1200px; margin: 0 auto; }}
  .contribute-inner h2 {{ font-size: 1.25rem; font-weight: 700; letter-spacing: -0.01em; color: var(--heading); margin-bottom: 0.4rem; }}
  .contribute-inner > p {{ margin-bottom: 1.25rem; color: var(--text-muted); font-size: 0.96rem; max-width: 68ch; }}
  .contribute-steps {{
    display: flex; flex-direction: column; gap: 0.45rem;
    margin: 0 0 1.25rem; padding: 0; list-style: none;
    counter-reset: step;
  }}
  .c-step {{
    display: flex; align-items: baseline; gap: 0.6rem;
    font-size: 0.92rem; color: var(--text);
  }}
  .c-step::before {{
    counter-increment: step; content: counter(step) ".";
    color: var(--text-muted); font-variant-numeric: tabular-nums;
    font-weight: 600; min-width: 1.2rem;
  }}
  .c-step code {{ color: var(--heading); }}
  .contribute-note {{ font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1rem; }}
  .contribute-links {{ display: flex; gap: 1.25rem; flex-wrap: wrap; font-size: 0.9rem; }}
  .contribute-links a {{ color: var(--brand-accent); text-decoration: none; }}
  .contribute-links a:hover {{ text-decoration: underline; }}

  /* ── FOOTER ───────────────────────────────────────── */
  footer {{
    background: var(--footer-bg);
    color: var(--footer-text);
    border-top: 1px solid var(--footer-border);
    transition: background .3s ease, color .3s ease;
  }}
  .footer-top {{
    max-width: 1200px; margin: 0 auto; padding: 2rem 2rem 1.5rem;
    display: flex; flex-wrap: wrap; gap: 0.5rem 1.5rem; align-items: baseline;
  }}
  .footer-top a {{
    color: var(--footer-text); text-decoration: none;
    font-size: 0.86rem; transition: color .2s;
  }}
  .footer-top a:hover {{ color: var(--brand-accent); }}
  .footer-bottom {{
    border-top: 1px solid var(--footer-border);
    padding: 1rem 2rem; font-size: 0.8rem;
    color: var(--text-muted); max-width: 1200px; margin: 0 auto;
  }}
  .footer-bottom code {{ color: var(--footer-heading); }}

  /* ── RESPONSIVE ───────────────────────────────────── */
  @media (max-width: 600px) {{
    .page-intro {{ padding: 1.75rem 1rem 0.25rem; }}
    .controls {{ margin: 1rem auto; padding: 0 1rem; }}
    .grid-wrap {{ padding: 0 1rem 3rem; }}
    .skills-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header id="site-header">
  <div class="header-inner">
    <div class="view-switch">
      <a class="view-btn active" data-view="skills" href="#skills">Skill Marketplace</a>
      <span class="view-sep">|</span>
      <a class="view-btn" data-view="prompts" href="#prompts">Prompt Library</a>
    </div>
    <nav>
      <a class="navlink" id="nav-browse" href="#skills" onclick="navBrowse(event)">Browse</a>
      <a class="navlink" href="#" onclick="event.preventDefault(); openInsights()">Insights</a>
      <a class="navlink" href="#contribute">Contribute</a>
      <a class="navlink" id="nav-suggest" href="{PROPOSE_URL}" target="_blank">Suggest a skill</a>
      <a class="navlink" href="https://github.com/acc-sebastian/skill-marketplace" target="_blank">GitHub</a>
      <button class="theme-toggle" id="theme-toggle" title="Toggle light / dark mode" aria-label="Toggle light / dark mode"><span id="theme-label">Dark</span></button>
    </nav>
  </div>
</header>

<main id="view-skills">
  <div class="page-intro">
    <h1>Skill library</h1>
    <p>Internal catalog of reusable AI skills for Claude Code and other assistants. Search, open a skill for install instructions, or add your own.</p>
  </div>

  <div class="controls">
    <div class="search-box">
      <div class="search-input-wrap">
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
      <strong>No skills found</strong>
      <p>Try a different search term or category filter.</p>
    </div>
  </div>
</main>

<main id="view-prompts" style="display:none">
  <div class="page-intro">
    <h1>Prompt library</h1>
    <p>Copy-paste prompt templates for recurring tasks. Open a prompt, fill in the variables, and paste the finished prompt into any AI chat — no installation needed.</p>
  </div>

  <div class="controls">
    <div class="search-box">
      <div class="search-input-wrap">
        <input type="text" id="prompt-search" placeholder="Search prompts, tags, descriptions…">
      </div>
      <div class="filter-wrap">
        <span class="filter-label">Category:</span>
        <button class="filter-btn p-filter-btn active" data-filter="all">All</button>
        {prompt_cat_buttons}
      </div>
    </div>
  </div>

  <div class="grid-wrap">
    <p class="result-count" id="prompt-result-count"></p>
    <div class="prompt-list" id="prompts-list"></div>
    <div class="no-results" id="prompt-no-results" style="display:none">
      <strong>No prompts found</strong>
      <p>Try a different search term or category filter.</p>
    </div>
  </div>
</main>

<!-- CONTRIBUTE SECTION -->
<section class="contribute-section" id="contribute">
  <div class="contribute-inner">
    <h2>Add a skill or prompt</h2>
    <p>Once merged to main it appears here within minutes.</p>
    <ol class="contribute-steps">
      <li class="c-step">Fork the GitHub repo</li>
      <li class="c-step">Add <code>metadata.json</code> + <code>SKILL.md</code> under <code>skills/</code> — or <code>metadata.json</code> + <code>PROMPT.md</code> under <code>prompts/</code></li>
      <li class="c-step">Open a pull request</li>
    </ol>
    <p class="contribute-note">No Git? Use the form instead — it opens a pre-filled issue and scaffolds the skill for you.</p>
    <div class="contribute-links">
      <a href="{PROPOSE_URL}" target="_blank">Suggest a skill (form)</a>
      <a href="{PROPOSE_PROMPT_URL}" target="_blank">Suggest a prompt (form)</a>
      <a href="https://github.com/acc-sebastian/skill-marketplace/blob/main/CONTRIBUTING.md" target="_blank">Contributor guide</a>
    </div>
  </div>
</section>

<!-- MODAL -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModalOnOverlay(event)">
  <div class="modal" id="modal">
    <div class="modal-header">
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
      <div class="modal-feedback">
        <span>Was this skill helpful?</span>
        <a id="fb-yes" target="_blank" rel="noopener">Yes</a>
        <a id="fb-no" target="_blank" rel="noopener">No</a>
        <span class="fb-spacer"></span>
        <a id="fb-bug" target="_blank" rel="noopener">Report a problem</a>
      </div>

      <div class="tabs">
        <button class="tab-btn active" onclick="switchTab(event,'claude-code')">Claude Code</button>
        <button class="tab-btn" onclick="switchTab(event,'copilot')">Copilot Studio</button>
        <button class="tab-btn" onclick="switchTab(event,'generic')">Any LLM</button>
        <button class="tab-btn" onclick="switchTab(event,'preview')">Skill Preview</button>
      </div>

      <div class="tab-panel active" id="tab-claude-code">
        <div class="deprecation-banner" style="background:var(--brand-light);border-color:var(--glass-border);color:var(--text)">
          <strong>Recommended:</strong> install the whole marketplace as a plugin — you get <em>every</em> skill and stay auto-updated:
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
          <button class="download-btn" id="btn-download-claude" onclick="downloadSkill()">Download SKILL.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">Copy to clipboard</button>
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
          <button class="download-btn" onclick="downloadSkill()">Download SKILL.md</button>
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
          <button class="download-btn" onclick="downloadSkill()">Download SKILL.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">Copy to clipboard</button>
        </div>
      </div>

      <div class="tab-panel" id="tab-preview">
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.75rem">Full content of <code>SKILL.md</code> — this is what gets installed in your AI harness.</p>
        <div class="skill-content-area" id="modal-skill-content"></div>
        <div class="btn-row">
          <button class="download-btn" onclick="downloadSkill()">Download SKILL.md</button>
          <button class="download-btn download-btn-ghost" onclick="copySkillContent()">Copy to clipboard</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- PROMPT MODAL -->
<div class="modal-overlay" id="prompt-modal-overlay" onclick="closePromptModalOnOverlay(event)">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-title-wrap">
        <div class="modal-title" id="prompt-modal-title"></div>
        <div class="modal-subtitle" id="prompt-modal-subtitle"></div>
      </div>
      <button class="modal-close" onclick="closePromptModal()">✕</button>
    </div>
    <div class="modal-body">
      <div id="prompt-modal-deprecation"></div>
      <div class="modal-tags" id="prompt-modal-tags"></div>
      <p class="modal-desc" id="prompt-modal-desc"></p>
      <div class="modal-feedback">
        <span>Was this prompt helpful?</span>
        <a id="pfb-yes" target="_blank" rel="noopener">Yes</a>
        <a id="pfb-no" target="_blank" rel="noopener">No</a>
        <span class="fb-spacer"></span>
        <a id="pfb-bug" target="_blank" rel="noopener">Report a problem</a>
      </div>

      <div id="prompt-var-block">
        <div class="var-section-label">Fill in the variables</div>
        <div class="var-form" id="prompt-var-form"></div>
      </div>

      <div class="var-section-label">Prompt preview</div>
      <div class="skill-content-area" id="prompt-preview"></div>
      <p class="prompt-copy-note" id="prompt-copy-note"></p>

      <div class="btn-row">
        <button class="download-btn" id="btn-copy-prompt" onclick="copyFilledPrompt(this)">Copy prompt</button>
        <button class="download-btn download-btn-ghost" onclick="copyRawTemplate(this)">Copy raw template</button>
        <button class="download-btn download-btn-ghost" onclick="downloadPrompt()">Download PROMPT.md</button>
      </div>
    </div>
  </div>
</div>

<!-- INSIGHTS OVERLAY -->
<div class="modal-overlay" id="insights-overlay" onclick="if(event.target===this) closeInsights()">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-title-wrap">
        <div class="modal-title">Insights</div>
        <div class="modal-subtitle">Live usage &amp; maintenance priority — fetched from GitHub</div>
      </div>
      <button class="modal-close" onclick="closeInsights()">✕</button>
    </div>
    <div class="modal-body" id="insights-body"></div>
  </div>
</div>

<footer>
  <div class="footer-top">
    <a href="#skills">Browse skills</a>
    <a href="#prompts">Browse prompts</a>
    <a href="{SITE_URL}/catalog.json" target="_blank">Skill catalog API</a>
    <a href="{SITE_URL}/prompt-catalog.json" target="_blank">Prompt catalog API</a>
    <a href="https://github.com/acc-sebastian/skill-marketplace/releases" target="_blank">Releases</a>
    <a href="https://github.com/acc-sebastian/skill-marketplace/blob/main/docs/enterprise-setup.md" target="_blank">Enterprise setup</a>
    <a href="https://github.com/acc-sebastian/skill-marketplace/blob/main/CONTRIBUTING.md" target="_blank">Contributor guide</a>
    <a href="https://github.com/acc-sebastian/skill-marketplace" target="_blank">GitHub</a>
  </div>
  <div class="footer-bottom">
    Auto-generated by <code>scripts/build_site.py</code>
  </div>
</footer>

<script>
const SKILLS = {skills_json};
const PROMPTS = {prompts_json};

let activeFilter = 'all';
let searchQuery = '';
let promptFilter = 'all';
let promptQuery = '';

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
      <div class="card-install-hint">View &amp; install</div>
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

function renderPromptList() {{
  const list = document.getElementById('prompts-list');
  const noRes = document.getElementById('prompt-no-results');
  const count = document.getElementById('prompt-result-count');

  const filtered = PROMPTS.filter(p => {{
    const matchCat = promptFilter === 'all' || p.category === promptFilter;
    const q = promptQuery.toLowerCase();
    const matchSearch = !q ||
      (p.name || '').toLowerCase().includes(q) ||
      (p.description || '').toLowerCase().includes(q) ||
      (p.tags || []).some(t => t.toLowerCase().includes(q)) ||
      (p.category || '').toLowerCase().includes(q) ||
      (p.author || '').toLowerCase().includes(q);
    return matchCat && matchSearch;
  }});

  list.innerHTML = '';
  if (filtered.length === 0) {{
    list.style.display = 'none';
    noRes.style.display = 'block';
    count.textContent = '';
    return;
  }}
  list.style.display = '';
  noRes.style.display = 'none';
  count.textContent = `Showing ${{filtered.length}} of ${{PROMPTS.length}} prompts`;

  filtered.forEach((prompt, idx) => {{
    const row = document.createElement('div');
    const status = prompt.status || 'published';
    row.className = 'prompt-row' + (status === 'deprecated' ? ' is-deprecated' : '');
    row.style.animationDelay = (idx * 0.04) + 's';
    row.onclick = () => openPromptModal(prompt);

    const complexityClass = `badge-complexity-${{prompt.complexity || 'beginner'}}`;
    const complexityLabel = (prompt.complexity || 'beginner').charAt(0).toUpperCase() + (prompt.complexity||'beginner').slice(1);
    const nVars = (prompt.variables || []).length;
    const varBadge = nVars ? `<span class="badge badge-harness">${{nVars}} variable${{nVars > 1 ? 's' : ''}}</span>` : '';

    row.innerHTML = `
      <div class="prompt-row-main">
        <div class="prompt-row-top">
          <span class="prompt-row-name">${{prompt.name || prompt.id}}</span>
          <span class="badge badge-cat">${{prompt.category || 'Other'}}</span>
          <span class="badge ${{complexityClass}}">${{complexityLabel}}</span>
          ${{statusBadgeHtml(status)}}${{varBadge}}
        </div>
        <div class="prompt-row-desc">${{prompt.description || ''}}</div>
      </div>
      <div class="prompt-row-action">Fill &amp; copy <span class="arrow">→</span></div>
    `;
    list.appendChild(row);
  }});
}}

function openModal(skill) {{
  currentSkill = skill;
  document.getElementById('modal-title').textContent = skill.name || skill.id;
  document.getElementById('modal-subtitle').textContent = `${{skill.category}} · v${{skill.version}} · by ${{skill.author}}`;
  document.getElementById('modal-desc').textContent = skill.description || '';
  document.getElementById('modal-skill-content').textContent = skill.skill_content || '(No SKILL.md content found)';

  // Feedback links -> pre-filled GitHub issues (no backend needed)
  const _newIssue = 'https://github.com/acc-sebastian/skill-marketplace/issues/new';
  const _iurl = (title, body, label) =>
    `${{_newIssue}}?title=${{encodeURIComponent(title)}}&body=${{encodeURIComponent(body)}}&labels=${{encodeURIComponent(label)}}`;
  const _sid = skill.id;
  document.getElementById('fb-yes').href = _iurl(`[Feedback] ${{_sid}}: helpful`, `Skill: ${{_sid}}\nHelpful: yes\n\nWhat worked well?`, 'feedback');
  document.getElementById('fb-no').href = _iurl(`[Feedback] ${{_sid}}: not helpful`, `Skill: ${{_sid}}\nHelpful: no\n\nWhat was missing or wrong?`, 'feedback');
  document.getElementById('fb-bug').href = _iurl(`[Bug] ${{_sid}}`, `Skill: ${{_sid}}\nVersion: ${{skill.version}}\n\nDescribe the problem:\n`, 'bug');

  // Deprecation banner
  const depEl = document.getElementById('modal-deprecation');
  if ((skill.status || 'published') === 'deprecated') {{
    const successor = SKILLS.find(s => s.id === skill.deprecated_by);
    const successorLink = successor
      ? `<a href="#" onclick="event.preventDefault(); openModal(SKILLS.find(s => s.id==='${{successor.id}}'))">${{successor.name}}</a>`
      : (skill.deprecated_by || 'a newer skill');
    const sunset = skill.sunset_date ? ` It will be removed on <strong>${{skill.sunset_date}}</strong>.` : '';
    depEl.innerHTML = `<div class="deprecation-banner"><strong>Deprecated.</strong> This skill is superseded by ${{successorLink}}.${{sunset}} Please migrate.</div>`;
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
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') {{ closeModal(); closePromptModal(); closeInsights(); }} }});

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
    btn.textContent = 'Copied';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy'; btn.classList.remove('copied'); }}, 2000);
  }});
}}

// ── PROMPT MODAL (fill variables → live preview → copy) ──
let currentPrompt = null;
let promptVarValues = {{}};

function escapeHtml(s) {{
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}}

function openPromptModal(prompt) {{
  currentPrompt = prompt;
  promptVarValues = {{}};
  document.getElementById('prompt-modal-title').textContent = prompt.name || prompt.id;
  document.getElementById('prompt-modal-subtitle').textContent = `${{prompt.category}} · v${{prompt.version}} · by ${{prompt.author}}`;
  document.getElementById('prompt-modal-desc').textContent = prompt.description || '';

  // Feedback links -> pre-filled GitHub issues (no backend needed)
  const _newIssue = 'https://github.com/acc-sebastian/skill-marketplace/issues/new';
  const _iurl = (title, body, label) =>
    `${{_newIssue}}?title=${{encodeURIComponent(title)}}&body=${{encodeURIComponent(body)}}&labels=${{encodeURIComponent(label)}}`;
  const _pid = prompt.id;
  document.getElementById('pfb-yes').href = _iurl(`[Feedback] ${{_pid}}: helpful`, `Prompt: ${{_pid}}\nHelpful: yes\n\nWhat worked well?`, 'feedback');
  document.getElementById('pfb-no').href = _iurl(`[Feedback] ${{_pid}}: not helpful`, `Prompt: ${{_pid}}\nHelpful: no\n\nWhat was missing or wrong?`, 'feedback');
  document.getElementById('pfb-bug').href = _iurl(`[Bug] ${{_pid}}`, `Prompt: ${{_pid}}\nVersion: ${{prompt.version}}\n\nDescribe the problem:\n`, 'bug');

  // Deprecation banner
  const depEl = document.getElementById('prompt-modal-deprecation');
  if ((prompt.status || 'published') === 'deprecated') {{
    const successor = PROMPTS.find(p => p.id === prompt.deprecated_by);
    const successorLink = successor
      ? `<a href="#" onclick="event.preventDefault(); openPromptModal(PROMPTS.find(p => p.id==='${{successor.id}}'))">${{successor.name}}</a>`
      : (prompt.deprecated_by || 'a newer prompt');
    const sunset = prompt.sunset_date ? ` It will be removed on <strong>${{prompt.sunset_date}}</strong>.` : '';
    depEl.innerHTML = `<div class="deprecation-banner"><strong>Deprecated.</strong> This prompt is superseded by ${{successorLink}}.${{sunset}} Please migrate.</div>`;
  }} else {{
    depEl.innerHTML = '';
  }}

  // Tags
  const tags = document.getElementById('prompt-modal-tags');
  tags.innerHTML = '';
  (prompt.tags || []).forEach(t => {{
    const b = document.createElement('span');
    b.className = 'badge badge-cat';
    b.textContent = '#' + t;
    tags.appendChild(b);
  }});

  // Variable form
  const form = document.getElementById('prompt-var-form');
  form.innerHTML = '';
  const vars = prompt.variables || [];
  document.getElementById('prompt-var-block').style.display = vars.length ? '' : 'none';
  vars.forEach(v => {{
    const field = document.createElement('div');
    field.className = 'var-field';
    const label = document.createElement('label');
    label.textContent = '{{{{' + v.name + '}}}}';
    if (v.required) {{
      const req = document.createElement('span');
      req.className = 'var-req';
      req.textContent = '*';
      label.appendChild(req);
    }}
    const hint = document.createElement('div');
    hint.className = 'var-hint';
    hint.textContent = v.description + (v.example ? ` — e.g. "${{v.example}}"` : '');
    const input = document.createElement('textarea');
    input.rows = 1;
    input.placeholder = v.example || '';
    input.addEventListener('input', () => {{
      promptVarValues[v.name] = input.value;
      updatePromptPreview();
    }});
    field.appendChild(label);
    field.appendChild(hint);
    field.appendChild(input);
    form.appendChild(field);
  }});

  updatePromptPreview();
  document.getElementById('prompt-modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function filledPromptText() {{
  if (!currentPrompt) return '';
  let t = currentPrompt.prompt_template || '';
  (currentPrompt.variables || []).forEach(v => {{
    const val = (promptVarValues[v.name] || '').trim();
    if (val) t = t.split('{{{{' + v.name + '}}}}').join(val);
  }});
  return t;
}}

function updatePromptPreview() {{
  const esc = escapeHtml(filledPromptText());
  document.getElementById('prompt-preview').innerHTML =
    esc.replace(/\\{{\\{{([A-Z0-9_]+)\\}}\\}}/g, '<mark class="var-missing">{{{{$1}}}}</mark>');

  const missing = (currentPrompt.variables || []).filter(v =>
    v.required && !(promptVarValues[v.name] || '').trim());
  document.getElementById('prompt-copy-note').textContent = missing.length
    ? `${{missing.length}} required variable${{missing.length > 1 ? 's' : ''}} not filled yet: ${{missing.map(v => v.name).join(', ')}}`
    : '';
}}

function copyFilledPrompt(btn) {{
  navigator.clipboard.writeText(filledPromptText()).then(() => {{
    const orig = btn.textContent;
    btn.textContent = 'Copied';
    setTimeout(() => {{ btn.textContent = orig; }}, 2000);
  }});
}}

function copyRawTemplate(btn) {{
  if (!currentPrompt) return;
  navigator.clipboard.writeText(currentPrompt.prompt_template || '').then(() => {{
    const orig = btn.textContent;
    btn.textContent = 'Copied';
    setTimeout(() => {{ btn.textContent = orig; }}, 2000);
  }});
}}

function downloadPrompt() {{
  if (!currentPrompt) return;
  const blob = new Blob([currentPrompt.prompt_content || ''], {{type: 'text/markdown'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'PROMPT.md';
  a.click();
  URL.revokeObjectURL(a.href);
}}

function closePromptModal() {{
  document.getElementById('prompt-modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}}
function closePromptModalOnOverlay(e) {{
  if (e.target === document.getElementById('prompt-modal-overlay')) closePromptModal();
}}

// ── INSIGHTS (live, from the public GitHub API) ──
const REPO_API = 'https://api.github.com/repos/acc-sebastian/skill-marketplace';

let insightsFor = 'skills';

function openInsights() {{
  insightsFor = activeView;
  document.getElementById('insights-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
  loadInsights();
}}
function closeInsights() {{
  document.getElementById('insights-overlay').classList.remove('open');
  document.body.style.overflow = '';
}}
function monthsSince(iso) {{
  if (!iso) return 0;
  const d = new Date(iso), n = new Date();
  return Math.max(0, (n.getFullYear()-d.getFullYear())*12 + (n.getMonth()-d.getMonth()));
}}

async function loadInsights() {{
  const isPrompts = insightsFor === 'prompts';
  const ITEMS = isPrompts ? PROMPTS : SKILLS;
  const body = document.getElementById('insights-body');
  body.innerHTML = '<p class="insights-note">Loading live data from GitHub…</p>';
  const downloads = {{}}, feedback = {{}}, bugs = {{}};
  if (!isPrompts) {{
    // Release download counts only exist for skills (tag id@version)
    try {{
      const rels = await fetch(REPO_API + '/releases?per_page=100').then(r => r.json());
      (Array.isArray(rels) ? rels : []).forEach(rel => {{
        const id = (rel.tag_name || '').split('@')[0];
        const dl = (rel.assets || []).reduce((s,a) => s + (a.download_count||0), 0);
        downloads[id] = (downloads[id]||0) + dl;
      }});
    }} catch (e) {{}}
  }}
  try {{
    const iss = await fetch(REPO_API + '/issues?state=all&per_page=100').then(r => r.json());
    (Array.isArray(iss) ? iss : []).forEach(i => {{
      if (i.pull_request) return;
      const labels = (i.labels||[]).map(l => l.name);
      const m = (i.title||'').match(/\\[(?:Feedback|Bug)\\]\\s+([a-z0-9-]+)/i);
      if (!m) return;
      const id = m[1];
      if (labels.includes('bug')) bugs[id] = (bugs[id]||0)+1;
      else if (labels.includes('feedback')) feedback[id] = (feedback[id]||0)+1;
    }});
  }} catch (e) {{}}

  const rows = ITEMS.map(s => {{
    const dl = downloads[s.id]||0, fb = feedback[s.id]||0, bg = bugs[s.id]||0;
    const age = monthsSince(s.last_reviewed);
    const score = dl*1 + bg*40 + age*8 + fb*3;
    return {{s, dl, fb, bg, age, score}};
  }}).sort((a,b) => b.score - a.score);

  const maxScore = Math.max(1, ...rows.map(r => r.score));
  const totalDl = rows.reduce((s,r) => s + r.dl, 0);
  const priOf = r => {{ const rel = r.score / maxScore; return rel >= 0.66 ? 'high' : (rel >= 0.33 ? 'med' : 'low'); }};

  let html = isPrompts
    ? `<p class="insights-note">Live from the GitHub API — feedback/bug issues per prompt (unauthenticated, may be rate-limited). <em>Maintenance priority</em> ranks open bugs × months since last review × feedback volume.</p>`
    : `<p class="insights-note">Live from the GitHub API — release download counts and feedback/bug issues (unauthenticated, may be rate-limited). Total downloads: <strong>${{totalDl}}</strong>. <em>Maintenance priority</em> ranks popularity × open bugs × months since last review.</p>`;
  html += `<div style="overflow-x:auto"><table class="insights-table"><thead><tr><th>${{isPrompts ? 'Prompt' : 'Skill'}}</th>${{isPrompts ? '' : '<th class="num">Downloads</th>'}}<th class="num">Feedback</th><th class="num">Bugs</th><th class="num">Reviewed</th><th>Priority</th></tr></thead><tbody>`;
  rows.forEach(r => {{
    const p = priOf(r);
    html += `<tr class="${{p==='high'?'pri-high':''}}">`
      + `<td><span class="insights-skill">${{r.s.name}}</span></td>`
      + (isPrompts ? '' : `<td class="num">${{r.dl}}</td>`)
      + `<td class="num">${{r.fb}}</td>`
      + `<td class="num">${{r.bg}}</td>`
      + `<td class="num">${{r.age}} mo</td>`
      + `<td><span class="pri-badge ${{p}}">${{p.toUpperCase()}}</span></td></tr>`;
  }});
  html += '</tbody></table></div>';
  body.innerHTML = html;
}}

// Filters (skills)
document.querySelectorAll('.filter-btn:not(.p-filter-btn)').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.filter-btn:not(.p-filter-btn)').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    renderCards();
  }});
}});

// Filters (prompts)
document.querySelectorAll('.p-filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.p-filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    promptFilter = btn.dataset.filter;
    renderPromptList();
  }});
}});

// Search
document.getElementById('search').addEventListener('input', e => {{
  searchQuery = e.target.value;
  renderCards();
}});
document.getElementById('prompt-search').addEventListener('input', e => {{
  promptQuery = e.target.value;
  renderPromptList();
}});

// ── VIEW SWITCHING (Skill Marketplace | Prompt Library) via hash routing ──
let activeView = 'skills';
const PROPOSE_URLS = {{ skills: '{PROPOSE_URL}', prompts: '{PROPOSE_PROMPT_URL}' }};

function applyView(view) {{
  activeView = view;
  document.getElementById('view-skills').style.display = view === 'skills' ? '' : 'none';
  document.getElementById('view-prompts').style.display = view === 'prompts' ? '' : 'none';
  document.querySelectorAll('.view-btn').forEach(b => b.classList.toggle('active', b.dataset.view === view));

  // Nav adapts to the active view
  document.getElementById('nav-browse').href = view === 'prompts' ? '#prompts' : '#skills';
  const suggest = document.getElementById('nav-suggest');
  suggest.textContent = view === 'prompts' ? 'Suggest a prompt' : 'Suggest a skill';
  suggest.href = PROPOSE_URLS[view];
}}

function navBrowse(e) {{
  e.preventDefault();
  const target = activeView === 'prompts' ? '#prompts' : '#skills';
  if (location.hash !== target) location.hash = target; // triggers applyView + scroll
  else window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}
window.addEventListener('hashchange', () => {{
  const h = location.hash.replace('#', '');
  if (h === 'skills' || h === 'prompts') {{
    applyView(h);
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}
}});

// Sticky header shadow on scroll
const _hdr = document.getElementById('site-header');
const _onScroll = () => {{ _hdr.classList.toggle('scrolled', window.scrollY > 8); }};
window.addEventListener('scroll', _onScroll, {{ passive: true }});
_onScroll();

// Light / dark theme toggle (label shows the mode you'll switch to)
function syncThemeLabel() {{
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const el = document.getElementById('theme-label');
  if (el) el.textContent = isDark ? 'Light' : 'Dark';
}}
syncThemeLabel();
document.getElementById('theme-toggle').addEventListener('click', () => {{
  const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try {{ localStorage.setItem('theme', next); }} catch (e) {{}}
  syncThemeLabel();
}});

// Init
renderCards();
renderPromptList();
applyView(location.hash === '#prompts' ? 'prompts' : 'skills');
</script>
</body>
</html>
"""


def main():
    DOCS_DIR.mkdir(exist_ok=True)
    print("Loading skills...")
    skills = load_skills()
    print("Loading prompts...")
    prompts = load_prompts()

    # Archived entries stay in the repo for provenance but leave site + catalogs
    visible = [s for s in skills if s.get("status") != "archived"]
    hidden = len(skills) - len(visible)
    if hidden:
        print(f"  ({hidden} archived skill(s) excluded)")
    visible_prompts = [p for p in prompts if p.get("status") != "archived"]
    hidden_prompts = len(prompts) - len(visible_prompts)
    if hidden_prompts:
        print(f"  ({hidden_prompts} archived prompt(s) excluded)")

    print(f"\nBuilding site with {len(visible)} skills and {len(visible_prompts)} prompts...")
    html = build_html(visible, visible_prompts)
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

    prompt_catalog = build_prompt_catalog(visible_prompts)
    pcat_out = DOCS_DIR / "prompt-catalog.json"
    with open(pcat_out, "w", encoding="utf-8") as f:
        json.dump(prompt_catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Catalog -> {pcat_out} ({prompt_catalog['count']} prompts)")

    # Publish the schemas alongside the site so catalog consumers can validate
    schema_dir = DOCS_DIR / "schema"
    for schema_name in ("skill.schema.json", "prompt.schema.json"):
        schema_src = ROOT / "schema" / schema_name
        if schema_src.exists():
            schema_dir.mkdir(exist_ok=True)
            (schema_dir / schema_name).write_text(
                schema_src.read_text(encoding="utf-8"), encoding="utf-8"
            )
            print(f"Schema  -> {schema_dir / schema_name}")


if __name__ == "__main__":
    main()
