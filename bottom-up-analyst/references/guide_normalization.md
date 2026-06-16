# Normalization — from GAAP to owner earnings

Phase 3 of the loop. The goal is the business's *real, repeatable* earning power — what an
owner would actually pocket — not the accounting surface. GAAP is a starting point, not the
answer: it mixes one-offs with the run-rate, expenses real investment as if it were waste
(and vice-versa), and hides economics in the footnotes. Your job is to un-distort it, and —
per the prime directive — to **name every adjustment** so a reader can undo it. An
unexplained "adjusted" number is exactly the kind of laundered guess this skill exists to
avoid.

Drive `sec-edgar-skill` to pull the statements (`sec-edgar-skill`'s `parse_financials.py` → CSV) and the
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

## When the thesis depends on a new revenue stream: model the unit economics

Normalization looks backward — it un-distorts what the business *has* earned. But many
theses (turnarounds, inflections, hypergrowth pivots, special situations) depend on a
revenue stream or business model that **doesn’t yet exist in the trailing financials.**
When the valuation’s base or bull case rests on a new stream, the memo must model its
unit economics explicitly — not just cite a management TAM estimate and plug a growth
rate into the DCF.

### What “model the unit economics” means

Build a **bottom-up revenue bridge** from the new stream’s inputs to its contribution
to FCF. The bridge should answer:

1. **What is the unit of sale?** A per-device chip fee, a per-store contribution, a
   per-seat SaaS subscription, a per-unit margin on hardware — name it.
2. **What does one unit cost to deliver?** COGS, fulfillment, support, platform costs.
   If the company hasn’t disclosed this, benchmark against the closest analog and mark
   it [A].
3. **How many units does the scenario assume?** Tie this to something observable —
   the number of customers in the pipeline, the addressable installed base, the
   contract backlog — not just a top-down TAM percentage.
4. **What is the resulting gross margin and contribution margin?** Show the math.
5. **How does this flow through to FCF?** After incremental SG&A, R&D, capex, and
   working capital required to support the new stream.

The bridge makes the assumption *auditable*. A reader who disagrees with your per-unit
fee or your customer count can re-run the math; a reader who sees only “$5–20M in
annual SaaS revenue per customer [A]” cannot. The bridge also forces *you* to confront
whether the numbers are internally consistent: if the per-device fee implies a price
point higher than the competitor’s whole product, the thesis has a problem you’d rather
find now.

### When to do this

Any time the valuation’s base or bull case assigns material value to a revenue stream
that is pre-revenue, in pilot, or represents a business model change from the trailing
financials. Examples:

- A regulatory catalyst opens a new market the company hasn’t yet entered (ISPR’s IKE
  age-gating chip in the flavored ENDS market)
- A partnership or JV creates a new product category (WRBY’s Google smart-glasses)
- A divestiture or restructuring changes the margin profile (CMTL’s Allerium post-S&S)
- A platform or marketplace layer is being built on top of an existing product

If the new stream is immaterial to the thesis (“a small adjacent opportunity”), a
sentence suffices. If it’s load-bearing, the bridge is mandatory.

## The honesty check

Every normalized figure is an [E]stimate built on an [A]ssumption. Mark them as such in the
memo, state the assumption inline, and make sure the thesis survives the *conservative* end
of each. If owner earnings only works on your aggressive maintenance-capex number, that's not
a thesis — that's a hope with a spreadsheet.
