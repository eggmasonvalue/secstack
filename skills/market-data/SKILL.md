---
name: market-data
description: >-
  Yahoo Finance market data for US-listed securities via yfinance: prices, market cap, share
  counts, returns, multiples, analyst estimates, options, earnings dates, industry peers,
  Treasury yields, and earnings-call transcripts. Use for any current market figure or
  call transcript.
---

# Market data

## Run

Run `python "<skill-dir>/scripts/<script>.py"` from the research workspace; `--help` is the flag
reference. No API key or SEC identity is needed.

```bash
fetch_market_data.py --ticker AAPL [--period 10y] [--industry] [--peers]   # snapshot + returns, stdout
fetch_transcripts.py --ticker AAPL --list
fetch_transcripts.py --ticker AAPL [--latest 2 | --year 2025 [--quarter Q3]]
```

**Transcripts** need a real browser because Yahoo blocks plain HTTP clients. The script drives
`agent-browser` (one-time setup: `agent-browser install`) and caches
`./transcript-cache/<TICKER>/transcripts/Q3-FY2026.md`, with the source URL. It
splits Prepared Remarks from Q&A when an operator turn mentions questions. It prints one path per transcript, and a nonzero exit means a
retrieval failed. `--year` matches the fiscal year in the call title. Transcripts are vendor
text, so check a quote you rely on against the issuer's own transcript or webcast.

**Everything else** comes from `yfinance` directly. The wrapper covers a few common jobs, not
the API. List what exists instead of guessing names:

```python
import yfinance as yf

t = yf.Ticker("AAPL")
[m for m in dir(t) if not m.startswith("_")]  # estimates, options, holders, calendar, ...
sorted(t.info)  # snapshot field names
```

## Gotchas (verified on yfinance 1.5)

- **Units disagree.** `dividendYield` is a percent (0.31 means 0.31%), while
  `trailingAnnualDividendYield`, `payoutRatio`, `heldPercentInsiders`,
  `heldPercentInstitutions`, and `shortPercentOfFloat` are fractions. `^TNX` closes in percent
  yield (4.93 means 4.93%).
- **Multi-class shares.** `sharesOutstanding` covers only the quoted class, while `marketCap`
  covers all classes (BRK-B: 1.41B class B shares vs 2.14B implied). Use
  `impliedSharesOutstanding` or the filing cover page for per-share math.
- **Symbols.** Share classes use a hyphen: `BRK-B` works, `BRK.B` returns nothing.
- **History is adjusted.** `history()` adjusts for splits and dividends by default, so returns
  include dividends. Pass `auto_adjust=False` for raw closes.
- **Dates.** Fields such as `mostRecentQuarter` are epoch seconds.
- **Speed.** Each `.info` is a slow per-ticker call. Batch prices with `yf.download([...])`.
- **Missing data.** Report the field name, units, period, and retrieval time. When a field is
  missing or stale, say so rather than swapping in a different field or period.
