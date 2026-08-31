---
name: market-scout
description: >-
  Retrieve current public market data and earnings-call transcripts for US-listed stocks via
  Yahoo Finance: quotes, market capitalization, shares, price history and trailing returns,
  industry context, peer tables, and transcript text. Use when a task needs a current market
  snapshot, performance calculation, Yahoo peer or industry data, a market-data field, or an
  earnings-call transcript. Use primary filings for facts that Yahoo does not author or when a
  load-bearing figure needs regulatory verification.
---

# Market Scout

Retrieve market context and transcript text without turning the result into an investment
conclusion.

## Runtime and paths

Resolve bundled paths relative to this `SKILL.md`. Invoke scripts by absolute path while keeping
the shell working directory at the research workspace. This puts the default
`./transcript-cache` beside the work rather than inside the installed skill; alternatively pass
`--cache-dir`.

The packaged SecStack profile already exposes this skill's Python dependencies. For standalone
use, run `uv sync --project "<skill-dir>"`, then either activate that environment or prefix the
examples below with `uv run --project "<skill-dir>"`. `fetch_transcripts.py` also requires the
`agent-browser` binary and its one-time browser installation (`agent-browser install`). No API key
or SEC identity is required.

## Choose a route

### Snapshot, returns, industry, and peers

`fetch_market_data.py` prints a live Markdown report to stdout. It does not cache time-sensitive
market data.

```bash
python "<skill-dir>/scripts/fetch_market_data.py" --ticker AAPL
python "<skill-dir>/scripts/fetch_market_data.py" --ticker AAPL --industry --peers
```

The default report includes common trailing windows available inside the requested history period.
Use `--period` to change how much history is fetched. For a different interval or field, use the
runtime-discovery route below rather than treating the bundled report as Yahoo's full schema.

### Earnings-call transcripts

List the periods Yahoo currently exposes, then request the exact period or latest count needed:

```bash
python "<skill-dir>/scripts/fetch_transcripts.py" --ticker AAPL --list
python "<skill-dir>/scripts/fetch_transcripts.py" --ticker AAPL --latest 1
python "<skill-dir>/scripts/fetch_transcripts.py" --ticker AAPL --year 2025
python "<skill-dir>/scripts/fetch_transcripts.py" --ticker AAPL --quarter Q3 --year 2025
```

Downloads are written to `<cache>/<TICKER>/transcripts/Q3-FY2026.md` and reused on later runs.
Artifact-producing mode emits one absolute path per completed transcript to stdout and diagnostics
to stderr. A partial or total retrieval failure exits nonzero rather than masquerading as an empty
period.

Each file preserves the Yahoo source URL and, when present, separates prepared remarks from Q&A.
Transcript text and speaker attribution are third-party data; verify a consequential quote against
the issuer's own transcript, webcast, or filing when available.

## Runtime discovery beyond the wrappers

The bundled scripts cover frequent jobs, not the limits of `yfinance`. Inspect the installed API
instead of guessing field names or assuming a fixed metric template:

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
print([name for name in dir(ticker) if not name.startswith("_")])
print(sorted((ticker.info or {}).keys()))
help(ticker.history)

industry = yf.Industry((ticker.info or {})["industryKey"])
print([name for name in dir(industry) if not name.startswith("_")])
```

Use this route for calendars, options, holders, financial tables, custom return windows, or other
Yahoo fields. Report the field name, period, units, and retrieval date. Treat missing or stale data
as missing; do not silently substitute a different field or period.
