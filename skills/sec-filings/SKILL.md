---
name: sec-filings
description: >-
  SEC EDGAR filings for US-listed issuers: 10-K/10-Q/8-K, 20-F/40-F/6-K, exhibits, XBRL
  financial statements, proxies, Form 4 insider trades, 13F institutional holders, and 13D/13G
  blockholders. Use when a fact should come from, or be checked against, the filing itself.
---

# SEC filings

The filing is the primary record. Pull it to disk, then read only the slice you need.

## Run

Run `python "<skill-dir>/scripts/<script>.py"` from the research workspace so `./sec-cache`
lands beside the work (`--cache-dir` or `$SEC_CACHE_DIR` moves it). SEC requests need
`EDGAR_IDENTITY="Name email@domain"`; without it the SEC returns 403. `test_setup.py --live`
diagnoses the environment, and `--help` is the flag reference.

Artifact commands print absolute paths on stdout and progress on stderr. A nonzero exit is a
retrieval failure, never evidence that the record does not exist.

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

Skip `orient.py` when you already have an accession or a cached file. Once you have an
accession, use it: it is globally unique and removes every date and form guess.

## Gotchas

- **Selectors use the filing date.** `--year`/`--quarter` are the calendar year and quarter the
  filing was *filed*, so a December-FYE company's FY2024 10-K is `--year 2025`.
  `--on-or-before` can land on an older filing; stderr names the one it picked.
- **Amendments.** Single-filing selectors exclude amendments because a 10-K/A may carry only the
  changed items. `fetch_filings.py` keeps originals and amendments, and `--accession` fetches
  either.
- **Item codes.** 10-Q items are namespaced by Part: a bare `"Item 2"` resolves to Part II
  (unregistered sales), while the MD&A is `"Part I, Item 2"`. On an 8-K, `--section list` tells
  you what the 8-K is about (2.02 earnings, 5.02 officer change, 5.07 vote results) before you
  read it. 20-F uses its own scheme: 3.D risk factors, 5 MD&A, 6 management and compensation,
  7.A major holders.
- **Exhibits hold the substance** of 6-Ks, 40-Fs, and many 8-Ks, usually in ex-99.1. An empty
  body or a cover note means you should run `--attachment list`.
- **Free-form filings** (DEF 14A, 6-K, S-1, 424B) are not item-addressable. Fetch them whole,
  read the filing's own table of contents in the first ~100 lines, then grep. `rg -n '^#'`
  maps a periodic report's headings.
- **XBRL.** `parse_financials.py` never substitutes a different period. When several 6-Ks carry
  statements it lists their accessions instead of guessing. Check period end and duration
  before you label a figure quarterly, and remember that IFRS filers tag `ifrs-full:` concepts.
- **Form 4.** Only code `P` is an open-market purchase. The transaction date and the filing
  date differ. "Remaining shares" is one ownership line, not the insider's total. Foreign
  private issuers file no Form 4, so absence of filings is not absence of trading.
- **13F** comes through a distilled 13f.info route that reports SEC periods, CIKs, and
  accessions. It reports share counts only, never dollars. A quarter becomes "latest" about 50
  days after quarter end. Go to raw EDGAR only for fields the route omits (voting authority,
  investment discretion) or for verification.
- **13D/13G form names changed in December 2024.** Query both `SCHEDULE 13D`/`13D/A` and the
  older `SC 13D`/`SC 13D/A` (and likewise for 13G). The daily index lists each schedule under
  both the filer and the subject company, so take the issuer from `obj().issuer_info`.
- **Cache.** Accession-keyed artifacts are reused; pass `--force` to regenerate them. Insider and
  13F summaries refresh on every run. ripgrep skips the git-ignored cache unless you point it
  at the directory or pass `--no-ignore`.
- **Timing.** A release can reach issuer IR before it reaches EDGAR, so check both for a
  same-day event.

## References

| Read | When |
| :-- | :-- |
| `references/edgartools.md` | writing inline `edgartools` code because no flag covers the job |
| `references/ownership.md` | interpreting Form 4, 13F, 13D/13G, proxy ownership, compensation, or governance |
