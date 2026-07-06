# Skill Pull Request

## Was ändert dieser PR?

<!-- Kurzbeschreibung: neue Skill / Update / Deprecation / Infrastruktur -->

## Checkliste

### Für neue Skills
- [ ] Ordnername ist kebab-case und identisch mit `id` in `metadata.json`
- [ ] `metadata.json` validiert gegen `schema/skill.schema.json` (`python scripts/validate_skills.py`)
- [ ] `owner` ist gesetzt und in `.github/CODEOWNERS` eingetragen
- [ ] `status` ist korrekt (`draft` oder `in-review` für neue Skills)
- [ ] `example_input` ist ein realistisches, testbares Beispiel
- [ ] `SKILL.md` hat YAML-Frontmatter und folgt der Struktur aus CONTRIBUTING.md
- [ ] Keine vertraulichen oder personenbezogenen Daten im Inhalt

### Für Skill-Updates
- [ ] `version` gebumpt (SemVer: Breaking Change am Prompt → MAJOR)
- [ ] `changelog` um Eintrag ergänzt (neueste Version zuerst)
- [ ] `last_reviewed` aktualisiert

### Für Deprecations
- [ ] `status: deprecated` gesetzt
- [ ] `deprecated_by` zeigt auf existierende Nachfolge-Skill
- [ ] `sunset_date` gesetzt

## Bezug

<!-- Falls dieser PR aus einem Skill-Vorschlag entstand: Closes #<issue-nummer> -->
