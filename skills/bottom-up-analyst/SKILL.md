---
name: bottom-up-analyst
description: >-
  Conduct substantive, long-only bottom-up research on one non-financial operating company.
  Use for an investment thesis, buy/pass/watch decision, valuation, earnings-quality review,
  bull/bear assessment, or full due-diligence memo when the user wants analysis rather than a
  quote or filing lookup. The framework suits businesses whose operating, asset, or transaction
  economics can be underwritten from public evidence, including cash-burning growth companies
  with observable unit economics. Do not use it as the primary framework for banks, insurers,
  REITs, funds, or clinical-stage and other predominantly binary-asset companies.
---

# Bottom-Up Analyst

Turn evidence about one company into a long-only investment judgment. Scale the work to the
question: answer a scoped valuation or earnings-quality request directly; produce the full memo
only for a deep dive or when the user asks for one.

This is the analysis layer of SecStack. Use `sec-edgar-skill` for filing evidence and
`market-scout` for market data and transcripts. A finished memo may later feed
`pitch-like-lou`, but this skill owns the research method and does not depend on that voice.

## Evidence discipline

Facts, estimates, assumptions, and external evidence must remain distinguishable. Use this
markup on load-bearing claims and tables, not on headings or connective prose:

- **[V] Verified:** checked against a cited filing, regulator, issuer document, or other
  authoritative primary record. Identify the form/document, period, section or accession, and
  date where available.
- **[E] Estimate:** calculated or modeled. Show the formula, inputs, units, and source dates.
- **[A] Assumption:** not established by available evidence. State what would validate it and
  how the conclusion changes if it is wrong.
- **[W] External evidence:** a web, trade, channel, expert, or secondary source. Name and date
  it. `[W]` describes provenance, not truth; assess incentives and corroboration.

Do not tag an inference `[V]` merely because its premises are verified. State the inference and
cite its premises. An issuer filing verifies what the issuer disclosed, not that management's
interpretation is neutral. Vendor-produced call transcripts are useful records of a call but
can contain transcription errors; verify a load-bearing quotation against issuer materials or
recording when practical.

Prefer the source authoritative for the claim. SEC filings lead for filed financials, capital
structure, contracts, ownership, and governance. Issuer IR may lead for a release not yet filed;
a regulator or court may lead for a rule or case; industry data may lead for market structure.
Report material conflicts instead of silently choosing one source.

## Workflow

### 1. Frame the decision

Identify the security, listing, as-of date, investor question, and requested depth. Resolve
ambiguous tickers or share classes before research. For a full deep dive, define the current
market expectation you need to test. For a scoped request, investigate only the evidence needed
to answer it and disclose what was not reviewed.

### 2. Build the evidence set

Use `sec-edgar-skill` orientation only when the relevant form or accession is unknown. Skip it
when an accession, cached artifact, or non-SEC source is already the precise route. Read the
latest annual filing and subsequent material updates for a full company review; choose narrower
sources for a narrower question.

Timestamp current market data. Check recent EDGAR and issuer IR for new disclosures, but do not
assume a same-day event has already been filed. Use call transcripts for management statements
and Q&A leads, with speaker attribution and the transcript caveat above.

Keep large documents on disk and retrieve only relevant sections. Follow each data skill's own
current guide and `--help`; do not guess flags, cache behavior, or field semantics here.

### 3. Select the analytical lenses

Choose an archetype only when it sharpens the work. Load the closest playbook from
`references/archetypes/`; use a primary and secondary lens when the economics genuinely span
both. Do not force a company into the taxonomy. If no playbook fits, reason from the business
model and the decision at hand.

| Lens | Use when the thesis turns on |
| :-- | :-- |
| `compounder.md` | returns on incremental capital and reinvestment runway |
| `hypergrowth.md` | immature profits, unit economics, and a path to positive cash flow |
| `cyclical.md` | normalized cycle earnings, cost position, and balance-sheet survival |
| `turnaround.md` | a specific mechanism changing margins, demand, or capital structure |
| `special_situation.md` | a transaction, legal document, security, or forced flow |
| `deep_value.md` | conservatively realizable assets and a path to realization |

### 4. Reconstruct the economics

Reconcile reported earnings to the cash-flow measure appropriate to the valuation. Separate
recurring operations from one-offs, acquisition effects, working-capital timing, stock
compensation, leases, and maintenance versus growth investment without double-counting any
adjustment. Use a multi-period view long enough for the business and cycle. Read
`references/guide_normalization.md`.

When a material part of value comes from a new stream or future margin structure, build a
bottom-up bridge from operational drivers to revenue, margins, reinvestment, and cash flow.
Treat an unsupported TAM share or margin target as `[A]`, not as a forecast.

### 5. Underwrite the business and stewards

Explain how the company makes money, why customers choose it, where industry profits accrue,
and what could change. Select peers by business model and economics rather than accepting an
automated industry list uncritically. Quantify material forces where reliable evidence permits;
otherwise use a bounded range or identify the unresolved variable. Do not invent precision to
fill a template. Read `references/guide_competitive.md`.

Review management incentives, dilution, capital allocation, controlling holders, related-party
transactions, and governance when they can affect value. Use 13F and Form 4 data as limited,
lagged evidence rather than a verdict. Read `references/guide_ownership_signals.md`.

### 6. Value the security

Use the lenses that match the cash-flow and asset economics; triangulation does not mean running
an inapplicable method. Reverse DCF is useful only when a positive base FCFF and the model shape
make implied growth interpretable. EPV is a no-growth operating case, not a guaranteed floor.
Special situations and asset plays usually need scenario payoffs or sum-of-parts work outside
the bundled scripts.

State the valuation date, cash-flow basis, enterprise-to-equity bridge, diluted share count,
discount rate, terminal assumptions, and scenario logic. Vary the assumptions that actually
drive value, not growth alone by habit. Read `references/guide_valuation.md` before running the
scripts.

### 7. Try to disprove the thesis

Write the strongest contrary explanation, run the relevant playbook's disqualifiers, and test
load-bearing assumptions. Distinguish permanent impairment from volatility. Describe what
would falsify the thesis, the expected timing, financing or dilution risk, and any evidence gap
that limits conviction. A pass or watch decision is a valid result.

### 8. Deliver at the requested depth

Use `references/memo_template.md` for a full deep dive. Adapt its sections and metrics to the
company and thesis; it is a decision-oriented skeleton, not a form. For a scoped answer, give
the conclusion, decisive evidence, calculations, countercase, missing work, and sources without
padding it into a full memo.

## Valuation scripts

Resolve script paths relative to this `SKILL.md` and invoke them by absolute path while keeping
the shell working directory at the user's research workspace. Every material assumption is
explicit; `--help` is the flag reference.

```bash
# Positive-FCFF forward sensitivity
python "<skill-dir>/scripts/dcf.py" forward --fcff0 1200 --growth 8,12,16 \
  --years 10 --terminal-growth 3 --wacc 10 --shares 500 --net-claims 200 --price 75

# Explicit annual FCFF, including an initial loss or inflection
python "<skill-dir>/scripts/dcf.py" forecast --fcff=-20,10,45,80,110 \
  --terminal-growth 2.5 --wacc 12 --shares 30 --net-claims 66 --price 8

# Growth implied by price
python "<skill-dir>/scripts/dcf.py" reverse --price 75 --fcff0 1200 --years 10 \
  --terminal-growth 3 --wacc 10 --shares 500 --net-claims 200

# No-growth operating earnings case
python "<skill-dir>/scripts/epv.py" --ebit 600 --tax 21 --wacc 9 \
  --shares 500 --net-claims 200 --price 10
```

The DCF is an enterprise model: pass normalized **FCFF**, discount at WACC, then subtract
`--net-claims` (debt and other senior claims less non-operating assets). Do not pass
after-interest owner earnings or FCFE and subtract debt again.

## Resources

| Resource | Read or run when |
| :-- | :-- |
| `references/memo_template.md` | writing a full due-diligence memo |
| `references/guide_normalization.md` | reconstructing normalized cash economics |
| `references/guide_competitive.md` | underwriting industry and competitive position |
| `references/guide_valuation.md` | choosing and implementing valuation lenses |
| `references/guide_ownership_signals.md` | assessing ownership, insiders, incentives, and governance |
| `references/archetypes/*.md` | one or two lenses materially sharpen the case |
| `scripts/dcf.py`, `scripts/epv.py` | reproducible enterprise-valuation arithmetic |

## Completion check

Before answering, ensure the work supports its own confidence: current security and source
periods are clear; material facts are cited; calculations reconcile; assumptions and inferences
are visible; the strongest countercase is addressed; valuation uses a consistent cash-flow
basis; and omitted work is disclosed. Do not manufacture a verdict stronger than the evidence.
