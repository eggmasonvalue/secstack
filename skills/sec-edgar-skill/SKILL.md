---
name: sec-edgar-skill
description: >-
  Retrieve, verify, and inspect SEC filings and filing-derived financial, ownership,
  compensation, and governance data. Use when current or auditable evidence must be pulled
  from EDGAR: 10-K/10-Q/8-K, 20-F/40-F/6-K, XBRL statements, Form 4 insider transactions,
  13F institutional holdings, 13D/13G blockholders, or proxy disclosures. The generic filing
  tools also accept other SEC forms. Do not trigger merely because an analysis mentions
  financials; use it when source material needs to be obtained or checked.
---

# SEC EDGAR Research Skill

Retrieve filing-derived evidence without loading entire filings into context.

## Role in the research stack

Prefer an SEC filing over model memory or a secondary summary for facts the filing discloses.
When an analytical skill is driving the task, provide the requested evidence and provenance
without substituting an investment conclusion. Use company investor relations, another
regulator, or reputable web sources when the information is not yet on EDGAR or is outside
EDGAR's scope.

## Runtime and paths

Resolve bundled paths relative to this `SKILL.md`. Invoke scripts by their resolved absolute
path while keeping the shell working directory at the research workspace; this keeps the
default `./sec-cache` beside the work rather than inside the installed skill. Alternatively,
pass `--cache-dir`.

SEC requests require a real contact identity:

```bash
export EDGAR_IDENTITY="Jane Analyst jane@example.com"
```

Every SEC-facing script also accepts `--identity`. The 13f.info convenience script and local
`list_headings.py` do not need an SEC identity. Diagnose the environment with:

```bash
python "<skill-dir>/scripts/test_setup.py" --live
```

## Choose the shortest reliable route

1. **Orient when discovery is needed.** Run `orient.py` when the relevant form or accession is
   unknown. It prints company identity, the recent filing mix, and recent accessions without
   downloading filing contents. Skip orientation when the user supplied an accession or
   cached file, or when the task is solely a 13f.info convenience query.
2. **Select exactly.** Use company/form/period selectors for ordinary retrieval. Use
   `--accession` when the user supplied one or a candidate-listing command identified one.
   `--on-or-before` is deliberately explicit: it may select an earlier filing.
3. **Keep large documents on disk.** Download Markdown or CSV into the cache. Search cached
   Markdown with native grep/ripgrep, then read only relevant line ranges.
4. **Prefer structured routes where they are sound.** Pull item-addressable sections and XBRL
   statements directly. For free-form filings, inspect their contents and attachments.
5. **Treat failure as failure.** Do not turn a network or parser error into a factual “no data”
   conclusion. Use the reported candidates, accession route, relevant guide, or edgartools
   `.docs` to recover.

For very recent disclosures, check EDGAR promptly but do not assume a filing must already
exist. A company release can precede its SEC filing.

## Cache behavior

The root resolves as `--cache-dir` > `$SEC_CACHE_DIR` > `./sec-cache`. Filing artifacts use:

```text
<TICKER>/<FORM>_<FILING-DATE>_<ACCESSION>[__<section-or-attachment>].md
<TICKER>/<FORM>_<FILING-DATE>_<ACCESSION>__<statement>.csv
```

Accession-keyed filing artifacts are immutable enough to reuse by default; pass `--force` to
regenerate them. Rolling insider and 13F summaries refresh because late filings or amendments
can change their source set. If ripgrep skips a gitignored cache, point it directly at the
company directory or use `--no-ignore`.

## Reference guides

Read only the guide needed for the question:

| Guide | Use it for |
| :-- | :-- |
| `references/guide_core.md` | Company resolution, filing discovery, `.to_context()`, exact accessions, and `.docs`. |
| `references/guide_filings.md` | Full filing text, SEC item codes, free-form navigation, and exhibits. |
| `references/guide_financials.md` | XBRL statements/facts, period semantics, and noisy financial 6-Ks. |
| `references/guide_ownership.md` | Forms 3/4/5, insider transactions, and Section 16 limitations. |
| `references/guide_proxy.md` | Beneficial ownership, board/governance, compensation, related parties, auditors, dilution, proposals, and voting. |
| `references/guide_holdings.md` | 13F institutional holdings and 13D/13G blockholder schedules. |

## Script routes

`--help` is the authoritative flag reference. Artifact-producing commands emit absolute paths
to stdout and progress to stderr; orientation, diagnostics, and list modes print reports.

```bash
# Discover forms and recent accessions
python "<skill-dir>/scripts/orient.py" --ticker AAPL

# Filing by ordinary selectors or exact accession
python "<skill-dir>/scripts/fetch_filing.py" --ticker AAPL --form 10-K --year 2025
python "<skill-dir>/scripts/fetch_filing.py" --accession 0000320193-25-000079

# One item or the filing's actual item list
python "<skill-dir>/scripts/fetch_filing.py" --ticker AAPL --form 10-K --year 2025 --section "Item 1A"
python "<skill-dir>/scripts/fetch_filing.py" --accession 0000320193-25-000079 --section list

# An exhibit, or the nearest matching filing on/before a date
python "<skill-dir>/scripts/fetch_filing.py" --ticker WIX --form 6-K --attachment "ex-99.1"
python "<skill-dir>/scripts/fetch_filing.py" --ticker AAPL --form 8-K --on-or-before 2026-06-15

# Bulk archive: intentionally includes originals and amendments
python "<skill-dir>/scripts/fetch_filings.py" --ticker AAPL --form 10-Q --start-year 2022 --end-year 2024

# Structured statements; period selection never falls back to a different report
python "<skill-dir>/scripts/parse_financials.py" --ticker AAPL --year 2025 --statement all
python "<skill-dir>/scripts/parse_financials.py" --accession 0000320193-25-000079 --statement all

# Local heading map
python "<skill-dir>/scripts/list_headings.py" --file sec-cache/AAPL/<filing>.md

# Form 4 transactions
python "<skill-dir>/scripts/fetch_insider_trades.py" --ticker AAPL
python "<skill-dir>/scripts/fetch_insider_trades.py" --ticker AAPL --start 2025-06-01 --buys-only

# Distilled 13F queries
python "<skill-dir>/scripts/fetch_13f_holders.py" --ticker AAPL
python "<skill-dir>/scripts/fetch_13f_holders.py" --ticker AAPL --history
python "<skill-dir>/scripts/fetch_13f_holders.py" --manager "Berkshire Hathaway"
python "<skill-dir>/scripts/fetch_13f_holders.py" --manager 0001067983 --ticker AAPL
```

The 13F convenience script uses 13f.info to resolve and distill routine holdings queries but
its reports expose the underlying SEC period, CIK, and accession rather than the intermediary.
Use raw EDGAR only for fields the distilled route does not provide—such as voting authority or
investment discretion—or to verify missing or inconsistent data.

## Important filing semantics

- `fetch_filing.py` selects original forms for ordinary company/form requests because an
  amendment may contain only changed items. Exact `--accession` retrieval can fetch either.
- `fetch_filings.py` intentionally preserves both originals and amendments in a bulk archive.
- A 6-K is not a standardized quarterly report. `parse_financials.py` prefers a matching 10-Q;
  otherwise it classifies financial 6-K candidates. If several contain statements, it lists
  their accessions instead of guessing.
- Form 4 reports distinguish transaction date from filing date and expose partial parsing.
- A successful generated report is complete for its advertised fields. Do not browse the
  intermediary provider after a successful 13F query; use the underlying SEC accession when
  deeper verification is required.
