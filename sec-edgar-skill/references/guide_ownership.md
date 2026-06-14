# Ownership & compensation — insiders, proxies, and exec pay

Two related questions about the people who run and own a company: what insiders are
buying and selling (Forms 3/4/5), and how executives are paid (the DEF 14A proxy, or
Form 20-F Item 6 for foreign issuers). For *external* 5%+ holders and institutions, see
`guide_holdings.md` instead.

## Insider transactions (Forms 3, 4, 5)

There is no `company.get_insiders()`. Query the ownership forms directly:

```python
form4s = company.get_filings(form="4")     # 3 = initial, 4 = changes, 5 = annual
latest = form4s.latest().obj()             # parse the XML into a structured object
print(latest.insider_name, latest.position)
df = latest.to_dataframe()
```

Access individual trades via DataFrames or the activities helper — not by iterating
`non_derivative_transactions` (which isn't exposed as a standard list):

```python
df_market  = latest.market_trades          # open-market buys / sells
df_options = latest.option_exercises
for act in latest.get_transaction_activities():
    print(act.transaction_type, act.code, act.shares, act.price_per_share)
    # transaction codes: P = purchase, S = sale, M = option exercise, F = tax withholding
```

## Executive compensation — DEF 14A (domestic filers)

US filers disclose executive compensation in the annual proxy (DEF 14A) and incorporate it
by reference into the 10-K rather than printing it there — so look in the proxy, not the
10-K. A proxy is a free-form filing: `filing.obj()` is a `ProxyStatement` with no item
codes, so you can't pull a section by code the way you can from a 10-K. Download it, read
the table of contents in its first ~100 lines to see its sections, then grep the body for
the part you want.

```python
proxy = company.get_filings(form="DEF 14A").latest()
text = proxy.markdown()      # save to the cache, then read its ToC + grep
```

The compensation disclosures (the Summary Compensation Table and the rest) are mandated by
Regulation S-K Item 402 — so a proxy's contents are predictable from that rule. Which tables
and narrative you pull, and what you make of them, is the caller's call. See
`guide_filings.md` for the item-addressable-vs-free-form distinction in general.

## Foreign private issuers

FPIs are exempt from several US ownership and governance rules, which changes *where* the
data is:

- **Section 16 exemption.** FPIs (and Canadian MJDS filers) don't file Forms 3/4/5, so
  insider-transaction data won't appear on EDGAR. Check the home-jurisdiction regulator
  (e.g. SEDAR+ for Canada) instead.
- **No DEF 14A.** FPIs don't file US proxies. Compensation is in **Form 20-F Item 6.B**
  and share ownership in **Item 6.E**. Many FPIs disclose pay only in aggregate unless
  their home-country rules require individual figures.

> **20-F Item 7.A boundary trap.** When slicing "Item 7.A Major Shareholders" by text,
> note the full Item 7 title is "Major Shareholders **and Related Party Transactions**."
> Using "Related Party Transactions" as the end boundary truncates early, because it also
> appears in the title — terminate the slice on "Item 8" instead.
