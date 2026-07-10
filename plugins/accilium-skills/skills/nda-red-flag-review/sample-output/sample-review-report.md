# NDA Red Flag Review — Meridian Drilling Systems Inc. / Projekt "Precision Bore"

**Dokument:** Meridian_Mutual_NDA_Draft_v2.docx (Entwurf vom 14.05.2026)
**Vertragsparteien:** Solstice Precision Manufacturing GmbH ↔ Meridian Drilling Systems Inc. (Delaware)
**Rolle unserer Organisation:** Mutual, überwiegend Discloser (Fertigungszeichnungen, Werkstoffdaten) · **Deal-Typ:** Technologie-Kooperation / Subcontracting
**Review-Datum:** 2026-07-09 · **Reviewer:** Claude (NDA Red Flag Review Skill) — Vorprüfung, keine Rechtsberatung

*(Fiktives Kalibrierungsbeispiel — beide Parteien und das Dokument sind erfunden.)*

---

## 1. Executive Summary

Nicht unterzeichnen ohne Änderung der Punkte F-01 (Residuals-Klausel) und F-02
(Rechtswahl Texas mit fault-unabhängiger Vertragsstrafe). Insgesamt 2 🔴, 4 🟡 und
1 ❓ Finding. Der Entwurf erlaubt Meridian die Nutzung von "in unaided memory"
verbliebenem Know-how unserer Organisation — für eine Kooperation mit
Fertigungszeichnungen ein Ausschlusskriterium. Zusätzlich fehlt eine
Exportkontrollklausel, obwohl technische Daten mit US-Nexus fließen. Die Carve-outs
und die Zweckbindung sind sauber.

---

## 2. Ampel-Übersicht (alle 14 Kategorien)

| # | Kategorie | Status | Kurzbefund |
|---|---|---|---|
| 1 | Parteien, Entities & Affiliates | 🟡 | Meridian-Affiliates empfangen, sind aber nicht gebunden (F-04) |
| 2 | Definition CI & Carve-outs | 🟢 | Breite Definition, alle 5 Standard-Carve-outs vorhanden (Ziff. 1.2) |
| 3 | Zweckbindung & Nutzungsbeschränkung | 🟢 | Enger Purpose (Ziff. 2.1); Reverse-Engineering-Verbot in Ziff. 2.3 |
| 4 | Laufzeit, Survival & Rückgabe/Löschung | 🟡 | Nur 2 Jahre Survival für technische Daten (F-05) |
| 5 | Sorgfaltsmaßstab & zulässige Empfänger | 🟢 | Reasonable care + need-to-know (Ziff. 3) |
| 6 | IP, Lizenzen & Residuals | 🔴 | Residuals-Klausel Ziff. 4.3 (F-01) |
| 7 | Versteckte Nicht-NDA-Pflichten | 🟢 | No-obligation-Klausel vorhanden (Ziff. 8.2) |
| 8 | Haftung, Vertragsstrafen & Remedies | 🔴 | USD 250k Vertragsstrafe je Verstoß, verschuldensunabhängig (F-02) |
| 9 | Rechtswahl, Gerichtsstand & Streitbeilegung | 🟡 | Texas law, Gerichte Harris County (F-03) |
| 10 | Börsenotierung / Insiderrecht | ⚪ | Keine kursrelevante Information im Scope (Subcontracting) |
| 11 | Exportkontrolle, Sanktionen & Compliance | 🟡 | Keine Exportkontrollklausel trotz techn. Daten mit US-Nexus (F-06) |
| 12 | Datenschutz (DSGVO) | ⚪ | Nur Business-Kontaktdaten; kurze Compliance-Klausel Ziff. 9.4 |
| 13 | Abtretung, Change of Control | 🟢 | Abtretung nur mit Zustimmung (Ziff. 10.1) |
| 14 | Formvorschriften, Sprache & Boilerplate | ❓ | Prevailing-Language-Klausel verweist auf "Spanish version" (F-07) |

---

## 3. Findings im Detail

### 🔴 F-01 — Residuals-Klausel (Ziff. 4.3, [¶041])

> "Recipient may use Residuals, meaning information retained in the unaided memory of its personnel, for any purpose."

**Problem:** Die Klausel lizenziert faktisch die Aufnahme unseres Know-hows in
Meridians eigene Entwicklung — Werkstoffparameter und Fertigungsschritte sind genau
das, was Ingenieure "in unaided memory" behalten. Sie hebelt Zweckbindung (Ziff. 2)
und Reverse-Engineering-Verbot (Ziff. 2.3) aus.

**Empfehlung:** Ersatzlose Streichung von Ziff. 4.3. Falls Meridian auf einer
Regelung besteht: ausdrückliche Klarstellung, dass keine Nutzung außerhalb des
Purpose zulässig ist ("no license granted"-Formulierung, Katalog § 6).

### 🔴 F-02 — Verschuldensunabhängige Vertragsstrafe USD 250.000 (Ziff. 6.2, [¶058])

> "…liquidated damages of USD 250,000 per occurrence, without proof of fault or actual damage."

**Problem:** Höhe und Verschuldensunabhängigkeit sind für ein Subcontracting-NDA
unverhältnismäßig; kombiniert mit texanischem Recht (F-03) entfällt ein
richterliches Mäßigungsrecht, wie es unter österreichischem Recht (§ 1336 ABGB)
bestünde. "Per occurrence" ohne Cap schafft unkalkulierbare Exponierung.

**Empfehlung:** Streichung oder Umbau auf verschuldensabhängige, gegenseitige
Vertragsstrafe in moderater Höhe mit Gesamtcap; gesetzliche Schadenersatzansprüche
bleiben unberührt. Finale Höhe: Entscheidung Legal.

### 🟡 F-03 — Rechtswahl Texas, Gerichtsstand Harris County (Ziff. 11.1, [¶072])

> "…governed by the laws of the State of Texas; exclusive venue in the courts of Harris County."

**Problem:** Durchsetzung unserer Geheimnisschutzinteressen vor texanischen State
Courts ist teuer und unvorhersehbar; in Kombination mit F-02 erhöht die Klausel das
Gesamtrisiko des Pakets.

**Empfehlung:** Unser bevorzugtes Recht und Gerichtsstand (siehe
organization-context.md) — in diesem Beispiel: österreichisches Recht,
Gerichtsstand Wien Innere Stadt; als Kompromiss für die US-Gegenpartei: VIAC- oder
ICC-Schiedsverfahren, Sitz Wien oder Zürich, Verfahrenssprache Englisch
(Fallback-Formulierung Katalog § 9).

### 🟡 F-04 — Einseitige Affiliate-Klausel (Ziff. 1.4, [¶009])

> "Recipient may disclose Confidential Information to its Affiliates."

**Problem:** Meridian-Affiliates dürfen empfangen, werden aber nicht selbst
verpflichtet; Meridian haftet nicht ausdrücklich für deren Verstöße.

**Empfehlung:** Weitergabe an Affiliates nur bei Bindung an gleichwertige
Pflichten und voller Haftung des Recipient für Affiliate-Verstöße.

### 🟡 F-05 — Survival nur 2 Jahre für technische Daten (Ziff. 7.1, [¶064])

> "The obligations under this Agreement expire two (2) years after the Effective Date."

**Problem:** Fertigungszeichnungen und Werkstoffdaten haben eine deutlich längere
wirtschaftliche Lebensdauer; nach Ablauf wäre Meridian frei.

**Empfehlung:** 5 Jahre ab letzter Offenlegung; für Geschäftsgeheimnisse iSd
Trade-Secrets-Recht Fortgeltung, solange die Geheimniseigenschaft besteht.

### 🟡 F-06 — Fehlende Exportkontrollklausel (fehlt; vgl. Ziff. 9)

**Problem:** Technische Daten mit möglichem US-Nexus fließen in beide Richtungen;
ohne Exportkontrollvorbehalt können wir vertraglich zu Transfers verpflichtet
werden, die regulatorisch unzulässig sind.

**Empfehlung:** Aufnahme der gegenseitigen Exportkontrollklausel (Fallback-Wortlaut
Katalog § 11); Weitergaben stehen unter dem Vorbehalt exportkontrollrechtlicher
Zulässigkeit.

### ❓ F-07 — Prevailing-Language-Klausel verweist auf spanische Fassung (Ziff. 12.3, [¶081])

> "In case of discrepancies, the Spanish language version shall prevail."

**Problem:** Es liegt nur die englische Fassung vor; eine spanische Fassung ist
nicht Teil des übermittelten Entwurfs — vermutlich ein Template-Überbleibsel.
Rechtsfolge unklar.

**Empfehlung:** Klausel streichen oder auf die englische Fassung umstellen;
Gegenseite um Klärung bitten, ob eine spanische Fassung existiert.

---

## 4. Fehlende Schutzklauseln

- [ ] **Exportkontrollvorbehalt** — fehlt vollständig (F-06); Fallback-Wortlaut Katalog § 11.
- [ ] **Injunctive-Relief-Anerkenntnis** — der Entwurf regelt nur liquidated damages;
      als überwiegender Discloser Anerkenntnis einstweiligen Rechtsschutzes ergänzen
      (Katalog § 8).
- [ ] **Löschzertifikat** — Rückgabe/Löschung (Ziff. 7.2) ohne Bestätigungspflicht;
      schriftliche Löschbestätigung auf Verlangen ergänzen.

---

## 5. Review-Limitationen

Annex A ("Technical Scope") wurde im Entwurf referenziert ([¶005]), liegt aber
nicht vor — die Bewertung von Ziff. 2 (Zweckbindung) steht unter diesem Vorbehalt.

---

## 6. Nächste Schritte

1. F-01 und F-02 an Legal — 🔴-Findings sind Unterzeichnungsblocker.
2. F-06 parallel an den Exportkontrollbeauftragten (Eskalationsmatrix § 11).
3. Auf Wunsch: Verhandlungs-E-Mail an Meridian auf Basis F-01 bis F-07 sowie
   Markup-Liste für Legal.

---

> **Disclaimer:** Diese Prüfung ist eine automatisierte Vorab-Sichtung anhand des
> internen Red-Flag-Katalogs und ersetzt keine rechtliche Prüfung. Sie stellt keine
> Rechtsberatung dar. Die Freigabe zur Unterzeichnung erfolgt ausschließlich durch
> Legal. / This review is an automated pre-screening against the internal red flag
> catalog and does not replace legal review or constitute legal advice. Signing
> approval rests exclusively with Legal.
