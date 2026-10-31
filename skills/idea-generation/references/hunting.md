# Hunting beyond the scanners

The scanners cover the frequent hunts. For others, such as spin-offs (Form 10-12B), tenders
(SC TO-T / SC TO-I), post-IPO lockups, buybacks, or insider selling, combine `sec-filings`,
`market-data`, and the web.

- **EDGAR full-text search:** `edgar.search_filings(query, forms=, items=, start_date=,
  end_date=, limit=)` returns at most 100 rows per page. Page with `fetch_more()`, and compare
  `.total` with the rows you fetched before claiming the list is complete.
- **Yahoo screener:** `yf.screen(yf.EquityQuery(...))`. Discover fields as described in
  `screens.md`.
- Company labels from EDGAR search carry tickers in parentheses. Convert `.` to `-` for Yahoo
  (`BRK-B`).
- A search hit shows that a term appears in a filing. Confirm the event, its status, and the
  date in the filing itself (and in later amendments).
