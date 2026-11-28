# SECstack skills

SECstack is a composable stack of five [agent skills](https://agentskills.io/home) for
bottom-up equity research on US-listed companies. Each skill can stand on its own; together
they form a research pipeline.

## The stack

| Layer | Skill | Job |
|---|---|---|
| **Discovery** | [`screen`](screen/) | Scan SEC filings and market data to surface new investment ideas. |
| **Data** | [`edgar`](edgar/) | Retrieve and extract SEC filings, ownership, and 13F holder data. |
| **Data** | [`market`](market/) | Pull prices, returns, peers, sector screens, and transcripts. |
| **Analysis** | [`diligence`](diligence/) | Turn one operating company into scoped analysis or an auditable investment memo. |
| **Voice** | [`pitch-like-lou`](pitch-like-lou/) | Render a finished thesis as a VIC-style pitch. |

## Data flow

```text
  screen  (surfaces tickers)
       │
       ▼
  diligence  (deep dive on one ticker)
       ├── edgar  (filings and ownership)
       ├── market  (price, peers, transcripts)
       ▼
  pitch-like-lou  (finished pitch)
```

`diligence` is the conductor. It decides what to pull, reasons over the evidence,
values the business, and produces the requested analysis or full memo. The data skills supply
the underlying evidence.

`screen` and `edgar` are independent data sources. `market` is also
swappable: the analyst can use a different market-data provider without changing its
reasoning workflow.

The voice skill renders from a finished thesis; it is not an idea generator.

**Production order for a full thesis:** screen → diligence → memo → optionally
pitch-like-lou.

## Progressive disclosure

Each skill keeps its `SKILL.md` entry point concise. Detailed guidance lives in
`references/`, executable helpers live in `scripts/`, and configuration/assets stay beside
the skill that owns them. Load only the guide or script required for the current task.

## Skill resources

- [`screen`](screen/) contains configurable market screens, SEC discovery
  scanners, conference discovery, and theme search.
- [`edgar`](edgar/) contains filing, financial, ownership, and 13F
  retrieval helpers.
- [`market`](market/) contains Yahoo Finance market and transcript helpers.
- [`diligence`](diligence/) contains valuation arithmetic and memo frameworks.
- [`pitch-like-lou`](pitch-like-lou/) contains the pitch-writing workflow and reference corpus.

Each skill's README documents its dependencies and usage. Invoke installed artifact-producing
scripts from the research workspace so their git-ignored runtime caches stay beside the work.

## Research scope

These skills produce research, not advice. Filings-first grounding, verified-versus-assumed
tagging, and pre-mortem analysis keep an LLM's fluent prose tethered to auditable evidence so
a human can reach their own judgment.
