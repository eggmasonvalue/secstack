---
name: due-diligence
description: >-
  Long-only due diligence on one US-listed operating company: investment thesis, valuation,
  earnings quality, bull/bear case, buy/watch/pass, or a full memo. Built for businesses whose
  economics can be underwritten from public evidence, including cash-burning growers with
  visible unit economics. Banks, insurers, REITs, funds, and binary-asset companies need other
  frameworks.
---

# Due diligence

Decide whether the price compensates for what can go wrong, using evidence a skeptical reader
can audit. *Pass* and *watch* are full answers. Size the work to the question: a scoped
question gets a scoped answer, and the full memo is for a deep dive or an explicit request.

## Evidence

Tag load-bearing claims and table rows (not prose):

- **[V]** checked against an authoritative primary record, cited by form, period,
  section or accession, and date;
- **[E]** calculated, with formula, inputs, units, and dates;
- **[A]** assumed, with what would confirm it and what changes if it is wrong;
- **[W]** web, trade, expert, or secondary, with source and date; `[W]` records where a claim
  came from, not whether it is true.

An inference from verified premises is an inference: cite the premises, then state it. An issuer
filing verifies what the issuer said, not that its framing is neutral. Use the source that is
authoritative for each claim (filings for filed numbers, IR for an unfiled release, the
regulator for a rule), and when sources conflict, report the conflict.

Use `sec-filings` for filings and `market-data` for prices and transcripts. Timestamp market
data. For a full review, read the latest 10-K and the material filings since.

## The work

These are moves, not a form. Skip what the question does not need, and disclose what you
skipped.

1. **Frame.** Pin down the security, share class, as-of date, and the question. Write down what
   the current price requires to be true: that is the expectation you are testing.
2. **Reconstruct the economics.** Bridge reported earnings to the cash flow the valuation uses,
   following `references/normalization.md`. When value rests on something that is not yet in
   the numbers, build it from operating drivers; an unsupported TAM share or margin target is
   `[A]`.
3. **Underwrite the business.** Explain where industry profit pools and why this company keeps
   its share. Write each claimed advantage as a chain: *asset or position → customer or cost
   consequence → operating evidence → economic result → why rivals can't copy it*. A label
   ("moat", "network effect") without the chain does no work. Choose peers by economics, not by
   sector code. Size threats where the evidence allows; otherwise give a range or name the
   leading indicator.
4. **Judge the stewards** when they can move value: incentives, dilution, capital allocation,
   control, related parties. 13F and Form 4 data are lagged clues; the
   `sec-filings` skill's `references/ownership.md` before interpreting them.
5. **Value it** with methods that fit the cash flows, following `references/valuation.md`.
6. **Try to kill it.** Make the strongest honest case against owning it, run the archetype's
   disqualifiers, and run a pre-mortem: a year from now this failed; what happened? Separate
   permanent impairment from volatility, and name the falsifiers and the date by which evidence
   should arrive.
7. **Deliver.** For a full memo, use `references/memo.md`. Otherwise give the conclusion, the
   decisive evidence, the arithmetic, the countercase, the open gaps, and the sources.

## Archetypes

When one or two archetypes sharpen the case, read their sections in `references/archetypes.md`.
Each section names the archetype's edge, its traps, its valuation route, and the indicator that
breaks first. If none fits, reason from the business directly.

| Archetype | The thesis turns on |
| :-- | :-- |
| compounder | incremental returns on capital and reinvestment runway |
| hypergrowth | immature margins, unit economics, path to positive cash flow |
| cyclical | normalized earnings, cost position, surviving the trough |
| turnaround | one specific mechanism changing margins, demand, or capital structure |
| special situation | a transaction, legal term, security, or forced flow |
| deep value | realizable assets and a path to realizing them |

## Done when

- the security, share class, and every source period are unambiguous;
- every load-bearing number is cited or tagged;
- the arithmetic reconciles: one cash-flow basis, an enterprise-to-equity bridge, diluted
  shares, and price as of a stated date;
- the strongest countercase has an answer; and
- conviction matches the weakest load-bearing link, and omitted work is disclosed.
