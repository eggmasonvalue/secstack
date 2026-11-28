# Normalization — reported results to economic cash flow

Use this guide when reported earnings do not represent the repeatable cash economics relevant
to the thesis. Normalization is a reconciliation, not permission to remove unpleasant costs.
Show each adjustment, source period, rationale, tax treatment, and effect so the reader can
reverse it.

## Choose the cash-flow basis first

Do not mix enterprise and equity cash flows.

### Free cash flow to the firm (FCFF)

Use FCFF for the bundled DCF and EPV scripts:

```text
FCFF = EBIT × (1 − normalized cash tax rate)
     + D&A and other justified non-cash add-backs
     − capital expenditure
     − increase in operating working capital
```

Do not use “non-cash” alone as justification to add back a recurring economic cost such as stock
compensation. FCFF is before interest and net borrowing. Discount it at WACC to value operations,
then bridge from enterprise value to common equity by adding non-operating assets and subtracting net debt,
preferred stock, minority interests, pension deficits, and other senior claims as appropriate.
Do not hide those items inside a label called net debt; show the bridge in the memo.

### Owner earnings or free cash flow to equity (FCFE)

A cash flow starting from net income or cash from operations is after interest under US GAAP and
is generally an equity cash flow. IFRS presentation can classify interest differently, so
reconcile it explicitly. Discount FCFE at the cost of equity and do not subtract debt again. The
bundled DCF does not model FCFE.

Whichever basis you use, reconcile it to the statements. Label units, currency, fiscal period,
and whether each figure is reported `[V]`, estimated `[E]`, or assumed `[A]`.

## Recurring versus non-recurring

Use a multi-period history and ask what a steady owner must expect to recur.

- Remove a gain or loss only when the underlying event is genuinely non-operating or unlikely
  to recur. Repeated restructuring, litigation, acquisition, or “one-time” costs belong in
  normalized economics unless the operating mechanism has demonstrably changed.
- Normalize taxes using the expected cash burden, including jurisdiction mix, credits, NOLs,
  and expiry. Do not adopt a headline statutory rate by default.
- Separate acquired growth from organic growth and include the acquisition spending required
  to sustain a roll-up's apparent growth.
- Distinguish temporary commodity, foreign-exchange, pension, fair-value, and working-capital
  effects from a changed run rate.

Present reported-to-normalized bridges for the periods that matter. A single adjusted year is
usually too easy to cherry-pick.

## Maintenance and growth investment

Total capex combines replacement, compliance, capacity, and expansion. Estimate maintenance
capex by triangulating evidence such as:

- management's disclosed split, treated as an issuer estimate rather than objective fact;
- physical units, replacement cycles, utilization, and current replacement cost;
- capex during periods with little capacity growth;
- depreciation by asset class, useful life, asset age, and inflation; and
- peer asset intensity and sustaining-capex disclosures.

D&A is a reference point, not a universal floor or ceiling. Old assets and inflation can make
replacement cost exceed depreciation; overbuilt capacity or accelerated depreciation can do the
opposite. If the split is uncertain, use a range and show how valuation changes.

A growth project is not economically free because it is excluded from “maintenance” capex.
Connect growth investment to incremental revenue, margins, and returns on incremental capital.

## Working capital and deferred revenue

Use operating working capital and preserve signs: an increase is a use of cash; a decrease is a
source. Normalize seasonal or event-driven swings with comparable dates and multiple periods.
Investigate receivable growth, inventory aging, payables extension, factoring, and channel
loading before treating a cash release as repeatable.

Deferred revenue is customer financing and a timing difference, not extra revenue to add back
mechanically. Its change already affects operating cash flow. Analyze billings, remaining
performance obligations, refund obligations, churn, and the future delivery cost; then model the
cash timing consistently without counting the same inflow twice.

## Stock-based compensation and dilution

Stock compensation is an economic cost, but common starting points treat it differently:

- GAAP EBIT and net income already expense it. Do not subtract the same expense again from an
  EBIT-based FCFF unless you first added it back.
- Cash from operations adds the non-cash expense back. A CFO-minus-capex measure therefore needs
  an explicit treatment: retain the GAAP expense in a reconstructed FCFF, subtract an estimate
  of ongoing grants, or model the cash needed to offset dilution.
- Reflect outstanding in-the-money instruments in diluted shares or value them separately.
  Model future grants consistently with operating margins. Do not charge the full compensation
  expense and an unrelated full dilution penalty without reconciling the overlap.

Show basic and diluted share-count history, grants, exercises, repurchases, and net issuance.
Repurchases that merely offset compensation are not a return of capital.

## Leases

Lease treatment must match the cash flow, capital structure, and comparison metric.

- If rent remains an operating expense and cash outflow, do not also add the full lease
  liability to debt without adjusting the earnings and cash-flow basis.
- If leases are capitalized as financing, add back the financing component consistently,
  capitalize the obligation, and use lease-adjusted peer metrics.

Either convention can be useful; mixing them double-counts the lease burden.

## A useful operating history

Choose rows and years for the business rather than forcing a fixed table. A typical operating
company history may include:

| Period | Revenue | Organic growth | EBIT margin | FCFF | Diluted shares | Net debt | ROIC |
| :-- | --: | --: | --: | --: | --: | --: | --: |
| [FY-2] | | | | | | | |
| [FY-1] | | | | | | | |
| [FY0] | | | | | | | |

For a cyclical, span a full cycle. For a turnaround, add quarterly bridge metrics. For a unit
model, show mature cohorts or stores. Explain denominator choices for ROIC and compute return on
incremental capital only across periods where the comparison is meaningful.

## New streams and changed economics

When a material scenario depends on a stream not represented in trailing results, bridge from
observable drivers rather than applying a TAM percentage:

```text
addressable units
× adoption or penetration
× price per unit
= revenue
× contribution margin
− incremental fixed cost
− capex and working-capital needs
= incremental FCFF
```

Use the actual economic unit: customer, seat, location, device, transaction, capacity unit, or
contract. Source price, volume, churn, utilization, cost to serve, and timing separately. Use
ranges when inputs are sparse. Reconcile the stream to consolidated revenue and costs so shared
expenses and cannibalization are not omitted.

## Final check

For each adjustment, ask:

1. Is it already reflected elsewhere in the cash flow, share count, or enterprise bridge?
2. Does it recur economically even if accounting labels it unusual?
3. Are tax and sign conventions correct?
4. Is the estimate supported by more than management's preferred presentation?
5. Does a conservative alternative materially change the decision?

An unexplained adjusted number is an assumption, not a fact.
