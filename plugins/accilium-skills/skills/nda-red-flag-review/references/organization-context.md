# Organization Context — Background for NDA Reviews

Fill this in once for your organization, then keep it updated. It gives the model
the background needed to calibrate severity correctly and to route escalations to
the right place — without it, every "Example house position" in the catalog is only
an illustration, not your organization's actual policy.

## Your organization in a few paragraphs

[Describe: legal form and jurisdiction of incorporation; whether the company is
publicly listed (and where) or privately held; group structure (holding + operating
subsidiaries, or a single entity); industry and what kind of information is
typically at stake in NDAs — technical/manufacturing know-how, financial data,
customer data, software/IP, etc.]

Two kinds of facts drive most house positions: whether your organization is
**listed** (capital-markets law constrains information flows and standstill/insider
topics) and what your organization's **most sensitive information type** is (trade
secrets and technical know-how need different protections than, say, financial
projections or customer lists).

## What this means per catalog category

Work through `references/red-flag-catalog.md` once and note, for each category
marked "Example house position", what your organization's actual preference is.
Typical questions to answer:

- **Entities (§ 1):** Is your organization a holding with operating subsidiaries?
  Which entity actually runs deals and exchanges information? Do NDAs need to
  explicitly cover group companies?
- **Technical/sensitive information (§§ 2, 3, 6):** What kind of information does
  your organization disclose that a counterparty could absorb and reuse (technical
  drawings, source code, customer data, pricing)? This drives how strict the
  carve-out, reverse-engineering, and residuals positions should be.
- **Deal types:** What's the typical NDA mix your organization signs — supplier/
  subcontractor, customer/tender, M&A, technology cooperation? M&A NDAs typically
  activate the listed-company layer (§ 10) and HR-data-in-due-diligence questions
  (§ 12).
- **Listed company (§ 10):** If your organization is listed, which market-abuse /
  disclosure regime applies (e.g. EU MAR, or a non-EU equivalent)? NDAs can never
  override statutory ad-hoc disclosure duties — this is a compliance topic, not a
  negotiation topic.
- **Export control (§ 11):** Does your organization's technology, products, or
  customer base carry export-control or sanctions exposure? If so, your
  organization cannot promise unconditional data flows to "recipient's affiliates
  worldwide" — the export-control reservation protects it from being contractually
  squeezed between the counterparty and the regulator.
- **Governing law / jurisdiction (§ 9) and penalty thresholds (§ 8):** What law and
  forum gives your organization predictability and enforcement confidence? What
  penalty amounts are, in practice, a rubber-stamp vs. an escalation to Legal? These
  numbers are jurisdiction- and risk-appetite-specific — set them explicitly rather
  than relying on the catalog's illustrative figures.

## Escalation map (template — fill in your own routing)

| Finding type | Route to |
|---|---|
| Any 🔴, and all M&A NDAs regardless of findings | [Legal / Legal (Group)] |
| Exclusivity / no-shop / standstill | [Legal **and** deal lead / Board level] |
| Insider-law questions (§ 10) | [Legal / Compliance (capital markets)] |
| Export-control questions (§ 11) | [Export-control officer / Compliance] |
| HR data in due diligence (§ 12) | [Legal + Data Protection] |

## Tone for reports

State who your organization's readers are (e.g., "finance and legal readers are
senior and time-poor") and any house style. As a default: factual, quantified, free
of hedging filler; one strong recommendation per finding; match the language of the
NDA unless told otherwise. Never "I think" / "it seems" — either the clause says it
(quote it) or the point is ❓ UNCLEAR.
