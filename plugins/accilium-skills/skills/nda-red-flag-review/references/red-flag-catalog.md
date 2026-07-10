# NDA Red Flag Catalog

The authoritative checklist for the deterministic pass. Walk all 14 categories in
order on every review. Severity guidance assumes your organization's perspective;
where severity depends on your organization's role (discloser vs. recipient), both
readings are given. Bullets labeled **Example house position** are illustrative
defaults — replace them with your organization's actual preferences in
`references/organization-context.md` before relying on this catalog for real
reviews.

Severity shorthand: 🔴 = blocker, 🟡 = negotiate, 🟢 = acceptable.

---

## Contents

1. Parties, entities & affiliates
2. Definition of Confidential Information & carve-outs
3. Permitted purpose & use restrictions
4. Term, survival & return/destruction
5. Standard of care & permitted recipients
6. IP, licenses & residuals
7. Hidden non-NDA obligations (non-compete, non-solicit, exclusivity)
8. Liability, contractual penalties & remedies
9. Governing law, jurisdiction & dispute resolution
10. Listed-company layer: insider law, market soundings, standstill
11. Export control, sanctions & compliance clauses
12. Data protection (GDPR)
13. Assignment, change of control & term of the agreement itself
14. Formalities, language & boilerplate

---

## 1. Parties, entities & affiliates

**Check:** Which legal entities are parties? Does the entity match who will actually
exchange information? Are affiliates/group companies covered — and symmetrically?

**Red flags:**
- 🔴 The named entity of your organization is not the one running the deal
  (obligations land on the wrong company; group companies may not be bound or
  protected).
- 🔴 Counterparty's affiliates may *receive* your organization's information but are
  not themselves *bound* by the obligations (one-directional affiliate clause).
- 🟡 "Affiliates" undefined or defined by a foreign-law concept without a control
  threshold.
- 🟡 One-way NDA where the deal will foreseeably require your organization to
  receive information too (or vice versa) — mismatch between structure and reality.

**Example house position** *(customize in organization-context.md)*: party should be
the operating entity actually involved; your organization's group companies covered
as protected disclosers and bound as recipients only where they actually receive
information. Affiliate definition: control ≥ 50% or the locally applicable
consolidation-accounting threshold (e.g., Austrian UGB/IFRS).

---

## 2. Definition of Confidential Information & carve-outs

**Check:** How is Confidential Information defined (marked-only vs. all-information)?
Are the market-standard exclusions present?

The five standard carve-outs — their **absence is a finding**:
(a) publicly available without breach; (b) already lawfully known to recipient;
(c) independently developed without use of the information; (d) lawfully received
from a third party without confidentiality restriction; (e) disclosure required by
law, court, or authority (with prompt-notice and protective-order cooperation).

**Red flags:**
- 🔴 No carve-outs at all, or (a)–(d) missing.
- 🔴 Your organization as discloser + "marked confidential only" definition, when
  information will flow in meetings, plant visits, or data rooms (oral/visual
  information falls out of protection). Acceptable only with an oral-disclosure
  confirmation mechanism that the team will realistically operate.
- 🟡 Legally-required-disclosure carve-out missing the notice/cooperation duty.
- 🟡 Recipient may keep "one archival copy" without confidentiality survival tied
  to it.
- 🟡 Your organization as recipient + boundless definition ("any information
  disclosed, in any form, whether or not related to the purpose") combined with
  long/perpetual term — operational compliance burden.
- 🟢 Broad definition with clean carve-outs and reasonable term.

**Example house position (as discloser)** *(customize)*: broad "all information
disclosed in connection with the Purpose, in any form" definition, full carve-out
set, burden of proof for carve-outs on the recipient.

---

## 3. Permitted purpose & use restrictions

**Check:** Is the Purpose defined narrowly and accurately? Is use restricted to the
Purpose?

**Red flags:**
- 🔴 No purpose limitation (recipient may use information for anything).
- 🔴 Purpose so broad it licenses competitive use ("for evaluating business
  opportunities between the parties generally").
- 🟡 Purpose description doesn't match the actual deal (creates breach risk for your
  own team when scope evolves).
- 🟡 Reverse-engineering not prohibited where your organization discloses technical
  information or provides samples/equipment — for a technology or manufacturing
  company this is close to 🔴; treat as 🔴 whenever proprietary design data,
  formulations, or manufacturing-process data is in scope.

**Example house position** *(customize)*: Purpose defined per deal, one sentence, no
"including but not limited to". Express no-reverse-engineering clause whenever
hardware, samples, or technical documentation change hands.

---

## 4. Term, survival & return/destruction

**Check:** How long do confidentiality obligations last? What happens to the
information at the end?

**Red flags:**
- 🔴 Your organization as recipient + perpetual/indefinite confidentiality with no
  trade-secret limitation — unmanageable compliance tail. (Perpetual protection
  *only* for information qualifying as trade secrets is 🟡 and often acceptable.)
- 🟡 Your organization as discloser + term under 3 years for technical information;
  under 2 years for anything. Design and process data should get 5+ years or
  trade-secret survival.
- 🟡 No return-or-destruction obligation, or no certification of destruction on
  request.
- 🟡 Return/destruction without the standard IT-carve-out (backup systems, legal
  retention duties) — your organization cannot operationally comply with an
  absolute deletion duty; negotiate the carve-out *with* survival of confidentiality
  for retained copies.
- 🟢 3–5 year term (5+ or trade-secret survival for technical data), destruction
  on request with certification, backup carve-out with continuing confidentiality.

---

## 5. Standard of care & permitted recipients

**Check:** What care standard applies? Who inside the recipient may see the
information?

**Red flags:**
- 🔴 Your organization as recipient + strict/absolute liability standard ("shall
  ensure that no disclosure occurs under any circumstances") with no
  reasonable-care qualifier.
- 🟡 Your organization as discloser + care standard diluted to "same care as own
  information" without the floor "but no less than reasonable care".
- 🟡 Need-to-know limitation missing, or permitted-recipient circle includes
  advisors/financing sources/affiliates without flowing down the obligations and
  without recipient's liability for them.
- 🟡 Your organization as recipient + obligation to have each employee sign
  individual undertakings (operationally heavy — negotiate toward "bound by
  employment or professional duties at least as protective").
- 🟢 Reasonable care, no less than own-information care; need-to-know; recipient
  liable for its representatives.

---

## 6. IP, licenses & residuals

**Check:** Does the NDA stay ownership-neutral, or does it move IP?

**Red flags:**
- 🔴 **Residuals clause** when your organization discloses ("recipient may use
  information retained in unaided memory") — this is a license to absorb your
  organization's know-how. Blocker in any technical or M&A context.
- 🔴 Any assignment of IP, or license grant beyond "use for the Purpose".
- 🔴 Feedback/improvements clause vesting rights in the counterparty for anything
  your organization contributes.
- 🟡 No express "no license granted" clause (add the standard reservation).
- 🟢 Express reservation: all IP stays with discloser, no license except the
  minimum use right for the Purpose.

---

## 7. Hidden non-NDA obligations

**Check:** Does the "NDA" smuggle in obligations that belong in a separate,
consciously negotiated agreement?

**Red flags — all at least 🟡, most 🔴, because they exceed the mandate under which
business teams sign NDAs:**
- 🔴 Non-compete of any kind.
- 🔴 Exclusivity / no-shop binding your organization (in M&A: only with Board
  awareness — route to Legal and deal lead immediately).
- 🟡 Non-solicitation of employees — market-tolerable in M&A if: mutual, ≤ 12–18
  months, limited to personnel *identified through the process*, with
  general-advertisement and unsolicited-application carve-outs. Anything broader: 🔴.
- 🟡 Obligation to negotiate ("the parties shall negotiate in good faith towards a
  definitive agreement") — can create pre-contractual liability exposure depending
  on governing law (e.g., culpa in contrahendo under Austrian/German-derived law);
  prefer express "no obligation to enter into any transaction".
- 🟢 Express no-obligation clause present.

---

## 8. Liability, contractual penalties & remedies

**Check:** Penalty clauses, liability caps/uncaps, indemnities, injunctive relief.

**Red flags:**
- 🔴 Your organization as recipient + contractual penalty (liquidated damages) per
  breach with no fault requirement, or in an amount disproportionate to the deal
  (illustrative screening heuristic — calibrate these numbers to your own risk
  appetite in `organization-context.md`: > EUR 100k per breach, or "per day of
  continuing breach" without cap, is 🔴; anything > EUR 25k or fault-independent at
  least 🟡 — Legal decides the number).
- 🔴 Uncapped indemnification of the counterparty including third-party claims and
  consequential damages.
- 🟡 Penalty without a judicial-reduction acknowledgment where your governing law
  provides one (example: "Richterliches Mäßigungsrecht bleibt unberührt" / § 1336
  ABGB under Austrian law), or drafted as cumulative with full damages without
  clarification.
- 🟡 Your organization as discloser + no injunctive-relief/equitable-remedies
  acknowledgment (damages alone are inadequate for secrecy breaches — add the
  standard clause).
- 🟡 Liability excluded for the counterparty's own representatives' breaches.
- 🟢 Fault-based liability, damages per statute, injunctive-relief acknowledgment,
  no penalty or a moderate mutual one.

---

## 9. Governing law, jurisdiction & dispute resolution

**Check:** Which law, which forum, which language of proceedings?

**Example house position** *(customize for your jurisdiction)*: e.g., for an
Austria-headquartered organization — Austrian law (excluding conflict-of-law rules
and CISG), exclusive jurisdiction of the courts competent for Vienna Inner City — or,
for counterparties outside the EU/EFTA enforcement space, VIAC arbitration (Vienna,
one or three arbitrators, German or English). Substitute your organization's own
preferred law, forum, and arbitration institution here.

**Red flags:**
- 🔴 Law + forum of a jurisdiction where your organization has no enforcement
  experience and which is unpredictable for trade-secret matters, combined with
  high penalty exposure (assess as a package — e.g., an exotic-forum clause plus
  fault-independent penalties).
- 🟡 Any law/forum other than your organization's preferred choice: rate by
  counterparty and enforcement reality — a neighboring, well-understood
  jurisdiction is often 🟢/🟡; a major international commercial-law jurisdiction for
  cross-border M&A is common but should be noted as 🟡; the counterparty's home law
  in a difficult enforcement jurisdiction is 🟡→🔴.
- 🟡 A jurisdiction/state-court combination with no genuine nexus to the deal.
- 🟡 Arbitration with seat/rules unusual for the region, or a proceedings language
  your team can't run.
- 🟢 Your organization's preferred law and forum, or a mutually acceptable
  arbitration institution and seat.

---

## 10. Listed-company layer: insider law, market soundings, standstill

If your organization is publicly listed, NDAs around M&A, capital measures, or
anything price-relevant have a regulatory dimension most counterparties' templates
ignore. Check this category whenever the deal could touch inside information; mark
⚪ N/A for routine supplier NDAs with a one-line justification, or ⚪ N/A entirely if
your organization is not a listed entity.

**Red flags:**
- 🔴 NDA obliges your organization to *disclose* inside information or restricts its
  ability to comply with statutory disclosure duties (e.g., ad-hoc publicity under
  EU MAR Art. 17, or the equivalent regime in your jurisdiction). Statutory-duty
  carve-outs must always prevail.
- 🟡 M&A/financing NDA without an insider-law acknowledgment (recipient aware that
  information may constitute inside information; dealing/tipping prohibitions apply
  under the applicable market-abuse regime; recipient maintains insider-list
  cooperation where required).
- 🟡 Market-sounding context (potential transaction tested with investors) without
  reference to the applicable market-sounding regime (e.g., EU MAR Art. 11).
- 🟡 Standstill demanded *from* your organization (restricting its dealing in
  counterparty securities) that is broader than the insider-law baseline or longer
  than the confidentiality term. A standstill your organization wants *from* a
  counterparty receiving price-relevant information is a house *ask*, not a flag —
  note if absent in a public-M&A context.
- 🟢 Clean statutory-carve-out + insider acknowledgment in price-relevant deals.

---

## 11. Export control, sanctions & compliance clauses

Technical data and certain products or technologies can be dual-use or
sanctions-exposed (e.g., EU restrictive measures, US EAR/OFAC where US-origin
technology or US persons are involved) — the specifics depend on your
organization's industry and products; confirm applicability in
`organization-context.md`. Check this category whenever technical data, drawings,
or equipment/product specifications are in scope; ⚪ N/A only for purely
commercial/financial NDAs.

**Red flags:**
- 🔴 NDA obliges your organization to transfer technical data to named
  recipients/countries regardless of export-control clearance ("recipient may
  share with its affiliates worldwide" with affiliates in embargoed/high-risk
  jurisdictions and no export-control reservation).
- 🔴 Compliance representation your organization cannot operationally give
  ("discloser warrants that no information is subject to any export-control
  regime").
- 🟡 No export-control reservation clause at all when technical data flows —
  add: transfers subject to applicable export-control and sanctions law; recipient
  responsible for its re-transfers.
- 🟡 Broad anti-corruption/compliance warranties with indemnity attached (belongs
  in the main agreement, sized there).
- 🟢 Mutual export-control compliance clause, transfers conditional on clearance.

---

## 12. Data protection (GDPR)

**Check:** Will personal data flow beyond signatories' business contact details
(e.g., HR data in M&A due diligence, employee lists)?

**Red flags:**
- 🟡 Personal data foreseeably in scope, but no GDPR allocation (independent
  controllers vs. processing relationship) and no reference to Art. 26/28
  arrangements where needed; third-country recipients without transfer-mechanism
  language (Art. 44 ff.).
- 🟡 NDA purports to *authorize* processing of personal data ("recipient may use
  all data for the Purpose") without lawful-basis framing.
- 🟢 Business-contact-only data: a short mutual GDPR-compliance sentence suffices;
  ⚪ N/A acceptable with justification if genuinely no personal data flows.

---

## 13. Assignment, change of control & term of the agreement itself

**Red flags:**
- 🟡 Counterparty may assign the NDA (and the information with it) freely —
  especially to a competitor via change of control.
- 🟡 Agreement term (as opposed to survival of confidentiality, § 4) auto-renews
  indefinitely, or termination doesn't end the *exchange* while obligations for
  already-shared information survive (the correct mechanic).
- 🟢 No assignment without written consent; either party may stop disclosing at any
  time; confidentiality survives termination per § 4.

**Example house position** *(customize)*: no assignment without consent;
termination right on change of control to a competitor.

---

## 14. Formalities, language & boilerplate

**Red flags:**
- 🟡 Written-form clause (Schriftformklausel) requiring wet-ink while the process
  runs on e-signature — align clause with reality (qualified e-signature or simple
  e-signature acceptance).
- 🟡 Prevailing-language clause pointing to a language version your organization
  hasn't reviewed; dual-language contract with contradictions between versions.
- 🟡 Entire-agreement clause that would wipe a prior, better NDA or side letters
  the team relies on.
- 🟡 Notices clause with unrealistic mechanics (fax-only; 24-hour deemed receipt).
- 🟢 Standard severability, written-form with e-signature allowance, notices by
  email + registered mail.

---

## Fallback wording bank

Short-form standard positions to adapt into recommendations (mirror the document's
defined terms and language; German equivalents in parentheses):

- **Carve-outs (§ 2):** "Confidential Information does not include information that
  (a) is or becomes publicly available other than through breach of this Agreement;
  (b) was lawfully known to the Recipient prior to disclosure; (c) is independently
  developed by the Recipient without use of the Confidential Information; (d) is
  lawfully obtained from a third party without restriction; or (e) is required to
  be disclosed by law or competent authority, provided the Recipient, to the extent
  legally permitted, promptly notifies the Discloser and cooperates in seeking
  protective measures."
- **No license (§ 6):** "Nothing in this Agreement grants any license or other
  right in or to the Confidential Information or any intellectual property, except
  the limited right to use it for the Purpose."
- **No obligation to transact (§ 7):** "Nothing in this Agreement obliges either
  party to enter into any further agreement or transaction."
- **Injunctive relief (§ 8):** "The parties acknowledge that a breach may cause
  irreparable harm for which damages are an inadequate remedy, and that the
  Discloser is entitled to seek injunctive relief in addition to all other
  remedies."
- **Statutory-duty carve-out (§ 10):** "Nothing in this Agreement restricts either
  party from complying with its statutory obligations, including disclosure
  obligations under applicable capital-markets law."
- **Export control (§ 11):** "Each party shall comply with applicable export
  control and sanctions laws. No Confidential Information shall be transferred or
  re-transferred where such transfer would violate applicable export control or
  sanctions law."
- **Governing law (§ 9)** *(illustrative — Austrian-law example; substitute your
  organization's actual choice of law and forum)*: "This Agreement is governed by
  Austrian law, excluding its conflict-of-law rules and the CISG. Exclusive place
  of jurisdiction is the court competent for Vienna, Inner City." (Gerichtsstands-
  klausel Wien Innere Stadt.)
