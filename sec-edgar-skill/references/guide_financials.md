# Financials — XBRL statements and facts

How to pull structured financial statements (Income, Balance Sheet, Cash Flow) and
individual XBRL facts, for both US-GAAP and IFRS filers. `scripts/parse_financials.py`
wraps statement extraction to CSV.

## Get filings for parsing

```python
filings = company.get_filings(form=["10-K", "20-F", "40-F"], year=2024, amendments=False)
filing = filings.latest()
```

> **Pass `year` to `get_filings`, not `.filter()`.** `EntityFilings.filter(year=...)`
> raises `TypeError` — `filter` doesn't accept `year`.
>
> **Use `amendments=False`.** Amendments (`10-K/A`, etc.) often carry only minor text
> changes and lack complete XBRL statement trees; exclude them to get the primary
> statements.

Annual reports (10-K / 20-F / 40-F) and quarterly reports (10-Q / 6-K) carry the
complete statement trees and can be parsed to CSV using `parse_financials.py`.

## Parse statements from a filing

```python
xbrl = filing.xbrl()
print(xbrl.to_context())                        # lists available statements

income  = xbrl.statements.income_statement()
balance = xbrl.statements.balance_sheet()
cash    = xbrl.statements.cashflow_statement()  # note: "cashflow", no underscore
df = income.to_dataframe()
```

> Statement accessors live on `xbrl.statements`, not on the `XBRL` object itself, and the
> cash-flow method is `cashflow_statement()` (no underscore in "cashflow").

## Multi-period history from the company

```python
fin = company.get_financials()
print(fin.to_context())
df = fin.income_statement().to_dataframe()      # methods are directly on this object
```

On the object returned by `get_financials()`, the statement methods are direct — not
under `.statements`.

> **Don't blindly `.mean()` / `.sum()` across periods.** A multi-period pull mixes
> current-period values with prior-period comparatives. For balance-sheet (instant)
> facts, filter `period_instant == report_date`; for income/cash-flow (duration) facts,
> filter `period_end == report_date` and sanity-check the duration (~90 days quarterly,
> ~360 days annual). Otherwise you average current figures with comparatives and corrupt
> the series.

## Individual facts — US-GAAP and IFRS

```python
rev_us   = xbrl.get_fact("us-gaap:Revenues")
rev_ifrs = xbrl.get_fact("ifrs-full:Revenue")   # foreign issuers often file IFRS
```

If US-GAAP tags come back empty for a foreign private issuer, try the IFRS equivalent —
20-F filers frequently report under IFRS rather than US-GAAP.
