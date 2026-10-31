# Valuation

Pick the methods the cash flows support. Running a method that does not fit adds no
triangulation. Every method has to land on the same security, date, currency, share count, and
capital structure.

## Enterprise to equity

```text
operating value + excess cash and non-operating assets
− debt − preferred − minorities − pension deficit − other senior claims
− options and similar claims not already in the share count
= common equity ÷ diluted shares (same date) = value per share
```

Show the whole bridge instead of folding it into "net debt", and date it to match the base
cash flow. The scripts take everything below operating value as one `--net-claims` figure
(negative when non-operating assets exceed the claims).

## Scripts

Run them with `python "<skill-dir>/scripts/…"`. Inputs are FCFF (see `normalization.md`) in one
monetary unit, shares in the matching count unit, and rates in percent. Pass `--price` to print
the discount or premium.

```bash
# constant-growth sensitivity; needs a positive base FCFF; add --growth2/--years2 for a second stage
dcf.py forward --fcff0 1200 --growth 8,12,16 --years 10 --terminal-growth 3 --wacc 10 \
  --shares 500 --net-claims 200 --price 75
# explicit annual FCFF; use this for losses or inflections; the final year must be positive
dcf.py forecast --fcff=-20,10,45,80,110 --terminal-growth 2.5 --wacc 12 --shares 30 \
  --net-claims 66 --price 8
# growth implied by the price
dcf.py reverse --price 75 --fcff0 1200 --years 10 --terminal-growth 3 --wacc 10 \
  --shares 500 --net-claims 200
# no-growth earnings power; --da and --maint-capex go together
epv.py --ebit 600 --tax 21 --wacc 9 --shares 500 --net-claims 200 [--da 100 --maint-capex 85]
```

Discounting FCFF at WACC and then subtracting debt is not double-counting. Double-counting
happens when one burden (leases, pensions, distress) sits in both the cash flow and the bridge.

## Traps

- **Growth sensitivity is not a set of scenarios.** Comma-separated growth rates vary one input.
  When margins, reinvestment, dilution, or financing also change, run each scenario as its own
  command, named for the mechanism that differs.
- **Reverse DCF** reads only when a positive base FCFF and constant growth describe the business.
  For an immature company, find which combinations of scale, margin, reinvestment, and dilution
  reconcile to the price instead.
- **Terminal value** assumes a mature state: growth funded by reinvestment (g = reinvestment
  rate × return on new capital), margins faded to defensible levels, WACC above g. Report the
  terminal value as a share of EV (the scripts print it) and its implied multiple (compute it), because that is where the model is
  least anchored.
- **EPV is not a floor.** It assumes steady-state working capital and overstates value when earnings are at a cyclical peak, assets are
  decaying, maintenance is understated, or liabilities sit outside the model. Use mid-cycle
  earnings for cyclicals.
- **Multiples** compare only when numerator, denominator, accounting, leases, and capital
  structure match: enterprise multiples over pre-interest measures, equity multiples over
  post-interest. A revenue multiple is a margin and reinvestment assumption in disguise; make
  the bridge explicit.
- **Discount rate.** Derive it from current inputs (the risk-free rate from `^TNX` via
  `market-data`, today's debt cost rather than the historical coupon) and sensitize it. Beta is
  noisy; a thin peer set argues for a wider range, not false precision. Distressed equity needs
  financing, dilution, and default modeled per scenario, not one blended WACC.
- **Asset plays and special situations** need their own arithmetic: sum of the parts with
  corporate costs allocated, realizable NAV after haircuts, taxes, and time, or a payoff tree
  with probabilities, timing, interim cash, and break value. Compare annualized returns, not raw
  spreads.

## Method by thesis shape

| Shape | Usually useful | Common misuse |
| :-- | :-- | :-- |
| Compounder | operating DCF, runway cases, reverse check | extrapolating today's ROIC forever |
| Cash-burning growth | explicit forecast, price-reconciliation scenarios | growing a negative FCFF base |
| Cyclical | mid-cycle EPV/DCF, trough balance sheet, asset values | spot multiple on peak earnings |
| Turnaround | explicit transition cases incl. failure, financing path | target margins applied immediately |
| Special situation | payoff tree, waterfall, SOTP, annualized return | a DCF obscuring the binding terms |
| Deep value | realizable NAV, burn and timing, EPV if durable | book value or EPV as a hard floor |

Finish with the range the evidence supports, the two or three assumptions that dominate it, and
the conditions under which the range stops being useful.
