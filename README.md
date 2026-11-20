# fitpick

A zero-dependency CLI that helps fitness-conscious buyers decide whether a
food is worth buying — and what to eat it as.

## Motivation

When you are trying to eat healthy (or hit a protein target), every trip to
the store becomes a math problem: is this protein bar worth ¥8? Should I treat
this as a snack or a cheat meal? Existing apps like MyFitnessPal are *food
databases* — they tell you the numbers, but they do not tell you **what to do
with them**.

`fitpick` flips that. You type in the numbers from the nutrition label, and it
gives you the three things you actually want:

1. **Value-for-money** — how much protein you get per unit of money.
2. **Suggested use** — main meal, snack, supplement, or treat.
3. **Recommendation score** — a 0–100 score with a plain-English verdict.

## Why this is different (innovation)

- **Not a database** — you supply your own data (from any label), so there is
  nothing to maintain and no API to call.
- **A decision tool, not a tracker** — MyFitnessPal *records*; `fitpick`
  *decides*. It is a "should I buy this?" answer, not a "what did I eat?" log.
- **Transparent rules** — every point is explained, and the thresholds are
  derived from public nutrition standards (China GB28050, ISSN/ACSM, AHA).
- **Zero dependencies** — pure Python standard library, works offline, installs
  without conflicts.

## Installation

```bash
pip install fitpick
