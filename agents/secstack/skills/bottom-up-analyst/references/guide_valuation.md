# Valuation — match the method to the economics

Valuation is a set of conditional claims, not a ritual. Choose methods that fit the business,
state what each method assumes, and reconcile them to the same security, date, currency, share
count, and capital structure. Multiple inapplicable methods do not create triangulation.

The bundled scripts cover enterprise DCF and EPV for non-financial operating companies. They do
not replace a segment model, asset appraisal, transaction waterfall, or probability tree.

## Build the enterprise-to-equity bridge

Before comparing per-share values, show the bridge:

```text
value of operating assets
+ excess cash and non-operating assets
− funded debt
− preferred and minority interests
− pension deficits and other senior claims
− value attributable to outstanding options or similar instruments, if not in shares
= value of common equity
÷ consistent diluted share count
= value per share
```

Avoid burying all adjustments in “net debt.” Match the bridge date to the base cash flow and
adjust for material subsequent transactions. Reconcile basic, reported diluted, and modeled
future shares.

## Enterprise DCF

### Cash-flow basis

The DCF script accepts free cash flow to the firm (FCFF): after-tax operating cash flow before
interest and net borrowing. Discount FCFF at WACC to obtain enterprise value, then subtract net
debt and other senior claims. Do not pass owner earnings or FCFE that already includes interest
and then subtract debt again.

Read `guide_normalization.md` for the reconciliation. A growing terminal state must include the
reinvestment needed to support that growth; terminal FCFF cannot assume growth while silently
removing its capital needs.

### Choose the route

Use the script path resolved from the installed skill.

**Forward growth sensitivity** works for a positive, normalized FCFF base when a constant rate
is a tolerable abstraction:

```bash
python "<skill-dir>/scripts/dcf.py" forward --fcff0 1200 --growth 8,12,16 \
  --years 10 --terminal-growth 3 --wacc 10 --shares 500 --net-claims 200 --price 75
```

Comma-separated growth values vary growth while holding every other input fixed. They are a
sensitivity, not complete bear/base/bull scenarios. Run separate commands when margins,
reinvestment, WACC, dilution, or the capital structure also differ.

**Explicit forecast** is preferable when FCFF begins negative or changes shape. Forecast each
year from revenue, margin, tax, reinvestment, and working-capital drivers:

```bash
python "<skill-dir>/scripts/dcf.py" forecast --fcff=-20,10,45,80,110 \
  --terminal-growth 2.5 --wacc 12 --shares 30 --net-claims 66 --price 8
```

The final explicit FCFF must be positive because it anchors a Gordon terminal value. Make the
transition to stable economics plausible rather than jumping from an immature margin directly
to perpetuity.

**Reverse growth DCF** asks which constant positive-FCFF growth rate equates the model to price:

```bash
python "<skill-dir>/scripts/dcf.py" reverse --price 75 --fcff0 1200 --years 10 \
  --terminal-growth 3 --wacc 10 --shares 500 --net-claims 200
```

The answer is conditional on every other input. It is informative only when positive base FCFF
and the model shape represent the business. It does not solve for revenue growth, margin, or
dilution, and it should not be presented as “the market's” unique forecast. For an immature
business, construct an operating model and test combinations of scale, margin, reinvestment,
and dilution that reconcile to price instead.

### Terminal value

A terminal state should be economically mature:

- terminal growth is consistent with the currency and long-run market opportunity;
- return on new capital and reinvestment support the growth rate;
- margins and competitive position have faded or stabilized plausibly;
- capital intensity, taxes, and dilution are normalized; and
- WACC exceeds terminal growth.

Report the terminal value as a percentage of enterprise value and cross-check its implied
terminal multiple. A high percentage is not automatically wrong, but it identifies where the
model is least anchored by near-term evidence.

## Earnings Power Value

EPV capitalizes normalized no-growth operating earnings at WACC. Without the optional
maintenance-capex refinement, it assumes D&A and maintenance capex offset:

```text
normalized after-tax EBIT = EBIT × (1 − normalized cash tax rate)
operating cash earnings    = after-tax EBIT + D&A − maintenance capex
EPV of operations          = operating cash earnings ÷ WACC
```

Use the D&A refinement only when both D&A and maintenance capex are estimated on a consistent
basis:

```bash
python "<skill-dir>/scripts/epv.py" --ebit 600 --tax 21 --wacc 9 \
  --shares 500 --net-claims 200 --da 100 --maint-capex 85 --price 10
```

EPV is a no-growth operating case, not a guaranteed floor. It can overstate value when earnings
are cyclical, assets are deteriorating, maintenance investment is understated, customers are
leaving, or liabilities sit outside the model. For cyclicals, use defensible mid-cycle earnings
and separately test trough liquidity.

## Relative and transaction evidence

Use multiples only when numerator, denominator, growth, accounting, leases, and capital
structure are comparable. Match enterprise multiples with pre-interest measures and equity
multiples with post-interest measures. Explain why a peer deserves the same or a different
multiple; an automated peer table is only a candidate list.

Useful anchors may include EV/EBIT, EV/FCFF, P/E, P/FCFE, unit value, replacement cost, and
precedent transactions. Sales multiples require an explicit margin and reinvestment bridge.
Historical multiples are evidence about prior expectations and rates, not intrinsic value.

Asset plays and special situations generally require their own arithmetic:

- sum-of-parts with segment-specific methods and corporate-cost allocation;
- liquidation or realizable NAV with asset haircuts, liabilities, tax, and timing;
- transaction outcomes with payoff, probability, timing, break value, and interim cash flows;
  and
- annualized expected return rather than an unadjusted spread.

Do not turn uncertain legal interpretation into a precise probability without qualified support.

## Discount rate

No fixed WACC or required-return table is timeless or company-specific. Derive a rate from
current inputs, document the date and sources, and sensitize it.

For an enterprise DCF:

```text
cost of equity = risk-free rate + beta × equity risk premium
WACC = E/(D+E) × cost of equity + D/(D+E) × pre-tax cost of debt × (1 − tax rate)
```

Add country or other risk components only when they are not already captured elsewhere. Use
market-value capital weights where observable. Estimate debt cost from current borrowing terms,
yield, or a defensible default spread rather than the historical coupon.

A bottom-up beta can be useful: choose operationally comparable firms, unlever their equity
betas using consistent market D/E and tax assumptions, take a robust central estimate, and
re-lever for a defensible current or target capital structure. But beta is a noisy model input,
not a fact. A thin or poor peer set may justify broader industry data, an alternative required
return, or wider sensitivity rather than false precision.

Using WACC for FCFF and then subtracting debt is not double-counting. WACC discounts operating
cash flow using financing costs; the debt subtraction allocates enterprise value to common
equity. Double-counting occurs when the same expected loss, lease burden, pension contribution,
or distress effect is embedded in both cash flow and an additional adjustment without
reconciliation.

If leverage or survival changes across scenarios, reflect financing costs, refinancing,
dilution, and default risk explicitly. A single normalized WACC can conceal the path dependency
of a distressed equity.

The memo should show enough of the derivation for a reader to replace the rate, but it need not
force a ceremonial subsection or peer-beta table when another method is better supported.

## Scenario design and margin of safety

Name scenarios for the mechanism that differs, not merely bear/base/bull. At minimum disclose:

- revenue or unit path;
- operating margin and reinvestment;
- taxes and working capital;
- financing, dilution, and enterprise bridge;
- discount and terminal assumptions; and
- evidence supporting the scenario weight, if probabilities are used.

Use sensitivity around the two or three variables that dominate value. Report value per share
and the price discount or premium to each relevant outcome. Margin of safety is a conclusion
about downside, uncertainty, and required return; no universal percentage substitutes for the
quality of the inputs.

## Method selection by thesis shape

| Thesis shape | Usually useful | Common misuse |
| :-- | :-- | :-- |
| Compounder | operating DCF, reinvestment/runway cases, reverse check | extrapolating current ROIC forever |
| Cash-burning growth | explicit operating forecast, price-reconciliation scenarios | growing a negative FCFF base |
| Cyclical | mid-cycle EPV/DCF, trough balance sheet, asset or unit values | valuing peak earnings at a spot multiple |
| Turnaround | explicit transition cases, failure case, financing path | applying target margins immediately |
| Special situation | payoff tree, waterfall, SOTP, annualized return | DCF obscuring the binding event terms |
| Deep value | realizable NAV/liquidation, burn and timing, EPV where durable | calling EPV or book value a hard floor |

End with the range supported by the evidence, the assumptions that dominate it, and the
conditions under which the range ceases to be useful.
