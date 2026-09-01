---
name: signal-sweep
description: >-
  Discover US-listed equity research candidates by scanning Form 4 purchases and Schedule 13D
  filings, configurable Yahoo Finance market screens, SEC filing full-text for a keyword or
  theme, and 8-K disclosures for investor events. Use when the user wants new tickers or asks
  who is buying, what companies match a market condition, which issuers mention a theme, or who
  is presenting at investor events. Use company-research skills instead when the ticker is
  already known and the task is diligence rather than discovery.
---

# Signal Sweep

Produce auditable candidate lists for further research. A match is a lead, not an investment
thesis.

## Runtime and universe

Resolve bundled paths relative to this `SKILL.md` and invoke scripts by absolute path while keeping
the shell working directory at the research workspace. Generated reports then land in the
workspace's `./signal-sweep-cache`; pass `--cache-dir` to put them elsewhere.

The packaged SecStack profile already exposes this skill's Python dependencies. For standalone
use, run `uv sync --project "<skill-dir>"`, then activate that environment or prefix the commands
below with `uv run --project "<skill-dir>"`. SEC-facing routes require `EDGAR_IDENTITY`; market
screens do not:

```bash
export EDGAR_IDENTITY="Jane Analyst jane@example.com"
```

The default universe is Yahoo Finance equities in region `us` between the market-cap bounds in
`screens.json` (currently $50M–$10B). Those bounds are configuration, not a definition of what is
investable, and can be changed for the task.

## Routes

### Insider purchases and Schedule 13D filings

```bash
python "<skill-dir>/scripts/scan_insiders.py" --date yesterday --lookback 5
```

The scan counts only Form 4 transaction code `P`. It reports:

- **clusters** — purchases by at least two distinct reporting owners in filings received during
  the scan window; and
- **dip/rip context** — a purchase whose trailing 22-trading-day return is unusually negative or
  positive relative to that stock's prior rolling returns (default threshold ±1.5 standard
  deviations).

Transaction date and filing date remain distinct. The move is measured as of the transaction date,
so a historical scan does not use today's price action. Schedule 13D and 13D/A matches are labeled
as blockholder filings, not presumed activism; inspect the linked filing for purpose and ownership.
Use `--zscore` only when the task calls for a different sensitivity. Prefer the
`DISCORD_WEBHOOK_URL` environment variable for optional alerts.

### Configurable market screens

```bash
python "<skill-dir>/scripts/scan_market.py" --list
python "<skill-dir>/scripts/scan_market.py" --screen near-52wk-low
python "<skill-dir>/scripts/scan_market.py" --all
```

`screens.json` contains the bundled query definitions. Results are ranked by each screen's declared
sort field and can be enriched with Yahoo snapshot fields. Read `references/guide_screens.md` only
when adding or changing a screen; it shows how to discover fields from the installed `yfinance`
version rather than treating a static list as exhaustive.

### SEC full-text theme search

```bash
python "<skill-dir>/scripts/search_themes.py" --keyword "cannabis" --since 2026-01-01
python "<skill-dir>/scripts/search_themes.py" --keyword "tariff" --since 2025-01-01 --until 2026-06-17
```

This searches EDGAR's full-text index, deduplicates the returned filing matches by issuer, applies
the configured market-cap universe, and links the most recent matching filing. `--limit` caps
filing documents before issuer deduplication; the report discloses when the server had more matches
than were fetched. A keyword match establishes mention, not economic exposure—open the linked filing
and inspect context before carrying a candidate forward.

### Investor-event discovery

```bash
python "<skill-dir>/scripts/scan_conferences.py" --start 2026-06-16 --end 2026-06-20
```

This searches 8-K full text for third-party conferences, fireside chats, forums, symposia, and
issuer-hosted investor or capital-markets days. It uses both Reg FD and Other Events disclosures;
it is not an Item 8.01-only scan. The report links each source accession and discloses query
truncation or retrieval failures. Classification is heuristic, so verify the event and date in the
filing.

## Output and failure semantics

Each successful scan writes a date- or range-keyed Markdown report under
`signal-sweep-cache/<route>/` and emits its absolute path to stdout. Re-running the same request
refreshes that report. Shared Yahoo market-cap lookups used by SEC-facing routes have a 24-hour disk
cache.

Reports distinguish a valid empty result from incomplete retrieval. Source-query, index, and total
parser failures exit nonzero. Recoverable omissions—such as an individually unparseable filing or
an unavailable Yahoo market cap—remain explicit coverage notes rather than becoming false no-data
claims.
