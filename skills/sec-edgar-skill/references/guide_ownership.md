# Insider ownership — Forms 3, 4, and 5

Use this guide for Section 16 ownership reports by directors, officers, and 10% holders. For
annual-meeting beneficial ownership, governance, and compensation, read `guide_proxy.md`. For
external blockholders and institutional managers, read `guide_holdings.md`.

## What the forms mean

- **Form 3:** initial beneficial-ownership statement when a person becomes subject to Section 16.
- **Form 4:** changes in ownership, generally reported within two business days.
- **Form 5:** selected annual transactions that were exempt or reported late.

There is no `company.get_insiders()` requirement for retrieval; query the forms directly:

```python
form4s = company.get_filings(form="4", amendments=False)
latest = form4s.latest().obj()
print(latest.insider_name, latest.position)
dataframe = latest.to_dataframe()
```

The bundled `fetch_insider_trades.py` is the normal company-level activity route. It queries
original Form 4s to avoid counting an original and amendment twice, distinguishes transaction
date from filing date, and reports partial parser coverage. Inspect a Form 4/A directly when a
specific correction matters.

## Transaction data

Use the DataFrame or activity helper rather than assuming internal transaction collections are
ordinary lists:

```python
dataframe = latest.market_trades
option_exercises = latest.option_exercises
for activity in latest.get_transaction_activities():
    print(
        activity.transaction_type,
        activity.code,
        activity.shares,
        activity.price_per_share,
    )
```

Common transaction codes include:

- `P` — open-market purchase;
- `S` — open-market sale;
- `M` — option exercise;
- `F` — tax withholding;
- `A` — award or grant;
- `G` — gift.

Only code `P` is an open-market insider purchase. Preserve the transaction date, filing date,
accession, shares, price, and post-transaction holdings so the record remains auditable.

## Foreign private issuers

Foreign private issuers, including Canadian MJDS filers, are generally exempt from Section 16
Forms 3/4/5. Absence of Form 4 filings is therefore not evidence that no insider transaction
occurred. Check the home-jurisdiction regulator when the task requires that information.

Foreign-issuer compensation and management ownership are generally found in Form 20-F Item 6;
see `guide_proxy.md` for the disclosure map.
