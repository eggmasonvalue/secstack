# US Market Research Skills

A composable stack of [agent skills](https://agentskills.io/home) for rigorous bottom-up equity
research on US-listed companies — from idea discovery through primary data (SEC filings +
market data), through an analytical framework, to a finished pitch. Each skill stands on its
own; together they form a pipeline.

## The skills

| Layer | Skill | Job |
|---|---|---|
| **Discovery** | [`signal-sweep`](signal-sweep/) | Scan SEC filings and market data across the $50M–$10B universe to surface new investment ideas: insider cluster/rip/dip buys, activist 13D filings, market screens, keyword/theme search, conference discovery. |
| **Data** | [`sec-edgar-skill`](sec-edgar-skill/) | Retrieve & extract SEC EDGAR filings (10-K/10-Q/8-K, 20-F/6-K, XBRL financials, ownership, holdings) and 13F institutional holder data (via 13f.info), token-efficiently. Unopinionated. |
| **Data** | [`market-scout`](market-scout/) | Pull price, returns, peers, sector screens, and earnings call transcripts via Yahoo Finance. Unopinionated. |
| **Analysis** | [`bottom-up-analyst`](bottom-up-analyst/) | Turn one ticker into an earned, auditable investment memo — drives the data skills, classifies the archetype, values it, tries to kill it. |
| **Voice** | [`pitch-like-lou`](pitch-like-lou/) | Render a Norbert Lou–style Value Investors Club pitch from a finished thesis. |

## Salient Features

### Composability

```text
  signal-sweep  (surfaces tickers)
       │
       ▼
  bottom-up-analyst  (deep dive on one ticker)
       ├── sec-edgar-skill  (SEC filings)
       ├── market-scout     (price, peers, transcripts)
       ▼
  pitch-like-lou  (finished pitch)
```

- **Discovery feeds analysis.** `signal-sweep` scans the universe and produces shortlists of
  tickers with reasons. `bottom-up-analyst` takes one of those tickers and does the deep dive.
  They are independent — you can skip discovery and hand the analyst a ticker directly.
- **The two data skills are independent and swappable.** `sec-edgar-skill` (filings) and
  `market-scout` (market data) know nothing of each other; either can be replaced — e.g. point
  the analyst at a paid data provider instead of `market-scout` and nothing else changes.
- **The analyst is the brain and the conductor.** `bottom-up-analyst` decides what to pull,
  reasons over it, values the business, and writes the memo. It drives the data skills; they
  never decide what matters.
- **The voice renders from a finished thesis.** `pitch-like-lou` turns the analyst's memo into a
  pitch; it is not an idea generator.

**Production order:** signal-sweep → analyst → memo → (optionally) Lou pitches from it.

### Progressive disclosure at the center of design - lets your model's intelligence shine through

#### Current snapshot

From the repository root, reproduce these reports with:

```bash
# Agent-loaded entry points
cloc --by-file --include-lang=Markdown bottom-up-analyst/SKILL.md pitch-like-lou/SKILL.md sec-edgar-skill/SKILL.md signal-sweep/SKILL.md market-scout/SKILL.md

# Referenced skill surface only
cloc \
  bottom-up-analyst/SKILL.md \
  bottom-up-analyst/references/memo_template.md \
  bottom-up-analyst/references/guide_normalization.md \
  bottom-up-analyst/references/guide_competitive.md \
  bottom-up-analyst/references/guide_valuation.md \
  bottom-up-analyst/references/guide_ownership_signals.md \
  bottom-up-analyst/references/archetypes/*.md \
  bottom-up-analyst/scripts/dcf.py bottom-up-analyst/scripts/epv.py \
  market-scout/SKILL.md market-scout/requirements.txt market-scout/scripts/fetch_market_data.py market-scout/scripts/fetch_transcripts.py \
  pitch-like-lou/SKILL.md pitch-like-lou/references/corpus/*.md \
  sec-edgar-skill/SKILL.md \
  sec-edgar-skill/references/guide_core.md sec-edgar-skill/references/guide_filings.md sec-edgar-skill/references/guide_financials.md sec-edgar-skill/references/guide_ownership.md sec-edgar-skill/references/guide_holdings.md \
  sec-edgar-skill/scripts/orient.py sec-edgar-skill/scripts/fetch_filing.py sec-edgar-skill/scripts/fetch_filings.py sec-edgar-skill/scripts/parse_financials.py sec-edgar-skill/scripts/list_headings.py sec-edgar-skill/scripts/fetch_insider_trades.py sec-edgar-skill/scripts/fetch_13f_holders.py sec-edgar-skill/scripts/test_setup.py \
  signal-sweep/SKILL.md signal-sweep/screens.json signal-sweep/references/guide_screens.md \
  signal-sweep/scripts/scan_insiders.py signal-sweep/scripts/scan_market.py signal-sweep/scripts/search_themes.py signal-sweep/scripts/scan_conferences.py
```

The second command lists the referenced skill paths explicitly, so repository-level docs and
unreferenced proposals are not counted.

```text
------------------------------------------------------------------------------------------
File                                        blank        comment           code
------------------------------------------------------------------------------------------
./bottom-up-analyst/SKILL.md                   51              0            228
./pitch-like-lou/SKILL.md                      39              0            164
./sec-edgar-skill/SKILL.md                     36              0            135
./signal-sweep/SKILL.md                        27              0             81
./market-scout/SKILL.md                        19              0             60
------------------------------------------------------------------------------------------
SUM:                                          172              0            668
------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Markdown                        29           1608              0           3025
Python                          16            711            534           2890
JSON                             1              0              0             99
Text                             1              1              0              5
-------------------------------------------------------------------------------
SUM:                            47           2320            534           6019
-------------------------------------------------------------------------------
```

## Install

Install the whole stack, or any single skill on its own - point your agent at
this repository, or at a single skill subfolder. Each skill is a self-contained
folder with its own `SKILL.md`.

## Setup

### SEC identity (required)

The SEC's [fair-access policy](https://www.sec.gov/os/webmaster-faq#developers) requires a
contact name and email in the User-Agent header. Requests without one are blocked (HTTP 403).
Set it once — `sec-edgar-skill` and `signal-sweep` both read it automatically:

```bash
export EDGAR_IDENTITY="Jane Analyst jane@example.com"     # bash/zsh
$env:EDGAR_IDENTITY = "Jane Analyst jane@example.com"     # PowerShell
```

Use your real name and email. The SEC uses this only to contact you if your traffic causes
problems — it is not authentication.

### Per-skill dependencies

- **`signal-sweep`** — `pip install -r signal-sweep/requirements.txt`
- **`sec-edgar-skill`** — `pip install -r sec-edgar-skill/requirements.txt`
- **`market-scout`** — install both before use: `pip install -r market-scout/requirements.txt`
  and `npm install -g agent-browser && agent-browser install`. No identity needed.
- **`bottom-up-analyst`** — valuation scripts are standard-library only; no install needed.
- **`pitch-like-lou`** — documentation and a reference corpus; nothing to install.

## Contributing

This repo is agent-maintained. Start at [`AGENTS.md`](AGENTS.md), then see
[`context/MAP.md`](context/MAP.md) (where things live),
[`context/DECISIONS.md`](context/DECISIONS.md) (why), and
[`context/CONVENTIONS.md`](context/CONVENTIONS.md) (code rules). Lint with
`uv run ruff check .` and `npx markdownlint-cli2 "**/*.md"`. Work on a branch and
open a PR — never commit to `main` directly.

## A note on scope

These skills produce **research, not advice**. They are tools for doing diligence rigorously and
honestly; nothing they output is a recommendation to buy or sell a security. The whole design —
filings-first grounding, verified-vs-assumed tagging, the pre-mortem — exists to keep an LLM's
fluent prose tethered to auditable evidence so a human can reach their own judgment.
