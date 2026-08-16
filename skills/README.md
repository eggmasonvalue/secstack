# SecStack skills

SecStack is a composable stack of five [agent skills](https://agentskills.io/home) for
bottom-up equity research on US-listed companies. Each skill can stand on its own; together
they form a research pipeline.

## The stack

| Layer | Skill | Job |
|---|---|---|
| **Discovery** | [`signal-sweep`](signal-sweep/) | Scan SEC filings and market data to surface new investment ideas. |
| **Data** | [`sec-edgar-skill`](sec-edgar-skill/) | Retrieve and extract SEC filings, ownership, and 13F holder data. |
| **Data** | [`market-scout`](market-scout/) | Pull prices, returns, peers, sector screens, and transcripts. |
| **Analysis** | [`bottom-up-analyst`](bottom-up-analyst/) | Turn one ticker into an auditable investment memo. |
| **Voice** | [`pitch-like-lou`](pitch-like-lou/) | Render a finished thesis as a VIC-style pitch. |

## Data flow

```text
  signal-sweep  (surfaces tickers)
       │
       ▼
  bottom-up-analyst  (deep dive on one ticker)
       ├── sec-edgar-skill  (filings and ownership)
       ├── market-scout  (price, peers, transcripts)
       ▼
  pitch-like-lou  (finished pitch)
```

`bottom-up-analyst` is the conductor. It decides what to pull, reasons over the evidence,
values the business, and writes the memo. The data skills never decide what matters.

`signal-sweep` and `sec-edgar-skill` are independent data sources. `market-scout` is also
swappable: the analyst can use a different market-data provider without changing its
reasoning workflow.

The voice skill renders from a finished thesis; it is not an idea generator.

**Production order:** signal-sweep → bottom-up-analyst → memo → optionally pitch-like-lou.

## Progressive disclosure

Each skill keeps its `SKILL.md` entry point concise. Detailed guidance lives in
`references/`, executable helpers live in `scripts/`, and configuration/assets stay beside
the skill that owns them. Load only the guide or script required for the current task.

## Skill resources

- [`signal-sweep`](signal-sweep/) contains configurable market screens, SEC discovery
  scanners, conference discovery, and theme search.
- [`sec-edgar-skill`](sec-edgar-skill/) contains filing, financial, ownership, and 13F
  retrieval helpers.
- [`market-scout`](market-scout/) contains Yahoo Finance market and transcript helpers.
- [`bottom-up-analyst`](bottom-up-analyst/) contains valuation arithmetic and memo frameworks.
- [`pitch-like-lou`](pitch-like-lou/) contains the pitch-writing workflow and reference corpus.

Each skill's README documents its own dependencies and usage. Runtime caches are generated
next to the relevant workspace and are git-ignored.

## Current snapshot

The following commands measure the entry-point surface and the explicitly referenced skill
resources from the repository root:

```bash
cloc --by-file --include-lang=Markdown \
  skills/bottom-up-analyst/SKILL.md \
  skills/pitch-like-lou/SKILL.md \
  skills/sec-edgar-skill/SKILL.md \
  skills/signal-sweep/SKILL.md \
  skills/market-scout/SKILL.md
```

```bash
cloc \
  skills/bottom-up-analyst/SKILL.md \
  skills/bottom-up-analyst/references/memo_template.md \
  skills/bottom-up-analyst/references/guide_normalization.md \
  skills/bottom-up-analyst/references/guide_competitive.md \
  skills/bottom-up-analyst/references/guide_valuation.md \
  skills/bottom-up-analyst/references/guide_ownership_signals.md \
  skills/bottom-up-analyst/references/archetypes/*.md \
  skills/bottom-up-analyst/scripts/dcf.py \
  skills/bottom-up-analyst/scripts/epv.py \
  skills/market-scout/SKILL.md \
  skills/market-scout/scripts/fetch_market_data.py \
  skills/market-scout/scripts/fetch_transcripts.py \
  skills/pitch-like-lou/SKILL.md \
  skills/pitch-like-lou/references/corpus/*.md \
  skills/sec-edgar-skill/SKILL.md \
  skills/sec-edgar-skill/references/guide_core.md \
  skills/sec-edgar-skill/references/guide_filings.md \
  skills/sec-edgar-skill/references/guide_financials.md \
  skills/sec-edgar-skill/references/guide_ownership.md \
  skills/sec-edgar-skill/references/guide_holdings.md \
  skills/sec-edgar-skill/scripts/orient.py \
  skills/sec-edgar-skill/scripts/fetch_filing.py \
  skills/sec-edgar-skill/scripts/fetch_filings.py \
  skills/sec-edgar-skill/scripts/parse_financials.py \
  skills/sec-edgar-skill/scripts/list_headings.py \
  skills/sec-edgar-skill/scripts/fetch_insider_trades.py \
  skills/sec-edgar-skill/scripts/fetch_13f_holders.py \
  skills/sec-edgar-skill/scripts/test_setup.py \
  skills/signal-sweep/SKILL.md \
  skills/signal-sweep/screens.json \
  skills/signal-sweep/references/guide_screens.md \
  skills/signal-sweep/scripts/scan_insiders.py \
  skills/signal-sweep/scripts/scan_market.py \
  skills/signal-sweep/scripts/search_themes.py \
  skills/signal-sweep/scripts/scan_conferences.py
```

## Research scope

These skills produce research, not advice. Filings-first grounding, verified-versus-assumed
tagging, and pre-mortem analysis keep an LLM's fluent prose tethered to auditable evidence so
a human can reach their own judgment.
