# Bottom-Up Analyst

An [agent skill](SKILL.md) for substantive, long-only fundamental research on one
non-financial operating company. It turns filing, market, industry, and ownership evidence
into a scoped answer or a full, auditable due-diligence memo.

The framework is designed for companies whose operating economics and cash flows can be
underwritten. It is not the primary framework for banks, insurers, REITs, funds, or
predominantly binary-asset companies.

## What it does

- Scales the work to the question instead of forcing every request into a full memo.
- Selects one or more optional analytical lenses: compounder, hypergrowth, cyclical,
  turnaround, special situation, or deep value.
- Reconciles reported results to normalized economics without double-counting stock
  compensation, leases, working capital, or enterprise-to-equity adjustments.
- Underwrites competitive position, management incentives, ownership, and governance when
  they are material to value.
- Chooses valuation methods for the business rather than mechanically running every method.
- Separates verified evidence, estimates, assumptions, and external evidence, with citations.
- Builds the strongest countercase and lets conviction fall when evidence is incomplete.

## Layout

- `SKILL.md` — workflow, evidence discipline, resource routing, and script examples.
- `references/memo_template.md` — adaptable full-memo skeleton.
- `references/guide_*.md` — normalization, competition, valuation, and
  ownership/governance guidance.
- `references/archetypes/` — optional playbooks for six common thesis shapes.
- `scripts/dcf.py` — forward, explicit-forecast, and reverse enterprise DCF.
- `scripts/epv.py` — no-growth Earnings Power Value arithmetic.

## Setup

The valuation scripts use only the Python standard library:

```bash
python scripts/dcf.py --help
python scripts/epv.py --help
```

They require material assumptions explicitly. `dcf.py` accepts free cash flow to the firm
(FCFF), discounts it at WACC, and bridges enterprise value to equity using net claims: debt and
other senior claims less non-operating assets.

Install and configure [`sec-edgar-skill`](../sec-edgar-skill/) for SEC evidence and
[`market-scout`](../market-scout/) for market data and transcripts. Each data skill owns its
runtime, cache, and source instructions.

## Scope and judgment

This skill supports research, not personalized investment advice. Its memo is an auditable
argument rather than a recommendation tailored to a person's circumstances. A human remains
responsible for checking the evidence, assumptions, suitability, and decision.
