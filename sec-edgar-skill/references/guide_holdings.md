# Holdings — institutions (13F) and 5%+ blockholders (13D/13G)

External ownership: large institutional managers (Form 13F) and 5%+ stakeholders
(Schedules 13D/13G). For company *insiders* — officers and directors — see
`guide_ownership.md` instead.

## Institutional holdings — two approaches

### Quick route: `fetch_13f_holders.py` (via 13f.info)

For the most common ownership questions — "who owns this stock?", "how has
institutional ownership changed?", "what does this fund hold?" — the bundled
`fetch_13f_holders.py` script queries [13f.info](https://13f.info), a free
structured interface to SEC 13F data. It is dramatically faster and more
token-efficient than parsing raw 13F XML from EDGAR, and answers the question
in one call:

```bash
# Who are the top institutional holders of CMTL right now?
python scripts/fetch_13f_holders.py --ticker CMTL --top 15

# How has institutional ownership changed over time?
python scripts/fetch_13f_holders.py --ticker CMTL --history

# What does Berkshire Hathaway hold?
python scripts/fetch_13f_holders.py --manager "Berkshire Hathaway"

# How has Royce's position in CMTL changed over time?
python scripts/fetch_13f_holders.py --cik 0000906304 --cusip 205826209

# Holders for a specific quarter
python scripts/fetch_13f_holders.py --ticker AAPL --year 2025 --quarter 4 --top 20
```

**Use this as the default for 13F questions.** It resolves ticker → CUSIP
automatically, handles manager search by name, and outputs compact Markdown.
No SEC identity or API key is needed — 13f.info is public.

### Deep route: `edgartools` (raw 13F from EDGAR)

When you need the raw filing itself (e.g. to verify a specific holding, check
voting/dispositive authority, or examine an amendment), use `edgartools` to
query the manager's CIK directly:

```python
manager = Company("Magnetar Capital LLC")
f13 = manager.get_filings(form="13F-HR").latest().obj()
df = f13.holdings                          # the holdings DataFrame
```

> Operating companies (AAPL, etc.) do **not** file 13F — querying their CIK for `13F-HR`
> returns an empty collection. You must query the fund manager's name or CIK.
>
> Holdings live on the `.holdings` attribute; the 13F object has no `.to_dataframe()`.

Filter the holdings DataFrame by CUSIP or issuer name to confirm whether a given manager
holds a target stock (you query each manager you care about).

## Blockholders (Schedules 13D / 13G)

13D signals an active/control intent; 13G signals a passive stake. Query both, and
include the `"SC "`-prefixed names — EDGAR often indexes these schedules that way, so
omitting them returns empty results:

```python
blocks = company.get_filings(
    form=["13D", "13G", "SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A"]
)
sched = blocks.latest().obj()        # Schedule13D / Schedule13G structured object
sched.reporting_persons              # who holds — each with voting / dispositive power
sched.issuer_info                    # the subject company (name, CIK, CUSIP)
sched.total_percent                  # aggregate % of class
sched.items.item4_purpose_of_transaction   # 13D Item 4 narrative, when present
```

These schedules parse into a **structured object**, not an item-addressable one — there is
no `sched["Item 4"]`. The per-item values live on `sched.items` (a dataclass with fields
like `item4_purpose_of_transaction` and `item5_percentage_of_class`).

> **Older filings lack structured tags.** Before EDGAR's late-2024 structured-XML mandate,
> `sched.has_structured_data` is `False` and the parsed fields come back `None`/`0`. For
> those, save the full Markdown (`fetch_filing.py`, no `--section`) and grep the ownership
> figure and the Item 4 purpose out of the text instead.
