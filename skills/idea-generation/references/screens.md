# Screens

Read this before you add or change an entry in `screens.json`. Yahoo's screener schema changes,
so ask the installed `yfinance` for it rather than trusting a static list:

```python
import yfinance as yf

q = yf.EquityQuery("eq", ["region", "us"])
q.valid_fields  # fields by category
q.valid_values  # accepted values for equality fields
```

Before keeping a new screen, run it with `--size 5` and inspect the raw matches. Confirm that
the units and the sort direction mean what the description says.

## Definition

```json
{
  "id": "positive-low-ev-revenue",
  "name": "Positive EV/Revenue Below 1x",
  "emoji": "📊",
  "description": "Positive trailing EV/revenue between 0x and 1x",
  "filters": [
    {"field": "lastclosetevtotalrevenue.lasttwelvemonths", "op": "lte", "value": 1.0},
    {"field": "lastclosetevtotalrevenue.lasttwelvemonths", "op": "gt", "value": 0}
  ],
  "sort": {"field": "lastclosetevtotalrevenue.lasttwelvemonths", "asc": true},
  "size": 25,
  "enrich": true
}
```

- Filters are ANDed together and with the `universe` bounds. To narrow one screen, add a filter;
  to move every scan, edit `universe`.
- A list value expands to `[field, *values]`, for operators such as `btwn` and `is-in`.
- `description` states the observable condition, not the reason it might hold.
- `enrich` adds best-effort Yahoo snapshot columns (P/E, short %, ownership, analyst rating).
  These columns do not filter; a missing one shows as n/a.

## Units of the bundled fields

| Field | Units |
| :-- | :-- |
| `intradaymarketcap` | dollars |
| `lastclose52weeklow.lasttwelvemonths` | close ÷ 52-week low (1.15 = 15% above); **lags**, see below |
| `lastclose52weekhigh.lasttwelvemonths` | close ÷ 52-week high (0.50 = 50% below); **lags**, see below |
| `fiftytwowkpercentchange` | percent (-10 = down 10%) |
| `pctheldinsider`, `pctheldinst` | fraction (0.15 = 15%) |
| `short_percentage_of_float.value` | percent (15 = 15%) |
| `short_interest_percentage_change.value` | percent (-20 = down 20%) |
| `avgdailyvol3m` | shares per day |

The `lastclose52week*.lasttwelvemonths` fields lag the live quote. On 2026-10-31, a `≤ 1.0`
low query returned stocks 6–50% above their current 52-week low, and a 0.4–0.6 high query
returned one stock trading at its high. `fiftytwowkpercentchange` was current. Check each
match's current price against its 52-week range (`regularMarketPrice` against
`fiftyTwoWeekLow`/`fiftyTwoWeekHigh` in the raw quotes, or the `market-data` snapshot) before you
call a stock near its low or high.
