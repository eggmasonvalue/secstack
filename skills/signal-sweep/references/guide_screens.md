# Screen Customization Guide

Read this guide when adding or changing a query in `screens.json`. Yahoo's screener schema evolves,
so inspect the installed `yfinance` version instead of treating examples here as a complete field
catalog.

## Discover the current schema

```python
import yfinance as yf

query = yf.EquityQuery("eq", ["region", "us"])
print(query.valid_fields)  # fields grouped by category
print(query.valid_values)  # accepted values for equality fields
help(yf.EquityQuery)
help(yf.screen)
```

Use the exact field spelling and value units returned at runtime. Before retaining a new screen,
run it with a small `--size`, inspect several raw matches, and confirm that the provider's units and
sort direction mean what the description says.

## Definition format

```json
{
  "id": "my-screen",
  "name": "Human-Readable Name",
  "emoji": "📊",
  "description": "The conditions this query applies",
  "filters": [
    {"field": "some.field", "op": "gte", "value": 42}
  ],
  "sort": {"field": "some.field", "asc": true},
  "size": 25,
  "enrich": true
}
```

- `id` is the unique CLI slug.
- `name`, `emoji`, and `description` label the report; describe the observable condition rather
  than asserting why it occurred.
- `filters` are combined with logical AND.
- `sort` declares the ranking field and direction.
- `size` is the maximum number of screener rows returned before enrichment.
- `enrich` adds Yahoo snapshot fields for each returned ticker.

Scalar values become `[field, value]` operands. A JSON list becomes `[field, *values]`, which
supports operators such as `btwn` and `is-in` when accepted by the installed API.

## Fields used by the bundled screens

These are examples, not the limits of `EquityQuery`:

| Field | Meaning and units used here |
|---|---|
| `region` | Yahoo region code; the default universe uses `us`. |
| `intradaymarketcap` | Market capitalization in dollars. |
| `lastclose52weeklow.lasttwelvemonths` | Last close divided by the 52-week low (`1.15` = 15% above). |
| `lastclose52weekhigh.lasttwelvemonths` | Last close divided by the 52-week high (`0.50` = 50% below). |
| `fiftytwowkpercentchange` | 52-week percentage change (`-10` = down 10%). |
| `avgdailyvol3m` | Three-month average daily share volume. |
| `pctheldinsider`, `pctheldinst` | Ownership fractions (`0.15` = 15%). |
| `short_percentage_of_float.value` | Short percentage of float (`15` = 15%). |
| `short_interest_percentage_change.value` | Percentage change in short interest (`-20` = down 20%). |

Do not infer more than the field establishes. For example, low institutional ownership does not by
itself prove that a stock is undiscovered, and a flat annual return does not prove that the market
ignored new information.

## Universe bounds

The `universe` object is injected into every query:

```json
"universe": {
  "region": "us",
  "market_cap_min": 50000000,
  "market_cap_max": 10000000000
}
```

An additional screen-level market-cap condition combines with these bounds. Change the universe
object when the whole scan should use different bounds; add a filter when only one screen needs to
be narrower.

## Enrichment

When enabled, enrichment adds best-effort Yahoo snapshot fields such as price, market cap, sector,
industry, P/E, short ownership, insider/institutional ownership, and analyst rating. These fields
are not part of the screen predicate unless the definition explicitly filters on them. Missing
enrichment remains `n/a` and does not invalidate the underlying screener match.

## Example

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

Add the object to `screens.json`, then inspect a small run:

```bash
python "<skill-dir>/scripts/scan_market.py" --screen positive-low-ev-revenue --size 5
```
