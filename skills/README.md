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

Each skill's README documents its dependencies and usage. Invoke installed artifact-producing
scripts from the research workspace so their git-ignored runtime caches stay beside the work.

## Research scope

These skills produce research, not advice. Filings-first grounding, verified-versus-assumed
tagging, and pre-mortem analysis keep an LLM's fluent prose tethered to auditable evidence so
a human can reach their own judgment.
