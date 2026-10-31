# SEC Filings

An agent skill for retrieving, verifying, and inspecting SEC filings and filing-derived
financial, ownership, compensation, and governance data without loading whole filings into
context.

## Included resources

- `SKILL.md` — commands, filing semantics, and gotchas.
- `references/edgartools.md` — inline `edgartools` API for jobs no script covers.
- `references/ownership.md` — Form 4, 13F, 13D/13G, proxy, and governance semantics.
- `scripts/` — command-line retrieval and extraction helpers.

## Install this skill

From the SecStack repository:

```bash
npx skills add eggmasonvalue/secstack --skill sec-filings
```

SecStack's profile bootstrap installs the Python dependencies automatically. For a standalone
installation, run from this directory:

```bash
uv sync
```

Then invoke the scripts with that environment, or configure the harness to use its Python.

## SEC identity

SEC requests require a real contact identity under the SEC fair-access policy:

```bash
export EDGAR_IDENTITY="Jane Analyst jane@example.com"
```

Do not commit it. The 13f.info convenience queries do not require an
SEC identity. Verify the full environment with:

```bash
uv run python scripts/test_setup.py --live
```

## Retrieval model

1. Survey a company's filing mix when the relevant form is unknown.
2. Select a filing by company/form/period or exact SEC accession.
3. Save filing text as Markdown and statements as CSV.
4. Search the local cache and read only relevant ranges.
5. Use structured item or XBRL extraction where the filing supports it.

Accession-keyed filing artifacts are reused unless `--force` is passed. Rolling ownership
summaries refresh because their source set can change.

## Data sources

Filing data comes from SEC EDGAR through the open-source `edgartools` library. Routine 13F
holder, manager, and position-history queries are distilled through 13f.info; generated reports
surface the underlying SEC reporting period, manager CIK, and accession rather than provider
navigation links. Raw EDGAR remains the verification and deep-field route.

---

Part of the [SecStack skills](https://github.com/eggmasonvalue/secstack) collection.
