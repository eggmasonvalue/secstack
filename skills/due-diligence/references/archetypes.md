# Archetypes

Read only the section or two that fit. Each one names the edge, the traps that should cut or
kill the case, the valuation route, and the *tell*: the indicator that shows the thesis
breaking before the headline numbers do.

## Compounder

**Edge:** duration and reinvestment, not a "quality" label. Sustainable growth ≈ reinvestment
rate × return on *incremental* capital, after dilution and acquisitions.
**Traps:** ROIC is an accounting artifact or omits required assets; incremental returns are
sliding toward the cost of capital; growth relies on M&A or spending the model excludes; the
runway is used up or copyable; the moat is really concentration, regulation, or a temporary
shortage; buybacks above value or merely offsetting dilution; enterprise growth that never
reaches per-share value.
**Value:** a forecast tied to reinvestment capacity and returns; a reverse check of the duration
the price implies. A terminal premium needs normalized reinvestment, not adjectives.
**Tell:** the operating metric where runway or return decay appears first.

## Hypergrowth (cash-burning, observable unit economics)

**Edge:** profit understates mature economics. Separate earned growth from purchased growth,
mature cohorts from the blended average, gross retention from expansion, and reachable demand
from TAM.
**Traps:** mature cohorts are still uneconomic; growth requires rising incentives or falling
prices; metric definitions drift; no plausible scale-and-margin path reconciles to the price;
funding runs out before break-even, or dilution swamps the outcome; costs are modeled to vanish
rather than scale.
**Value:** `dcf.py forecast` built from explicit revenue, margin, reinvestment, and dilution,
including financing until the company is cash-positive. Do not grow a negative base.
**Tell:** the metric that separates investment from bad unit economics, and the date by which it
should show.

## Cyclical

**Edge:** pricing on normalized rather than spot earnings, with a balance sheet that survives the
trough. Identify the real cycle driver and separate it from secular change.
**Traps:** "mid-cycle" anchored to a favorable stretch; liquidity or covenants fail in the
downside path; a high position on the cost curve; new capacity or substitution keeps the old
cycle from returning; management adds capacity at peaks and issues equity at troughs; the thesis
needs timing precision the evidence lacks.
**Value:** trough, normal, and strong cases with FCFF, liquidity, and dilution for each;
mid-cycle EPV or DCF; asset and replacement values. A spot multiple on peak earnings is not
evidence.
**Tell:** the supply, inventory, or utilization indicator that would prove mid-cycle too high.

## Turnaround or inflection

**Edge:** one identified change → the operating line it hits → size and timing → cash cost →
evidence so far → FCFF if it works. Separate self-help from external recovery.
**Traps:** no mechanism, only cheapness or targets; progress visible only in adjusted figures;
the runway ends before evidence arrives; savings offset by lost revenue or stranded costs; an
ordinary cyclical rebound passed off as an inflection; management has missed similar plans
before; a price that already assumes success.
**Value:** failure, partial, and success cases through `dcf.py forecast`, with implementation
cost, timing, and financing. Never award the target margin on day one.
**Tell:** dated milestones and the cash runway that separate "delayed" from "broken".

## Special situation

**Edge:** reading the operative document precisely and getting the capital structure complete.
Read the agreement, indenture, plan, or order itself, not a summary of it. A document verifies
its text, not your legal reading of it; mark the interpretation `[A]`.
**Traps:** a condition, definition, consent, financing out, or senior claim defeats the apparent
term; minority protections are weak; an open-ended timeline lets carry costs eat the return;
break value is pegged to the unaffected price without re-underwriting the business;
probabilities have no base rate; taxes, fees, proration, or liquidity change the payoff to the
exact security.
**Value:** a payoff for each outcome to the exact class, with interim cash, probability basis,
timing, and annualized return; rebuild the post-event balance sheet.
**Tell:** the next document or decision date that resolves the binding term.

## Deep value or asset play

**Edge:** conservatively realizable value per diluted share, plus someone able and willing to
realize it.
**Traps:** restricted cash, liens, senior claims, or contingencies consume the cushion; burn
erodes it before realization; assets won't realize at the assumed value; a controller can
delay or divert value; pay, related-party leakage, or dilution eats the discount; taxes and
transaction costs erase it; there is no decision-maker and no path.
**Value:** a realizable-value bridge (adjusted cash, recoverable working capital, appraised
assets, minus every claim, burn through realization, and tax and transaction costs), with
ranges for recovery and timing. Model the outcomes; do not multiply the discount by a
probability.
**Tell:** the rate at which the asset cushion is melting, and who controls realization.
