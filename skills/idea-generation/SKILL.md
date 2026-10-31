---
name: idea-generation
description: >-
  Idea generation for US-listed equities: find new tickers worth researching from insider
  buying, 13D blockholders, market screens, SEC full-text themes, investor events, or any other
  filing- or price-based hunt. Use when the user wants candidates, not work on a known company.
---

# Idea generation

The output is a shortlist of leads with sources. A match earns a closer look, not a thesis.

## Run

Run `python "<skill-dir>/scripts/<script>.py"` from the research workspace; `--help` is the flag
reference. Each scan writes `./idea-cache/<route>/<date-or-range>.md` and prints its path, and a
rerun overwrites it. SEC routes need `EDGAR_IDENTITY="Name email@domain"`; screens do not. The
universe is Yahoo `us` equities between the market-cap bounds in `screens.json` (currently
$50M–$10B). Those bounds are configuration, so change them when the hunt calls for it.

```bash
scan_insiders.py --date yesterday [--lookback 5] [--zscore 1.5]   # Form 4 buys + Schedule 13Ds
scan_market.py --list | --screen near-52wk-low [--size 10] | --all
search_themes.py --keyword "tariff" --since 2025-01-01 [--until 2026-06-17] [--limit 200]
scan_conferences.py --start 2026-06-16 --end 2026-06-20
```

## What each report means

- **Insiders.** Counts only Form 4 code `P`, and only rows with positive shares. A *cluster*
  means at least two distinct reporting owners (matched by CIK, else by name) bought within the filing window. *Dip* and
  *rip* tags compare the 22-trading-day return as of the **transaction date** with the stock's
  prior 252 rolling 22-day returns, so a historical scan never uses today's prices; with fewer
  than 80 closes the tag is n/a. A 13D row names a blockholder; Item 4 of the filing says
  whether there is a plan. `DISCORD_WEBHOOK_URL` enables optional alerts.
- **Screens.** These are Yahoo screener predicates and say nothing about why a stock qualifies.
  The 52-week low/high ratio fields behind `near-52wk-low` and `fallen-from-grace` lag the live
  quote. Before you repeat a "near low" claim, check the hit with `market-data`, whose snapshot
  prints the 52-week high and low. Read `references/screens.md` before adding or editing a screen; field units are
  inconsistent.
- **Themes.** A full-text hit proves a word appears, not that the business is exposed to it;
  open the linked filing. `--limit` caps documents before issuer deduplication, and the report
  says when the server had more.
- **Events.** The classifier is heuristic. It drops "conference call" and "forum selection"
  boilerplate and needs attendance language such as "will present". Confirm the event and its
  date in the filing.
- **Coverage.** An empty report is a valid result. A nonzero exit or a coverage note means
  retrieval was incomplete. Omitted rows (unparseable filings, tickers Yahoo cannot price) are
  listed, never silently dropped. Market-cap lookups are cached for 24 hours.

## Hunting beyond the scanners

The scanners encode the frequent hunts. For others, such as spin-offs (Form 10-12B), tenders
(SC TO-T / SC TO-I), post-IPO lockups, buybacks, or insider selling, combine `sec-filings`, `market-data`,
and the web. Two ways to query directly:

- **EDGAR full-text search:** `edgar.search_filings(query, forms=, items=, start_date=,
  end_date=, limit=)` returns at most 100 rows per page. Page with `fetch_more()` and compare
  `.total` with what you fetched before claiming completeness.
- **Yahoo screener:** `yf.screen(yf.EquityQuery(...))`, with fields discovered as described in
  `references/screens.md`.

Labels from EDGAR search carry tickers in parentheses. Convert `.` to `-` for Yahoo (`BRK-B`).
