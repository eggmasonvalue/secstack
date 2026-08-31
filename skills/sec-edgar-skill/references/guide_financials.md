# Financials — XBRL statements, facts, and periods

Use XBRL for structured income statements, balance sheets, cash-flow statements, and
individual facts. `scripts/parse_financials.py` writes statements to accession-keyed CSVs.
It never substitutes a different filing when the requested filing period has no match.

## Select the filing

For ordinary annual or domestic quarterly reports:

```python
filings = company.get_filings(
    form=["10-K", "20-F", "40-F"],
    year=2025,
    amendments=False,
)
filing = filings.latest()
```

Pass `year` to `get_filings`, not `EntityFilings.filter()`, which does not accept it. Exclude
amendments for ordinary statement extraction because an amendment may lack the complete XBRL
statement tree.

When the exact record is known, prefer its accession:

```python
from edgar import find

filing = find("0000320193-25-000079")
```

The script equivalents are:

```bash
python scripts/parse_financials.py --ticker AAPL --year 2025 --statement all
python scripts/parse_financials.py --accession 0000320193-25-000079 --statement all
```

A missing period is an error. Read the nearby candidates in stderr and rerun deliberately;
do not silently use the latest report.

## Financial 6-Ks require candidate selection

A 6-K is a foreign private issuer's general current report, not a standardized quarterly
report. It can contain financing, governance, operational, or other disclosures. Some 6-Ks
carry tagged annual, half-year, nine-month, revised, or voluntary interim financial statements.

For a requested filing window, `parse_financials.py`:

1. prefers a matching original 10-Q when one exists;
2. otherwise surveys 6-K and 6-K/A filings in the window;
3. looks for XBRL metadata, statement objects, and financial attachment descriptions;
4. extracts when exactly one filing has parseable statements;
5. lists candidate accessions instead of guessing when several match;
6. identifies likely textual financial 6-Ks when no statements can be parsed.

Use the reported accession for a second, exact call. For a textual candidate, fetch that
accession with `fetch_filing.py --attachment list` and pull the relevant exhibit.

XBRL proves that tagged information exists; it does not by itself prove that the filing is a
calendar-quarter report. Verify statement period ends and durations before labeling the data.

## Parse statements

```python
xbrl = filing.xbrl()
print(xbrl.to_context())

income = xbrl.statements.income_statement()
balance = xbrl.statements.balance_sheet()
cash = xbrl.statements.cashflow_statement()
df = income.to_dataframe()
```

Statement accessors live on `xbrl.statements`; the cash-flow accessor is
`cashflow_statement()` without an underscore inside “cashflow.”

## Multi-period company financials

```python
financials = company.get_financials()
print(financials.to_context())
df = financials.income_statement().to_dataframe()
```

On the object returned by `get_financials()`, statement methods are direct rather than under
`.statements`.

Do not blindly average or sum rows across periods. A pull can mix current values with prior
comparatives. For balance-sheet instant facts, filter to the intended `period_instant`; for
income and cash-flow duration facts, verify `period_end` and duration. Quarterly, half-year,
nine-month, and annual durations are not interchangeable.

## Individual facts — US-GAAP and IFRS

```python
revenue_us = xbrl.get_fact("us-gaap:Revenues")
revenue_ifrs = xbrl.get_fact("ifrs-full:Revenue")
```

Foreign private issuers frequently report under IFRS. If a US-GAAP concept is absent, inspect
the filing taxonomy and use the corresponding IFRS or issuer-extension concept rather than
assuming the fact is missing.
