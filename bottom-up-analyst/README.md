# Bottom-Up Analyst

An [agent skill](SKILL.md) that turns **one company** into an **earned investment thesis**,
written up as a detailed, auditable due-diligence memo. It is the analytical engine of a
bottom-up research stack: given a ticker or a name, it drives SEC-filing and market-data
tools for grounding, reasons over the evidence, classifies the business into an archetype,
triangulates an intrinsic-value range, tries to kill its own thesis, and writes the memo.

## Where it sits

The **analyst** in a three-layer stack: the [data skills](../sec-edgar-skill/) ground it, and
[`pitch-like-lou`](../pitch-like-lou/) renders a pitch from its memo. The analyst is the missing
middle — it decides what to pull, reasons to a verdict, values the business, and writes the memo;
the data skills decide nothing and Lou assumes the work is already done. See the
[stack overview](../README.md) for how the four compose. **Production order:** analyst → memo →
(optionally) Lou pitches from it; the definition of done is a **pitch-ready memo**.

## What it does

- **Classifies** the company into one of six archetypes and loads the matching playbook —
  *compounder, hypergrowth, cyclical, turnaround/inflection, special-situation, deep-value* —
  so the right questions get the weight. (Lou's three value-investing shapes are a subset;
  the rest extend past where he worked. "Anything else" falls back to the core method.)
- **Normalizes** GAAP into owner earnings — maintenance vs. growth capex, stock comp, deferred
  revenue, one-offs — and shows capital allocation as a year-by-year trend.
- **Analyzes competitive position** filings-first (including *peers'* filings for management
  commentary), using the web only for what filings genuinely can't give — and labels it.
- **Values** by triangulation, weighted by archetype, with a **reverse-DCF** ("what's priced
  in?") as a first-class lens alongside forward DCF, EPV, and multiples.
- **Stress-tests** every thesis against the archetype's disqualifiers and a borrowed
  discipline: separate what you *know* from what you *believe*, concede the weak points, never
  let conviction outrun the evidence.

## Layout

- `SKILL.md` — the skill itself (the entry point an agent loads): the loop, archetype routing,
  how it drives the tools, and the valuation tooling.
- `references/` — lazily-loaded guides: the memo template, normalization, competitive analysis,
  valuation, and one playbook per archetype (`references/archetypes/`).
- `scripts/` — thin, self-documenting valuation tools:
  - `dcf.py` — two-stage DCF, **forward** (assumptions → intrinsic value) and **reverse**
    (price → implied growth), with a bear/base/bull sensitivity table.
  - `epv.py` — Earnings Power Value, the no-growth floor.

## Setup

The valuation scripts are pure-Python (standard library only) — no install needed:

```bash
python scripts/dcf.py --help
python scripts/epv.py --help
```

For the data layer, install and configure [`sec-edgar-skill`](../sec-edgar-skill/) (it needs an
`EDGAR_IDENTITY`) and, for market data, [`market-scout`](../market-scout/); this skill drives
those tools but does not re-document them.

## A note on scope

This skill produces analysis, not advice. It is a tool for doing research rigorously and
honestly; it does not know your circumstances and nothing it writes is a recommendation to buy
or sell a security. Its entire design — the honesty markup, the pre-mortem, the
verified-vs-assumed tagging — exists to keep an LLM's fluent prose tethered to evidence, so
that a human can audit every claim and reach their own judgment.
