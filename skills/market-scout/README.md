# Market Scout

Pull public market data — price, market cap, trailing returns, peers, and sector screens — for
US-listed stocks via [`yfinance`](https://github.com/ranaroussi/yfinance). An unopinionated data
layer: it surfaces facts and rankings; it decides nothing.

Part of the [SecStack skills](../README.md) collection.

## Installation (do this first)

Install Python deps and browser runtime before using the scripts:

```bash
pip install -r requirements.txt
# The SecStack bootstrap installs agent-browser into the isolated Pi profile.
# Run this once from an active SecStack profile:
agent-browser install
```

- `yfinance`/`pandas` power market/peer data.
- `agent-browser` is required for earnings-call transcript pages (JS-rendered Yahoo/Quartr).
- In the packaged SecStack profile, its Pi-managed binary is already on PATH.

## Use

```bash
python scripts/fetch_market_data.py --ticker AAPL --peers
```

## Earnings call transcripts (Yahoo + Quartr)

```bash
python scripts/fetch_transcripts.py --ticker AAPL --list
python scripts/fetch_transcripts.py --ticker AAPL --latest 1
```

yfinance offers far more than the script wraps and is self-documenting (`dir()`, `help()`,
`t.info.keys()`) — see [SKILL.md](SKILL.md) for how to discover and construct what you need.

Market data is best-effort and occasionally stale or missing for thinly-covered names; confirm
anything load-bearing against a primary source.
