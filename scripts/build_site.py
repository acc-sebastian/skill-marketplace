#!/usr/bin/env python3
"""
Build the Skill Marketplace static site.

Reads:  skills/*/metadata.json + skills/*/skill.md
Writes: docs/index.html

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
<style>
  :root {{
    --brand-dark: #00225a;
    --brand-blue: #0051a0;
    --brand-accent: #0099cc;
    --brand-light: #e8f4fb;
    --bg: #f7f9fc;
    --surface: #ffffff;
    --border: #dde3ec;
    --text: #1a2233;
    --text-muted: #5a6a82;
    --radius: 12px;
    --shadow: 0 2px 12px rgba(0,34,90,0.10);
    --shadow-hover: 0 6px 28px rgba(0,34,90,0.18);
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }}

  /* ── HEADER ───────────────────────────────────────── */
  header {{
    background: linear-gradient(135deg, var(--brand-dark) 0%, var(--brand-blue) 100%);
    color: #fff;
    padding: 0 2rem;
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
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 800;
  }}
  .logo-text {{ font-size: 1.1rem; font-weight: 700; letter-spacing: 0.02em; }}
  .logo-sub {{ font-size: 0.75rem; opacity: 0.75; display: block; }}
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
    background: linear-gradient(135deg, var(--brand-dark) 0%, var(--brand-blue) 100%);
    color: #fff;
    text-align: center;
    padding: 4rem 2rem 5rem;
  }}
  .hero h1 {{ font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight: 800; margin-bottom: 0.75rem; }}
  .hero p {{ font-size: 1.1rem; opacity: 0.85; max-width: 560px; margin: 0 auto 2rem; }}
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
    background: linear-gradient(90deg, var(--brand-accent), var(--brand-blue));
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
  .badge-cat {{ background: var(--brand-light); color: var(--brand-blue); }}
  .badge-harness {{ background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }}
  .badge-complexity-beginner {{ background: #f0fdf4; color: #16a34a; }}
  .badge-complexity-intermediate {{ background: #fffbeb; color: #d97706; }}
  .badge-complexity-advanced {{ background: #fef2f2; color: #dc2626; }}
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
    background: linear-gradient(135deg, var(--brand-dark), var(--brand-blue));
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
    background: #0f172a; color: #e2e8f0;
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
  .copy-btn.copied {{ background: #16a34a; color: #fff; border-color: #16a34a; }}

  .skill-content-area {{
    background: #f8fafc;
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
  .contribute-inner h2 {{ font-size: 1.8rem; margin-bottom: 0.75rem; }}
  .contribute-inner p {{ opacity: 0.8; margin-bottom: 1.5rem; }}
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

  /* ── FOOTER ───────────────────────────────────────── */
  footer {{
    background: #080f1e;
    color: rgba(255,255,255,0.5);
    text-align: center;
    padding: 1.5rem;
    font-size: 0.82rem;
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
      <a href="https://github.com/acc-sebastian/skill-marketplace" target="_blank">GitHub ↗</a>
    </nav>
  </div>
</header>

<div class="hero">
  <h1>AI Skills, Ready to Deploy</h1>
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
    <a class="cta-btn" href="https://github.com/acc-sebastian/skill-marketplace/blob/main/CONTRIBUTING.md" target="_blank">
      📖 Read the Contributor Guide
    </a>
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
    card.className = 'skill-card';
    card.onclick = () => openModal(skill);

    const harnessBadges = (skill.harnesses || []).slice(0,2).map(h => {{
      const labels = {{'claude-code':'Claude Code','copilot-studio':'Copilot Studio','generic':'Any LLM'}};
      return `<span class="badge badge-harness">${{labels[h] || h}}</span>`;
    }}).join('');

    const complexityClass = `badge-complexity-${{skill.complexity || 'beginner'}}`;
    const complexityLabel = (skill.complexity || 'beginner').charAt(0).toUpperCase() + (skill.complexity||'beginner').slice(1);

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
        ${{harnessBadges}}
      </div>
      <div class="card-install-hint">Click to install →</div>
    `;
    grid.appendChild(card);
  }});
}}

function openModal(skill) {{
  currentSkill = skill;
  document.getElementById('modal-emoji').textContent = skill.emoji || '🔧';
  document.getElementById('modal-title').textContent = skill.name || skill.id;
  document.getElementById('modal-subtitle').textContent = `${{skill.category}} · v${{skill.version}} · by ${{skill.author}}`;
  document.getElementById('modal-desc').textContent = skill.description || '';
  document.getElementById('modal-skill-content').textContent = skill.skill_content || '(No skill.md content found)';

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
    print(f"\nBuilding site with {len(skills)} skills...")
    html = build_html(skills)
    out = DOCS_DIR / "index.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done! -> {out}")
    size_kb = out.stat().st_size / 1024
    print(f"Site size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
