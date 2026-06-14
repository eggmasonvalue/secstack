# Market Scout

Pull public market data — price, market cap, trailing returns, peers, and sector screens — for
US-listed stocks via [`yfinance`](https://github.com/ranaroussi/yfinance). An unopinionated data
layer: it surfaces facts and rankings; it decides nothing.

Part of the [us-market-research-skills](../README.md) stack.

## Use

```bash
pip install -r requirements.txt      # yfinance + pandas; no API key or identity needed
python scripts/fetch_market_data.py --ticker AAPL --peers
```

yfinance offers far more than the script wraps and is self-documenting (`dir()`, `help()`,
`t.info.keys()`) — see [SKILL.md](SKILL.md) for how to discover and construct what you need.

Market data is best-effort and occasionally stale or missing for thinly-covered names; confirm
anything load-bearing against a primary source.
