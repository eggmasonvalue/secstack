---
name: idea-generation
description: >-
  Idea generation for US-listed equities: find new tickers worth researching from insider
  buying, 13D blockholders, market screens, SEC full-text themes, investor events, or any other
  filing- or price-based hunt. Use when the user wants candidates, not work on a known company.
---

# Idea generation

The output is a shortlist of leads with sources; a match is a lead, not a thesis.

Run `python "<skill-dir>/scripts/<script>.py"` from the research workspace; `--help` is the flag
reference. Each scan writes a report to `./idea-cache/<route>/` and prints its path. The report
states what its matches mean, along with any coverage gaps. SEC routes need `EDGAR_IDENTITY`.
The universe is set by the market-cap bounds in `screens.json`; change them when the hunt calls
for it.

```bash
scan_insiders.py --date yesterday [--lookback 5] [--zscore 1.5]   # Form 4 buys + Schedule 13Ds
scan_market.py --list | --screen near-52wk-low [--size 10] | --all
search_themes.py --keyword "tariff" --since 2025-01-01 [--until 2026-06-17] [--limit 200]
scan_conferences.py --start 2026-06-16 --end 2026-06-20
```

| Read | When |
| :-- | :-- |
| `references/screens.md` | adding or changing a screen |
| `references/hunting.md` | a hunt the scanners don't cover |
