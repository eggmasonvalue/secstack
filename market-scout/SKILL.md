---
name: market-scout
description: >-
  Pull public market data for US-listed stocks via Yahoo Finance (yfinance): current price,
  market cap, shares, 52-week range, trailing returns, and sector/industry peer tables and
  pre-ranked screens (top by weight, top performers, top growth). Use this whenever a task
  needs a quick market snapshot or quote for a ticker, trailing performance, a company's peer
  set, or a sector/theme shortlist — e.g. "what's the price/return on X", "who are X's peers",
  "best-performing names in this industry", or turning a theme into a concrete list of tickers
  to investigate. This is an unopinionated market-data layer: it surfaces facts and rankings;
  it does not decide what is cheap, good, or worth buying.
---

# Market Scout

Pull **public market data** and do light **sector/peer screening** for US-listed stocks with
`yfinance`. Unopinionated: it surfaces prices, returns, peers, and rankings; it does not decide
what is cheap or worth buying — leave that to whatever framework is driving.

## Setup

Install the deps (Python ≥ 3.10); **no API key or identity is needed** — Yahoo Finance is public.

```bash
pip install -r requirements.txt    # yfinance + pandas
```

## yfinance is self-documenting — discover, then construct

The bundled script wraps only the common snapshot/returns/peers case. yfinance exposes far more
(financials, holders, options, earnings dates, calendar, sector/industry screens, …). **Do not
assume or hard-code field names — discover them at runtime** and build exactly what the task
needs:

```python
import yfinance as yf
t = yf.Ticker("AAPL")

print([a for a in dir(t) if not a.startswith("_")])   # all attributes/methods
help(yf.Ticker)                                         # full documented API
list(t.info.keys())                                     # every field in the snapshot

# Sector/industry screening primitives (great for a theme -> shortlist):
ind = yf.Industry(t.info["industryKey"])
print([a for a in dir(ind) if not a.startswith("_")])  # top_companies,
                                                        # top_performing_companies,
                                                        # top_growth_companies, overview, ...
```

When a field or method isn't what you expected, `dir()` / `help()` / `.info.keys()` recover the
answer inline — prefer that over guessing.

## Script

Run with the project's Python; it prints a compact Markdown summary to stdout (market data is
small and time-sensitive, so nothing is cached). `--help` is the authoritative flag reference:

```bash
python scripts/fetch_market_data.py --ticker AAPL --industry --peers
```
