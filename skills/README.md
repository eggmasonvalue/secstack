# SecStack skills

SecStack is a composable stack of five [agent skills](https://agentskills.io/home) for
bottom-up equity research on US-listed companies. Each skill can stand on its own; together
they form a research pipeline.

## The stack

| Layer | Skill | Job |
|---|---|---|
| **Discovery** | [`idea-generation`](idea-generation/) | Surface new tickers from insider buying, 13Ds, screens, filing themes, and investor events. |
| **Data** | [`sec-filings`](sec-filings/) | Retrieve filings, XBRL statements, insider trades, 13F holders, and blockholders. |
| **Data** | [`market-data`](market-data/) | Pull any Yahoo Finance field and earnings-call transcripts. |
| **Analysis** | [`due-diligence`](due-diligence/) | Turn one operating company into a scoped answer or an auditable investment memo. |
| **Voice** | [`pitch-like-lou`](pitch-like-lou/) | Render a finished thesis as a VIC-style pitch. |

## Data flow

```text
  idea-generation  (surfaces tickers)
       │
       ▼
  due-diligence  (deep dive on one ticker)
       ├── sec-filings  (filings and ownership)
       ├── market-data  (price, peers, transcripts)
       ▼
  pitch-like-lou  (finished pitch)
```

`due-diligence` is the conductor. It decides what to pull, reasons over the evidence,
values the business, and produces the requested analysis or full memo. The data skills supply
the underlying evidence.

`idea-generation` and `sec-filings` are independent data sources. `market-data` is also
swappable: due diligence can use a different market-data provider without changing its
reasoning.

The voice skill renders from a finished thesis; it is not an idea generator.

**Production order for a full thesis:** idea-generation → due-diligence → memo → optionally
pitch-like-lou.

## Progressive disclosure

Each `SKILL.md` carries what every run needs: commands, semantics, and the gotchas the
scripts encode. Branch-specific detail lives in `references/`, executable helpers in
`scripts/`, and configuration beside the skill that owns it.

## Skill resources

- [`idea-generation`](idea-generation/) contains configurable market screens, SEC discovery
  scanners, conference discovery, and theme search.
- [`sec-filings`](sec-filings/) contains filing, financial, ownership, and 13F
  retrieval helpers plus an inline `edgartools` reference.
- [`market-data`](market-data/) contains Yahoo Finance snapshot and transcript helpers.
- [`due-diligence`](due-diligence/) contains valuation arithmetic, archetypes, and the memo
  spine.
- [`pitch-like-lou`](pitch-like-lou/) contains the pitch-writing workflow and reference corpus.

Each skill's README documents its dependencies and usage. Invoke installed artifact-producing
scripts from the research workspace so their git-ignored runtime caches stay beside the work.

## Research scope

These skills produce research, not advice. Filings-first grounding, verified-versus-assumed
tagging, and pre-mortem analysis keep an LLM's fluent prose tethered to auditable evidence so
a human can reach their own judgment.
