---
name: nda-red-flag-review
description: >
  Screen NDAs (non-disclosure / confidentiality agreements) for legal and commercial
  red flags and produce a structured, clause-referenced review report with severity
  ratings and negotiation recommendations. Use this skill whenever the user uploads or
  pastes an NDA, confidentiality agreement, Geheimhaltungsvereinbarung,
  Vertraulichkeitsvereinbarung, or CDA and asks to review, check, screen, analyze, or
  red-flag it — and also when they ask broader questions like "is this NDA okay to
  sign?", "was ist problematisch an diesem NDA?", "check this confidentiality
  agreement", or "prepare NDA feedback for the counterparty". Also use it for
  comparing an NDA against the organization's standard positions or drafting a
  markup/negotiation email based on a review.
license: Internal use. Not legal advice.
---

# NDA Red Flag Review

Pre-screen NDAs before they go to Legal. The output is a structured review report
that tells the business owner and Legal, at a glance: what is dangerous (🔴), what
should be negotiated (🟡), what is fine (🟢), and what is *missing*.

> **Before first use:** this skill ships with a generic, industry-neutral red-flag
> catalog. Fill in `references/organization-context.md` with your own organization's
> legal preferences (governing law, jurisdiction, penalty thresholds, listed-company
> status, export-control exposure, escalation routing) — every "Example house
> position" in the catalog is illustrative until you do.

**This skill produces a screening aid, not legal advice.** Every report must carry
the disclaimer from the template and route the final decision to Legal. Never tell
the user an NDA is "safe to sign" — the strongest permitted positive statement is
"no red flags found against the catalog; route to Legal for confirmation."

## Why this skill works the way it does

Ad-hoc NDA reviews miss things because attention follows the loudest clause. This
skill prevents that with a **deterministic checklist pass**: all 14 catalog
categories are checked on every review, and each one gets an explicit status. A
category is never silently skipped — "not present" is itself a finding (a missing
carve-out list is one of the most common and most serious NDA defects). The
generative layer is reserved for what genuinely needs judgment: interpreting clause
language, rating severity in context, and drafting negotiation positions.

## Workflow

### Step 1 — Ingest the document

If the NDA is a file (docx/pdf), run the extraction script so every paragraph gets
a stable citation index:

```bash
python scripts/extract_nda_text.py <path-to-nda> > /tmp/nda_extracted.txt
```

The script emits numbered paragraphs (`[¶012]`). Use these markers in the report so
every finding is traceable. If the NDA is pasted as text, number the clauses
yourself using the document's own clause numbering where available.

If the document is a scan (the script will say so), rasterize and read it page by
page instead — see the pdf-reading skill if available.

### Step 2 — Establish deal context

The severity of many flags depends on which side your organization is on. Determine
from the document and conversation; ask the user **only** if it cannot be inferred:

1. **Your organization's role**: discloser, recipient, or mutual? (Check the parties
   clause and the definition of Confidential Information.)
2. **Deal type**: M&A / due diligence, supplier/procurement, customer/tender, JV or
   technology cooperation, other?
3. **Which entity of your organization** is named as party? (Wrong-entity flags, see
   catalog § 1.)

Record the context at the top of the report. If the user answers or the document
settles it, do not re-ask.

### Step 3 — Deterministic checklist pass

Read `references/red-flag-catalog.md` (the authoritative catalog: 14 categories,
severity rules, and example house positions inline). Walk **all 14 categories in
order**. For each category, record exactly one status:

| Status | Meaning |
|---|---|
| 🔴 RED | Blocker-level finding — do not sign without change |
| 🟡 AMBER | Negotiate — deviates from the organization's house position or market standard |
| 🟢 GREEN | Checked, acceptable |
| ⚪ N/A | Genuinely not applicable to this deal type (justify in one line) |
| ❓ UNCLEAR | Language is ambiguous — flag for Legal with the quote |

A missing protective clause (e.g., no standard carve-outs, no injunctive-relief
language when your organization discloses) is scored in the relevant category as 🔴
or 🟡 per the catalog — absence is a finding, not an N/A.

Severity calibration depends on your organization's specific situation (listed-
company status, export-control exposure, governing-law preference, industry). The
catalog ships with **illustrative example house positions** — replace them with your
organization's actual preferences in `references/organization-context.md` before
relying on this skill for real reviews. Read that file the first time you use this
skill in a conversation, and whenever a finding needs the underlying rationale.

### Step 4 — Evidence discipline

Every 🔴 / 🟡 / ❓ finding must contain:

1. **Location**: clause number and `[¶NNN]` marker.
2. **Quote**: the shortest decisive excerpt (≤ 25 words) of the clause.
3. **Issue**: what the clause does and why it hurts your organization *in this deal
   context*.
4. **Recommendation**: the concrete change — use the fallback wording from the
   catalog where one exists, adapted to the document's language and defined terms.

No finding without a quote. If you cannot quote it, it is ❓ UNCLEAR, not 🔴.

### Step 5 — Generate the report

Fill `templates/review-report-template.md` exactly — do not invent your own report
structure. Key rules:

- **Language**: write the report in the language of the NDA (German NDA → German
  report), unless the user asks otherwise. Keep the traffic-light table structure
  identical in both languages.
- **Executive summary**: max 5 sentences. Lead with the sign/negotiate/stop
  recommendation and the count of findings (e.g., "2 🔴, 4 🟡").
- **Traffic-light table**: all 14 categories, always, in catalog order — including
  the 🟢 and ⚪ ones. The complete table is what makes the review auditable.
- **Detailed findings**: only 🔴, 🟡 and ❓, ordered by severity then clause order.
- **Missing-clause section**: list protective clauses the organization would want
  that are absent, even when already scored above — Legal reads this section first.
- **Disclaimer**: verbatim from the template. Never remove or soften it.

Save the report as a Markdown file and share it. A worked example is in
`sample-output/sample-review-report.md` — match its tone and depth: precise,
unemotional, no filler.

### Step 6 — Offer follow-ups (do not auto-execute)

After delivering the report, offer — but do not perform unasked:

- a **negotiation email** to the counterparty (use the 🟡/🔴 recommendations;
  template hints in `templates/negotiation-email-snippets.md`),
- a **markup list** formatted for Legal (clause → current wording → proposed wording),
- a **comparison** against a second NDA version if the user has one.

## Hard rules

- Never state or imply that signing is safe or legally compliant. Screening ≠ Freigabe.
- Never fabricate clause numbers, quotes, or paragraph markers. If extraction
  failed for a section, say so in the report under "Review limitations".
- If the document is not an NDA (e.g., a full services agreement with embedded
  confidentiality terms), say so, review only the confidentiality-relevant parts
  against the catalog, and recommend a full contract review by Legal.
- If personal data of identifiable individuals appears in the NDA beyond the
  signatories' business contact details, do not reproduce it in the report.
- Confidentiality of the review itself: the NDA and the report are internal to your
  organization. Do not summarize deal details beyond what the report requires.

## Bundled resources

| File | When to read |
|---|---|
| `references/red-flag-catalog.md` | Every review — Step 3. The authoritative checklist. |
| `references/organization-context.md` | First use per conversation; when a house-position rationale is needed. Fill this in before relying on the skill for real reviews. |
| `templates/review-report-template.md` | Every review — Step 5. |
| `templates/negotiation-email-snippets.md` | Only when the user wants the follow-up email. |
| `sample-output/sample-review-report.md` | When calibrating tone/depth of the report. |
| `scripts/extract_nda_text.py` | Step 1, for file inputs. |
