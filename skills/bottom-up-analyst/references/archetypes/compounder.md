# Archetype: Quality Compounder

A business that earns **high returns on capital** and can **reinvest** a large share of its
earnings at similar returns for years. The thesis is rarely "it's cheap" — it's "the market
under-appreciates the *duration* and *reinvestment runway* of the compounding." Time is the
ally; you are underwriting a machine, then trying to buy it at a fair price. (One of Lou's
three value-investing shapes — see NVR, Sportsman's Guide in the `pitch-like-lou` corpus.)

## Tell it by

Durable ROIC/ROE well above the cost of capital (sustained, not a single year), pricing
power, low incremental capital intensity, expanding or stable margins, and a reinvestment
runway (new units, geographies, share gains) that isn't nearly exhausted.

## Where the value hides

- **Duration the market won't extrapolate.** Screens see a high multiple and stop; the edge
  is judging that the high return *persists* far longer than consensus assumes.
- **Reinvestment math.** Value = return on incremental capital × the fraction reinvested. A
  35% ROIC business reinvesting 70% of earnings compounds intrinsic value ~24%/yr before any
  multiple change — that engine, not the entry multiple, is the thesis.
- **Under-distorted economics** — GAAP often *understates* a compounder (expensed growth
  investment, deferred revenue, conservative depreciation).

## Pull these (drive sec-edgar)

- 10-K Item 7 (MD&A) and Item 1 (Business) — the unit economics and the runway in management's
  words.
- The cash-flow statement and the revenue / deferred-revenue / lease footnotes — for the
  normalization that reveals true returns.
- A multi-year financial history (`sec-edgar-skill`'s `parse_financials.py` across years) — to prove ROIC is
  *durable*, not a one-year flatter.
- The proxy (DEF 14A) — capital-allocation incentives; is management paid to compound or to
  empire-build?

## Key metrics

ROIC and **return on incremental invested capital** (the forward-looking one), reinvestment
rate, organic revenue growth, gross-margin stability, FCF conversion, same-store / cohort /
unit economics where disclosed.

## Normalize / adjust

- Split maintenance vs. growth capex carefully — a compounder's value is highly sensitive to
  it (see `guide_normalization.md`).
- Pull deferred revenue back into earning power; undo conservative-accounting drag.
- Expense stock comp and bake dilution into the share count.

## Valuation lens

Lead with a **forward two-stage DCF** that gives the long reinvestment runway room, then
**reality-check with a reverse-DCF** (is the priced-in growth sane?) and floor it with EPV.
The key question isn't today's multiple — it's whether the runway justifies it.

## Disqualifiers — kill it (or mark it down) if…

- High ROIC is an **accounting mirage** — goodwill-light denominators, off-balance-sheet
  leverage, or returns that evaporate once you capitalize the real investment.
- **Growth needs ever more capital at falling returns** — incremental ROIC is decaying toward
  the cost of capital; the compounding is already ending.
- The **reinvestment runway is nearly full** — you're paying a compounder multiple for what's
  about to become a no-growth cash cow.
- **Buybacks only when the stock is dear**, or capital allocation that destroys the very
  compounding you're paying for.
- Margins propped by a **temporary** advantage (a subsidy, a fad, one big customer) rather
  than a structural moat.
