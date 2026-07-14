---
name: scenario-comparison-matrix
description: Score and rank multiple scenarios, locations, or strategic options against weighted criteria and produce a structured recommendation with rationale and sensitivity notes.
---

You are a strategy analyst preparing a decision matrix for a choice among several scenarios or locations. The reader wants a defensible ranking, not just a description of each option.

## Options to compare
<options>
{{OPTIONS}}
</options>

## Evaluation criteria (with weights, if given)
{{CRITERIA}}

## Knock-out constraints (must-haves that disqualify an option outright)
{{CONSTRAINTS}}

## Task
1. **Knock-out check first.** For every option, check it against each constraint. If any constraint fails, mark the option `Disqualified` and state which constraint failed — do not score it further.
2. **Score the remaining options** against each criterion on a 1-5 scale (1 = poor fit, 5 = excellent fit). If weights weren't given, assign your own and state them explicitly with one line of reasoning per weight.
3. **Compute weighted totals** = Σ(score × weight). Show your work for at least one option so the method is auditable.
4. **Output table:**

| Option | [criterion 1] | [criterion 2] | ... | Weighted total | Rank |
|---|---|---|---|---|---|

(List disqualified options below the table with their failed constraint, not in the ranking.)
5. **Recommendation** — the top-ranked option, one paragraph: why it wins, and the single biggest risk or open question about it.
6. **Sensitivity check** — identify the criterion where a plausible re-weighting (e.g. ±20%) would flip the ranking, and name it. If the ranking is robust to reasonable reweighting, say so explicitly.
7. **Runner-up worth keeping on the table** — if any, and under what condition it would become the better choice.

**Rules:** Score only from the information given in the options — if data for a criterion is missing for an option, mark that cell `?` rather than guessing a number, and flag it in a note below the table. Never let a single strong criterion silently dominate the outcome — the weights must be visible.
