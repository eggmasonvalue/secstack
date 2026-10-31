---
name: sec-filings
description: >-
  SEC EDGAR filings for US-listed issuers: 10-K/10-Q/8-K, 20-F/40-F/6-K, exhibits, XBRL
  financial statements, proxies, Form 4 insider trades, 13F institutional holders, and 13D/13G
  blockholders. Use when a fact should come from, or be checked against, the filing itself.
---

# SEC filings

Pull filings to disk and read only the slice you need.

Run `python "<skill-dir>/scripts/<script>.py"` from the research workspace, so the cache lands
in `./sec-cache`. SEC requests need `EDGAR_IDENTITY="Name email@domain"`. Read `--help` before
choosing selectors. A nonzero exit means retrieval failed; it is not evidence that the record is
absent. When something misbehaves, run `test_setup.py --live`.

```bash
orient.py --ticker AAPL                       # identity, form mix, recent accessions
fetch_filing.py --ticker AAPL --form 10-K --year 2025 [--section "Item 1A" | --section list]
fetch_filing.py --accession 0000320193-25-000079 [--attachment list | "ex-99.1" | all]
fetch_filing.py --ticker AAPL --form 8-K --on-or-before 2026-06-15
fetch_filings.py --ticker AAPL --form 10-Q --start-year 2022 --end-year 2024 [--attachments]
parse_financials.py --ticker AAPL --year 2025 [--quarter 2] [--statement income]
parse_financials.py --accession 0000320193-25-000079
fetch_insider_trades.py --ticker AAPL [--start 2025-06-01] [--buys-only]
fetch_13f_holders.py --ticker AAPL [--history | --year 2025 --quarter 2]
fetch_13f_holders.py --manager "Berkshire Hathaway" [--history]
fetch_13f_holders.py --manager 0001067983 --ticker AAPL      # one manager's position history
```

Once you have an accession, select by it.

| Read | When |
| :-- | :-- |
| `references/ownership.md` | interpreting Form 4, 13F, 13D/13G, proxy ownership, compensation, or governance |
| `references/edgartools.md` | writing inline `edgartools` code because no script covers the job |
