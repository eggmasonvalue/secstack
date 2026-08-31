# Institutional holdings and blockholders

Use the distilled 13F script for routine stock-, manager-, and manager-position questions. Use
raw EDGAR when a required filing field is not surfaced, the distilled result is missing or
inconsistent, or the user asks for source-level verification.

## Distilled 13F routes

```bash
# Which reporting managers disclosed this security?
python scripts/fetch_13f_holders.py --ticker AAPL

# Aggregate reporting-manager/share history
python scripts/fetch_13f_holders.py --ticker AAPL --history

# Latest complete disclosed portfolio for a manager
python scripts/fetch_13f_holders.py --manager "Berkshire Hathaway"

# Latest quarter-over-quarter share changes plus filing history
python scripts/fetch_13f_holders.py --manager "Berkshire Hathaway" --history

# One manager's disclosed position history in one security
python scripts/fetch_13f_holders.py --manager 0001067983 --ticker AAPL
```

The script resolves manager CIKs and security CUSIPs internally. Reports expose underlying SEC
periods and identifiers rather than intermediary-provider links. A successful report is the
complete normal surface; do not browse the provider looking for omitted routine fields.

13F is delayed and incomplete as a picture of ownership. It covers reportable long positions
of filing managers, not retail holders, all institutions, short positions, or every security.
Treat “who owns this stock?” as shorthand for “which Form 13F managers disclosed this CUSIP?”
Reconcile multiple share classes and CUSIPs before aggregating.

## Raw 13F via edgartools

A 13F is filed by the investment manager, not the operating company:

```python
manager = Company("Magnetar Capital LLC")
filing = manager.get_filings(form="13F-HR", amendments=False).latest()
thirteen_f = filing.obj()
holdings = thirteen_f.holdings
```

Use raw holdings for voting authority, investment discretion, other-manager fields, precise
amendment treatment, or verification. Holdings are already a DataFrame; the 13F object does
not need `.to_dataframe()`.

An operating company's CIK normally does not file the 13F portfolios that hold its stock. A
stock-centric reverse lookup therefore belongs to the distilled route.

## Schedules 13D and 13G

Schedules 13D and 13G disclose beneficial ownership above the applicable threshold under
different eligibility and reporting regimes. Do not reduce the distinction to “active” versus
“passive”: Schedule 13G also covers qualified institutional and exempt investors.

Query the schedule names used by EDGAR, including `SC` prefixes and amendments:

```python
schedules = company.get_filings(form=["13D", "13G", "SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A"])
schedule = schedules.latest().obj()
schedule.reporting_persons
schedule.issuer_info
schedule.total_percent
schedule.items.item4_purpose_of_transaction
```

These parse into structured schedule objects rather than item-addressable company reports.
Fields such as the 13D purpose narrative live on `schedule.items`; there is no generic
`schedule["Item 4"]` contract.

Follow the amendment chain for a reporting person instead of treating every accession as a
separate current holder. Preserve reporting-person identity, share class, measurement date,
shares, percentage, voting/dispositive power, and accession.

Older schedules may lack structured XML. When parsed fields are absent, fetch the exact
accession as full Markdown and inspect the ownership tables and Item 4 narrative directly.
