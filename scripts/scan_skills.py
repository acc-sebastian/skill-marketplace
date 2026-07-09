#!/usr/bin/env python3
"""
Scan skills for sensitive data and prompt-injection patterns (Roadmap Phase 4).

Runs in CI (validate.yml). Two severities:
  - SECRET  (private keys, cloud keys, tokens)      -> FAIL the build (exit 1)
  - WARNING (emails, phone numbers, injection cues) -> print, do NOT fail

Regex/heuristic only — no network calls, so it's deterministic in CI.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "plugins" / "sbo-skills" / "skills"
PROMPTS_DIR = ROOT / "prompts"

# High-confidence secrets -> hard fail
SECRET_PATTERNS = [
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9-]{20,}\b")),
    ("Generic assigned secret", re.compile(
        r"(?i)(?:api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"][A-Za-z0-9/+_-]{16,}['\"]")),
]

# Lower-confidence PII / injection -> warn only
WARNING_PATTERNS = [
    ("Email address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("Phone number", re.compile(r"(?<!\d)(?:\+\d{1,3}[ .-]?)?(?:\(\d{2,4}\)[ .-]?)?\d{3,4}[ .-]\d{3,4}(?:[ .-]\d{2,4})?(?!\d)")),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")),
    ("Prompt injection cue", re.compile(
        r"(?i)\b(ignore (?:all )?previous instructions|disregard (?:the )?(?:above|previous)|"
        r"forget (?:everything|all) (?:above|previous)|system prompt:|you are now|reveal your (?:system )?prompt)\b")),
]


def scan_text(text):
    secrets, warnings = [], []
    for label, pat in SECRET_PATTERNS:
        if pat.search(text):
            secrets.append(label)
    for label, pat in WARNING_PATTERNS:
        if pat.search(text):
            warnings.append(label)
    return secrets, warnings


def main():
    n_secret = 0
    n_warn = 0
    targets = [(SKILLS_DIR, "plugins/sbo-skills/skills", ("SKILL.md", "metadata.json")),
               (PROMPTS_DIR, "prompts", ("PROMPT.md", "metadata.json"))]
    for base_dir, rel, fnames in targets:
        if not base_dir.exists():
            continue
        for d in sorted(base_dir.iterdir()):
            if not d.is_dir():
                continue
            for fname in fnames:
                f = d / fname
                if not f.exists():
                    continue
                secrets, warnings = scan_text(f.read_text(encoding="utf-8"))
                for s in secrets:
                    print(f"::error file={rel}/{d.name}/{fname}::SECRET — {s}")
                    n_secret += 1
                for w in warnings:
                    print(f"  WARN  {rel}/{d.name}/{fname}: possible {w}")
                    n_warn += 1

    print(f"\nScan complete: {n_secret} secret(s), {n_warn} warning(s).")
    if n_secret:
        print("FAIL — remove hard-coded secrets before merging.")
        sys.exit(1)
    print("OK — no hard-coded secrets. (Warnings are advisory.)")


if __name__ == "__main__":
    main()
