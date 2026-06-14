# Filing text — sections, items, and exhibits

Everything you can pull as *text* from a filing: a whole report, one section, or an
exhibit. Two facts shape how you do it efficiently:

- **Filings live on disk, not in context.** Convert to Markdown into the cache, then grep
  and read line ranges (`edgartools` strips SEC HTML to roughly a tenth of the size).
- **A form is addressed one of two ways.** Some forms expose their sections by the SEC
  *item codes* you already know; the rest you navigate by their own table of contents.
  Knowing which kind you're holding is the whole game.

`scripts/fetch_filing.py` wraps every path below; the library snippets show what it calls
under the hood, so you can drop to them inline when a flag doesn't cover your case. For
XBRL numbers (revenue, EPS, balances) use `guide_financials.md` — this guide is the
narrative and event text.

## 1. Item-addressable forms — pull a section by its code

Periodic and current reports parse into a typed object whose sections are keyed by SEC
item code. You don't discover the structure — you ask for the item directly.

```python
filing = company.get_filings(form="10-K").latest()
report = filing.obj()            # TenK / TenQ / CurrentReport / TwentyF / ...
report.items                     # -> ['Item 1', 'Item 1A', 'Item 1B', ...] actually present
risk = report["Item 1A"]         # just that item's text, not the whole 100k-word filing
```

- `report.items` is the filing's real table of contents in the SEC's own taxonomy — a
  neutral structural map. List it first to see what the filing actually contains.
- `report["<code>"]` returns only that section, so you spend tokens on one item. An item
  that isn't present returns `None`.
- Script: `fetch_filing.py --section "Item 1A"`, or `--section list` to print the codes the
  filing contains.

> `Filing.markdown()` takes **no** section argument — passing one is silently ignored and
> returns the whole filing. Sections come from the parsed object (`filing.obj()[code]`),
> which is what `--section` uses.

The codes are fixed by SEC rule, which is why you can address them from memory:

```
10-K   Item 1 Business · Item 1A Risk Factors · Item 7 MD&A · Item 7A Market Risk · Item 8 Financial Statements
10-Q   keyed by Part:  "Part I, Item 2" MD&A · "Part II, Item 1" Legal · "Part II, Item 1A" Risk Factors
8-K    Item 1.01 Material Agreement · Item 2.02 Results of Operations (earnings) · Item 5.02 Director/Officer change · Item 9.01 Exhibits
20-F   Item 3.D Risk Factors · Item 4 Business · Item 5 Operating & Financial Review (MD&A) · Item 6 Directors & Compensation
```

`report.items` always returns the complete, authoritative list for the filing in hand; the
lines above just show the code *format*, which differs by form:

- **10-Q codes are namespaced by Part — and a bare code resolves to the wrong one.** Pass
  the full `"Part I, Item 2"` for the MD&A: a bare `"Item 2"` silently returns *Part II's*
  Item 2 ("Unregistered Sales"), not what you meant. Run `--section list` to see the exact
  keys.
- **An 8-K's `report.items` tells you what it's *about*.** An 8-K reports only the events it
  fired (e.g. `['Item 2.02', 'Item 9.01']` is an earnings release with exhibits), so listing
  the items is the cheapest way to triage one before reading it.
- **20-F uses a different scheme** from the 10-K (risk factors are Item 3.D, MD&A is Item 5),
  because foreign private issuers report on a different schedule.
- **40-F** (Canadian MJDS) usually wraps the home-country annual report as exhibits rather
  than US items — fetch the full filing or its attachments (§3).

## 2. Free-form forms — read the structure, then grep

DEF 14A proxies, 6-K reports, prospectuses, and the like have no item taxonomy: their
`filing.obj()` exposes no `.items` and isn't subscriptable. Save the whole filing as
Markdown, then navigate by its own structure:

```python
text = filing.markdown()         # clean Markdown for the entire filing
```

- A proxy (and most long filings) carries a **table of contents** in its first ~100 lines,
  listing every section with its page number — that's the filing's own map. Read it to see
  what's inside, then grep the body for the section you want.
- These convert to heavily *tabular* Markdown with few `#` headers, so `list_headings.py`
  (which keys on `#`) helps less here than on a periodic report. On a full 10-K/10-Q/20-F —
  whose Markdown *is* `#`-structured — `list_headings.py` is the fast way to map it.

Where a free-form filing's substance lives is in the relevant domain guide — e.g. proxy /
compensation in `guide_ownership.md`.

## 3. Attachments and exhibits

Exhibits — press releases, agreements, the foreign annual report inside a 40-F — are
separate documents hanging off the filing:

```python
attachments = list(filing.attachments)         # cast to a list first (see below)
for i, att in enumerate(attachments[:10]):      # slice — a filing can have 90+ exhibits
    print(i, att.document, att.description)
text = attachments[1].markdown()                # convert one exhibit to Markdown
```

Script: `fetch_filing.py --attachment "ex-99.1"` (or `list` | `all` | an index), or
`fetch_filings.py --attachments` to capture exhibits across a whole year range.

> **Index attachments via a list.** `filing.attachments` looks items up by their 1-based
> SEC *sequence number*, which can skip values — so integer indexing on the raw collection
> can return the wrong item or none. Cast to `list(...)` first and use 0-based indices.

> **Foreign private issuers and Form 6-K.** A 6-K is how an FPI reports interim results and
> material events — its 8-K/10-Q equivalent — but it's free-form (no item codes), and its
> main body is often just a brief cover note. The actual results or press release is an
> attachment, usually **Exhibit 99.1**. If a 6-K body comes back empty, list the attachments
> and fetch the exhibit (`fetch_filing.py --attachment "ex-99.1"`).

## Then search locally

Once a filing (or section, or exhibit) is in the cache, search it with your native
grep/ripgrep and read the matching line ranges. Don't run text searches through the library
— that's slower and round-trips to remote endpoints. *What* you search for, and what you
make of it, is yours (or your framework's) to decide; this skill just makes the text fast to
reach.
