# Due Diligence

An [agent skill](SKILL.md) for long-only due diligence on one US-listed operating company. It
turns filing, market, industry, and ownership evidence into a scoped answer or a full,
auditable memo. Banks, insurers, REITs, funds, and binary-asset companies need other
frameworks.

## What it does

- Sizes the work to the question; a full memo only for a deep dive or explicit request.
- Tags evidence as verified, estimated, assumed, or external, with citations.
- Reconciles reported results to one cash-flow basis without double-counting stock
  compensation, leases, working capital, or bridge items.
- Underwrites competitive advantage as a causal chain, not a label.
- Chooses valuation methods that fit the cash flows, and lets conviction fall to the weakest
  load-bearing link.

## Layout

- `SKILL.md` — evidence discipline, the moves of the work, completion bar.
- `references/normalization.md` — reported-to-cash bridge and where adjustments go wrong.
- `references/valuation.md` — enterprise bridge, script usage, valuation traps.
- `references/archetypes.md` — edge, traps, valuation route, and tell for six thesis shapes.
- `references/memo.md` — full-memo spine.
- `scripts/dcf.py`, `scripts/epv.py` — standard-library FCFF DCF (forward, forecast,
  reverse) and Earnings Power Value. Python 3.10+.

Install and configure [`sec-filings`](../sec-filings/) for SEC evidence and
[`market-data`](../market-data/) for market data and transcripts.

## Scope and judgment

This skill supports research, not personalized investment advice. A human remains responsible
for checking the evidence, assumptions, suitability, and decision.
