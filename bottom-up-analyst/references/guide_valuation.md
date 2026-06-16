# Valuation — triangulation, weighted by archetype

Phase 5 of the loop. Value is a *range*, reached from independent lenses, never a single
false-precision point. Each lens has failure modes; the archetype tells you which to trust.
The discipline is to make every assumption explicit and conservative enough that the thesis
survives the *low* end — an intrinsic value that only works on heroic inputs is a hope, not a
valuation.

Run the arithmetic with the bundled scripts (`scripts/dcf.py`, `scripts/epv.py`) rather than
re-deriving it each time; `--help` is the flag reference. Reason about the *inputs* here.

## The four lenses

### 1. Reverse-DCF — "what's already priced in" (first-class)
Instead of forecasting, **invert**: solve for the stage-1 growth (or margin) the *current
price* requires, then ask one question — *is that achievable?* This is the most honest lens
when the future is uncertain, and for **hypergrowth** names it is often the *only* defensible
one: rather than pretend you can forecast a hyper-growth decade, you judge whether the
market's embedded expectation is too high, about right, or too low. Run it on every name as a
reality check, even when another lens leads.

```bash
python scripts/dcf.py --mode reverse --price 150 --fcf0 1200 --years 10 \
  --terminal-growth 3 --discount 10 --shares 500 --net-debt 200
```
Read the result against reality: if the price implies 22% FCF growth for a decade and the
company has never exceeded 12%, the bar is too high regardless of how good the story sounds.

### 2. Forward DCF — intrinsic value under your assumptions
A two-stage discounted cash flow on normalized owner earnings (phase 3). Best for businesses
with *predictable* cash flows — compounders, stable cash generators. Drive it with
**bear/base/bull** growth cases (the script accepts comma-separated growth for a quick
sensitivity table) so the output is a range, not a point.

```bash
python scripts/dcf.py --fcf0 1200 --growth 8,12,16 --years 10 --terminal-growth 3 \
  --discount 10 --shares 500 --net-debt 200
```

When the FCF trajectory has a **structural bend** — the near-term growth rate differs
materially from the long-run rate — a single stage-1 rate is a forced average that
misrepresents both phases. Use the **three-stage model** by adding `--growth2` and
`--years2`. Stage 1 captures the distinct near-term phase, stage 2 captures the subsequent
normalized phase, then the terminal value. The output is a stage-1 × stage-2 sensitivity
matrix. Reach for it whenever the business has an identifiable reason for the growth rate
to change — not just turnarounds, but any shape where one rate doesn’t fit:

- **Turnaround / inflection:** cost-outs, margin expansion, or debt paydown free up FCF
  faster than revenue grows (stage 1), then revenue-driven growth takes over (stage 2).
- **Hypergrowth investing phase:** heavy S&M/R&D depresses FCF now; once the business
  scales past the investment hump, FCF inflects sharply (stage 1), then grows at a
  mature-compounder rate (stage 2).
- **Cyclical recovery:** earnings snap back from trough to mid-cycle (stage 1), then grow
  at trend (stage 2).
- **Regulatory / deployment wave:** a defined tailwind (NG9-1-1 rollout, 5G buildout)
  drives elevated growth for a bounded period (stage 1), then steady-state (stage 2).
- **Post-acquisition synergies:** integration savings land over 2–3 years (stage 1),
  then organic growth resumes (stage 2).

```bash
python scripts/dcf.py --fcf0 5 --growth 25,35,50 --years 3 \
  --growth2 5,8 --years2 7 --terminal-growth 2.5 --discount 12 \
  --shares 30 --net-debt 66 --price 2.75
```

### 3. EPV — the no-growth floor
Earnings Power Value capitalizes *current normalized* operating earnings with **no growth
credit** — a conservative floor that answers "what's it worth if the growth never shows up?"
Especially clarifying for cyclicals (use mid-cycle EBIT), deep-value, and any case where you
don't want to pay for a future you can't underwrite.

```bash
python scripts/epv.py --ebit 600 --tax 21 --wacc 9 --shares 500 --net-debt 200
```

### 4. Relative multiples — the sanity check
P/E, EV/EBIT, EV/Sales, P/FCF against the peer set (`market-scout` gives you the peers).
Never a thesis on its own — "cheap vs. peers" can mean the whole group is
mispriced or the company deserves its discount — but a vital cross-check on the absolute
lenses, and the right primary lens for some special situations and asset plays.

## Setting the inputs honestly

The output is only as good as three judgment calls — show your work on each:

- **Discount rate.** Tie it to the *risk of the cash flows*, not a textbook beta. A wide-moat
  compounder and a single-product turnaround do not deserve the same rate. State it and why.
- **Terminal value.** This is usually most of a DCF's value, so it's where false precision
  hides. Keep terminal growth at or below long-run GDP; sanity-check the implied terminal
  multiple — if it bakes in a permanent premium multiple, you've smuggled optimism into the
  tail.
- **The base cash flow.** Use *normalized* owner earnings (phase 3), not a peak or trough
  year. Garbage in, garbage out — most valuation errors are bad inputs, not bad arithmetic.

## Weighting by archetype

Lean on the lens the business actually fits; report the others as cross-checks.

| Archetype | Lead lens | Cross-check with |
| :-- | :-- | :-- |
| Compounder | Forward DCF (long stage-1 runway) | Reverse-DCF reality check; EPV floor |
| Hypergrowth | **Reverse-DCF** (what's priced in) | Multiples; scenario forward DCF |
| Cyclical | EPV on **mid-cycle** earnings | Normalized P/E; mid-cycle multiples |
| Turnaround / inflection | Scenario DCF (post-inflection margins) | EPV today as downside floor |
| Special situation | Event payoff / sum-of-parts | Multiples on the resulting pieces |
| Deep value | Asset value / liquidation; EPV floor | Multiples; reverse-DCF for the catalyst |

## The output

A defensible **intrinsic-value range** (low–high, anchored to bear–bull), the **margin of
safety** at today's price, and a plain statement of the *one or two assumptions the value is
most sensitive to* — because that's where the next reader (and reality) will push hardest.
Carry these straight into the verdict.
