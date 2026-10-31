# yfinance inline

Use this when writing `yfinance` code yourself. List what exists rather than guessing names:

```python
import yfinance as yf

t = yf.Ticker("AAPL")
[m for m in dir(t) if not m.startswith("_")]  # estimates, options, holders, calendar, ...
sorted(t.info)  # snapshot field names
```

Verified on yfinance 1.5:

- **Units disagree.** `dividendYield` is a percent (0.31 means 0.31%), while
  `trailingAnnualDividendYield`, `payoutRatio`, `heldPercentInsiders`,
  `heldPercentInstitutions`, and `shortPercentOfFloat` are fractions. `^TNX` closes in percent
  yield (4.93 means 4.93%).
- **Multi-class shares.** `sharesOutstanding` covers only the quoted class, while `marketCap`
  covers all classes. Use `impliedSharesOutstanding` or the filing cover page for per-share math.
- **Symbols.** Share classes use a hyphen: `BRK-B`.
- **History is adjusted.** `history()` adjusts for splits and dividends by default. Pass
  `auto_adjust=False` for raw closes.
- **Dates.** Fields such as `mostRecentQuarter` are epoch seconds.
- **Speed.** Each `.info` is a slow per-ticker call. Batch prices with `yf.download([...])`.
- **Transcripts.** Yahoo blocks plain HTTP clients; `fetch_transcripts.py` drives a real browser.

Report each figure's field name, units, period, and retrieval time. When a field is missing or
stale, say so rather than swapping in a different field or period.
