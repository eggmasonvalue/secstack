---
name: market-data
description: >-
  Yahoo Finance market data for US-listed securities via yfinance: prices, market cap, share
  counts, returns, multiples, analyst estimates, options, earnings dates, industry peers,
  Treasury yields, and earnings-call transcripts. Use for any current market figure or
  call transcript.
---

# Market data

Run `python "<skill-dir>/scripts/<script>.py"` from the research workspace; `--help` is the flag
reference.

```bash
fetch_market_data.py --ticker AAPL [--period 10y] [--industry] [--peers]   # snapshot + returns
fetch_transcripts.py --ticker AAPL --list
fetch_transcripts.py --ticker AAPL [--latest 2 | --year 2025 [--quarter Q3]]  # -> ./transcript-cache
```

The scripts cover two jobs. For any other field (estimates, options, holders, calendars, yields,
financial tables), use `yfinance` directly after reading `references/yfinance.md`.
