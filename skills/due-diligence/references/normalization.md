# Normalization

Bridge reported results to the repeatable cash economics the valuation uses. Show every
adjustment with its source period, rationale, tax effect, and size, so a reader can undo it.
Use several periods, because a single adjusted year is easy to cherry-pick. A cyclical needs a
whole cycle.

## Pick the basis first

```text
FCFF = EBIT × (1 − normalized cash tax rate) + D&A − capex − Δ operating working capital
```

FCFF comes before interest, is discounted at WACC, and is what the bundled scripts take. Cash
flow built from net income or CFO is after interest under US GAAP, which makes it an equity
cash flow (FCFE), discounted at cost of equity with no debt subtracted afterwards. IFRS can put
interest in other cash-flow sections, so reconcile. Mixing the two bases is the most common
silent error.

## Where adjustments go wrong

- **"One-time" items.** Restructuring, litigation, and acquisition costs that keep recurring
  are operating costs. Remove an item only if its mechanism has demonstrably ended.
- **Taxes.** Use the expected cash burden (jurisdiction mix, NOLs and their expiry, credits),
  not the statutory rate.
- **Stock compensation.** EBIT already expenses it, while CFO adds it back. Charge it exactly
  once: keep the expense in EBIT-based FCFF, *or* model the cash needed to offset dilution, but
  not both. Buybacks that only absorb grants are not returns of capital. Show the history of
  basic and diluted share counts.
- **Maintenance capex.** Triangulate from management's split (an issuer estimate), capex in
  low-growth years, replacement cost against D&A (old assets plus inflation push maintenance
  above D&A), and peers. Give a range when it is uncertain. Growth capex is not free; tie it to
  the revenue and returns it buys.
- **Working capital.** An increase uses cash. Before calling a release repeatable, rule out
  factoring, payables stretch, inventory aging, and channel loading. Deferred revenue is timing,
  not extra cash to add back, because CFO already counts it.
- **Leases.** Pick one convention and carry it through earnings, cash flow, debt, and peer
  multiples. Expensing rent *and* adding the lease liability to debt double-counts.
- **Acquisitions.** Separate organic growth from acquired growth. A roll-up's acquisition
  spend is part of its reinvestment.
- **Non-GAAP.** Reconcile management's metrics to GAAP and track changes in their definitions.

## New streams

When value depends on revenue not yet in the numbers, build it in the business's actual unit
(customer, seat, store, device, contract):

```text
units × adoption × price = revenue
revenue × contribution margin − incremental fixed cost − capex − working capital = incremental FCFF
```

Source each input separately, use ranges when inputs are sparse, and reconcile to consolidated
results so shared costs and cannibalization show up.
