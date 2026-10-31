# edgartools inline

Use this when no script flag covers the job. When unsure of a method, ask the library itself:
`obj.docs`, `obj.docs.search("attachments")`, `obj.to_context()`.

## Preamble

The scripts do this on import. Inline code has to do it explicitly:

```python
import os, sys

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")  # edgartools reprs contain emoji; cp1252 crashes
try:
    import truststore

    truststore.inject_into_ssl()  # corporate TLS inspection otherwise breaks HTTPS
except ImportError:
    pass
import edgar

edgar.set_identity(os.environ["EDGAR_IDENTITY"])
```

## Companies and filings

```python
from edgar import Company, find

company = Company("AAPL")  # ticker, CIK, or name
company.tickers  # a list; there is no company.ticker
filings = company.get_filings(form="10-Q", year=2025, quarter=2, amendments=False)
filings = company.get_filings(date="2024-01-01:2025-12-31")
filing = find("0000320193-25-000079")  # exact accession
filing.markdown()  # whole filing; it takes no section argument and ignores one
```

- `year` and `quarter` filter on the *filing* date, and `year` belongs on `get_filings`.
  `EntityFilings.filter()` does not accept it.
- A company's form mix changes over time (domestic to foreign filer, a new listing, a
  reorganization), so survey several years before concluding a form is absent.

## Sections and exhibits

```python
report = filing.obj()  # TenK, TenQ, CurrentReport, TwentyF, ...
report.items  # the item codes actually present
report["Item 1A"]  # None when absent; 10-Q keys are "Part I, Item 2" style

attachments = list(filing.attachments)  # use list indices
attachments[1].markdown()
```

Raw `filing.attachments[i]` looks attachments up by SEC sequence number, which can skip values.
Cast to a list first. Free-form forms (DEF 14A, 6-K, S-1, 424B) have no `.items`. A 6-K or
40-F body is often just a cover note, with the substance in an exhibit.

## XBRL

```python
xbrl = filing.xbrl()
xbrl.statements.income_statement()  # also balance_sheet(), cashflow_statement()
xbrl.get_fact("us-gaap:Revenues")  # IFRS filers: "ifrs-full:Revenue"

financials = company.get_financials()  # multi-period; statement methods sit directly on it
financials.income_statement().to_dataframe()
```

A pull can mix current values with prior-period comparatives. Filter balance-sheet facts on
`period_instant`, and filter income and cash-flow facts on period end and duration, before you
sum, average, or compare them.

## Ownership forms

```python
form4 = company.get_filings(form="4", amendments=False).latest().obj()
form4.to_dataframe()  # rows with Code, Shares, Price, Remaining Shares
form4.market_trades, form4.option_exercises

# Forms were renamed in Dec 2024; history needs both spellings. Bare "13D" matches nothing.
forms = ["SCHEDULE 13D", "SCHEDULE 13D/A", "SC 13D", "SC 13D/A"]  # same pattern for 13G
schedule = company.get_filings(form=forms).latest().obj()  # one filing; holders need each person's chain
schedule.issuer_info, schedule.reporting_persons, schedule.total_percent
schedule.items.item4_purpose_of_transaction  # no schedule["Item 4"] contract

manager = Company("Magnetar Capital LLC")  # 13Fs are filed by the manager, not the issuer
manager.get_filings(form="13F-HR", amendments=False).latest().obj().holdings  # a DataFrame
```

Older schedules can lack structured XML. When parsed fields come back empty, read the
filing's Markdown directly. The daily index (`edgar.get_filings(...)`) lists each schedule under
both the filer and the subject company, so take the issuer from `issuer_info`.
