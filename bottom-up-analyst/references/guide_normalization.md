# Normalization — from GAAP to owner earnings

Phase 3 of the loop. The goal is the business's *real, repeatable* earning power — what an
owner would actually pocket — not the accounting surface. GAAP is a starting point, not the
answer: it mixes one-offs with the run-rate, expenses real investment as if it were waste
(and vice-versa), and hides economics in the footnotes. Your job is to un-distort it, and —
per the prime directive — to **name every adjustment** so a reader can undo it. An
unexplained "adjusted" number is exactly the kind of laundered guess this skill exists to
avoid.

Drive `sec-edgar-skill` to pull the statements (`parse_financials.py` → CSV) and the
relevant footnotes (grep the cached 10-K); do the reasoning here.

## Owner earnings — the target number

Start from the Buffett definition and adjust toward cash an owner could remove without
harming the business:

```
Owner earnings = net income
              + depreciation & amortization
              + other non-cash charges
              − maintenance capex            (NOT total capex — see below)
              ± normalized working-capital change
              − real stock-based compensation cost
```

The art is in three places, and each is a judgment you must show your work on:

### 1. Maintenance vs. growth capex
Total capex on the cash-flow statement bundles "keep the lights on" with "build the future."
Only **maintenance** capex belongs in owner earnings; growth capex is optional spending you
can value separately. Estimate maintenance capex from D&A as a floor, from management's own
split if they disclose one [V], from unit economics (capex per store/rig/MW at steady
state), or from history (capex in no-growth years). State which method and why — a
compounder's value swings hard on this number.

### 2. Working capital — separate structural from one-off
A growing business consumes working capital; a shrinking or seasonal one releases it. Pull
the *normalized* draw, not a single year's swing, and watch for channel-stuffing or a
one-time release flattering operating cash flow.

### 3. Stock-based comp is a real expense
It is non-cash but not free — it transfers ownership. Subtract it, and fold the resulting
dilution into the share count (treasury-stock method) rather than admiring a "cash" number
that quietly grows the shares 4% a year. For hypergrowth names this is often *the* swing
factor between "profitable" and not.

## Common distortions to undo

- **Deferred / subscription revenue.** Cash collected up front can make GAAP *understate*
  real earnings (a healthy subscription book) or overstate durability — read the deferred
  revenue footnote and decide which.
- **Leases.** Post-ASC 842, operating leases are on the balance sheet; treat lease
  obligations as the debt-like commitments they are when you compute net debt and TEV.
- **One-offs and "non-recurring" items that recur.** Restructuring every year is an
  operating cost, not a special item. Back out the genuinely one-time; keep the rest.
- **Acquired growth vs. organic.** Strip the contribution of acquisitions to see the
  organic engine; a roll-up's "growth" can be capital consumption in disguise.
- **Non-operating noise.** Pension mark-to-market, FX, fair-value swings on securities —
  separate from operating earning power.

## Show the trend, not a snapshot

A single normalized year can be cherry-picked or flattered. Build the **year-by-year
capital-allocation table** — it is the most persuasive object in the memo because the trend
argues for itself:

```text
            Shares(M)   Net debt($M)   Reinvested($M)   ROIC(%)   FCF/share
FY-4          15.2         420            …               …          …
FY-3          13.6         360
FY-2          11.1         300
FY-1          10.4         210
FY0            9.2         120
```

Falling share count, falling debt, rising returns on retained capital — that picture tells
the reader how management actually behaves, which no single ratio can.

## The honesty check

Every normalized figure is an [E]stimate built on an [A]ssumption. Mark them as such in the
memo, state the assumption inline, and make sure the thesis survives the *conservative* end
of each. If owner earnings only works on your aggressive maintenance-capex number, that's not
a thesis — that's a hope with a spreadsheet.
