# Proxy and governance disclosures

Use this guide for beneficial ownership, board structure, compensation, related parties,
auditors, equity plans, proposals, and voting. Domestic issuers generally disclose these in
DEF 14A; foreign private issuers generally use Form 20-F and home-jurisdiction materials.

## Navigate a domestic proxy

A DEF 14A is free-form rather than SEC-item-addressable. Fetch the full filing, inspect its
opening table of contents, then grep its Markdown for the filing's own headings:

```bash
python scripts/fetch_filing.py --ticker AAPL --form "DEF 14A"
```

Prefer an exact accession when orientation reports several proxy-related filings. Common
heading language varies, so search related terms rather than assuming one exact title.

## Beneficial ownership

Look for headings such as:

- Security Ownership of Certain Beneficial Owners and Management;
- Principal Shareholders;
- Beneficial Ownership;
- Stock Ownership of Directors and Executive Officers.

Capture the measurement date, share class, shares, percentage, footnotes, and whether the row
covers a person, reporting group, or aggregate management. Do not combine 13F holdings with
proxy ownership percentages without reconciling dates, classes, and reporting entities.

For external 5% schedules and institutional filings, use `guide_holdings.md`; the proxy table
is the issuer's annual consolidated disclosure and may have a different measurement date.

## Board and committees

Relevant sections commonly cover:

- director biographies, tenure, qualifications, and other directorships;
- independence determinations;
- audit, compensation, and nominating/governance committee membership;
- board leadership and lead-independent-director structure;
- meeting attendance;
- risk oversight;
- director compensation.

Extract what the filing states and preserve the relevant date. Avoid turning structural facts
into a governance score inside this data skill.

## Executive compensation

Regulation S-K Item 402 disclosures commonly include:

- Compensation Discussion and Analysis;
- Summary Compensation Table;
- Grants of Plan-Based Awards;
- Outstanding Equity Awards at Fiscal Year-End;
- Option Exercises and Stock Vested;
- Pension Benefits and Nonqualified Deferred Compensation;
- Potential Payments upon Termination or Change in Control;
- Pay Versus Performance;
- CEO pay ratio.

Capture table periods, units, footnotes, grant terms, and award status. “Total compensation” is
not interchangeable with realized pay or current equity value.

## Related parties, auditors, and equity plans

Search for:

- Certain Relationships and Related Transactions;
- Transactions with Related Persons;
- independent registered public accounting firm;
- audit and non-audit fees;
- auditor ratification;
- Equity Compensation Plan Information;
- request to approve or amend an equity incentive plan.

For equity plans, preserve authorized, outstanding, and remaining-share definitions rather
than collapsing them into one dilution number. Securities offerings, warrants, convertibles,
and ATM programs may instead require 10-Q/10-K footnotes, 8-K exhibits, S-3, or 424B filings.

## Proposals and voting

The proxy explains each management or shareholder proposal and the board's stated
recommendation. The eventual vote is generally reported in Form 8-K Item 5.07:

```bash
python scripts/fetch_filing.py --ticker AAPL --form 8-K --section "Item 5.07"
```

Keep proposals, recommendations, and final voting results distinct. Record votes for, against,
abstained, and broker non-votes as presented rather than reducing them to a pass/fail label.

## Foreign private issuers

Foreign private issuers generally do not file DEF 14A. Start with Form 20-F Item 6:

- Item 6.A — directors and senior management;
- Item 6.B — compensation;
- Item 6.C — board practices;
- Item 6.D — employees;
- Item 6.E — share ownership.

Home-country annual reports, meeting circulars, or regulator filings may contain greater
detail. Form 20-F Item 7.A covers major shareholders; when slicing by text, terminate at Item 8
rather than the words “Related Party Transactions,” which also occur in Item 7's full title.
