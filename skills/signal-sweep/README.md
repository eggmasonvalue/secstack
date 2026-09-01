# Signal Sweep

An [agent skill](SKILL.md) that discovers equity-research candidates from SEC filings and Yahoo
Finance market data. It emits shortlists with source links and coverage notes; every match still
requires company-level diligence.

## Capabilities

| Route | Script |
|---|---|
| Form 4 purchase clusters and event-date move context; Schedule 13D filings | `scan_insiders.py` |
| Configurable Yahoo Finance market screens | `scan_market.py` |
| SEC filing full-text keyword/theme search | `search_themes.py` |
| Investor-event discovery across relevant 8-K disclosures | `scan_conferences.py` |

Within [SecStack](../README.md), the skill sits upstream of
[`bottom-up-analyst`](../bottom-up-analyst/): it proposes tickers; the analyst investigates them.

## Setup

The SecStack bootstrap installs this skill's dependencies into the profile environment. For
standalone use:

```bash
uv sync --project "<skill-dir>"
```

Activate the resulting environment or prefix script commands with
`uv run --project "<skill-dir>"`.

Set `EDGAR_IDENTITY` for insider, theme, and investor-event scans (see
[profile setup](../../README.md#one-time-runtime-setup)). Market screens use Yahoo Finance only.

Keep the research workspace as the current directory and invoke installed scripts by resolved
absolute path. This keeps `signal-sweep-cache/` with the research rather than the installed skill.
See [SKILL.md](SKILL.md) for routes, semantics, and output contracts.

## Screen customization

Definitions and universe bounds live in [`screens.json`](screens.json). See
[`references/guide_screens.md`](references/guide_screens.md) when adding or changing a screen; the
guide uses runtime `yfinance` discovery because provider fields can change.

## Daily workflow

[`.github/workflows/insider-scan.yml`](../../.github/workflows/insider-scan.yml) runs the insider
scan on weekdays, optionally posts results to Discord, and uploads the Markdown report. It requires
`EDGAR_IDENTITY`; set `DISCORD_WEBHOOK_URL` only when alerts are wanted. The workflow also supports
manual date, lookback, and threshold inputs.
