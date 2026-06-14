"""Two-stage DCF — forward (assumptions -> intrinsic value) and reverse (price -> implied growth).

Part of the bottom-up-analyst skill's valuation tooling. The judgment — which lens to weight,
how to set the inputs honestly — lives in ``references/guide_valuation.md``; this script just
does the arithmetic the same way every time so memos are comparable. Output is a compact
Markdown summary to stdout. Run ``--help`` for all flags.

Conventions: monetary inputs (``--fcf0``, ``--net-debt``) share one unit (e.g. $millions);
``--shares`` is in the matching count unit (e.g. millions) so per-share output is in dollars.
Rates (``--growth``, ``--terminal-growth``, ``--discount``) are percentages.

Model: free cash flow grows at the stage-1 rate for ``--years``, then a Gordon terminal value
captures perpetual growth at ``--terminal-growth``. Everything is discounted at ``--discount``.
Enterprise value -> less net debt -> equity value -> per share.
"""
import argparse
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def two_stage_value(fcf0, g1, years, g_term, disc):
    """Return (enterprise_value, pv_stage1, pv_terminal) for a two-stage DCF.

    Rates are decimals here (0.10 not 10). Raises ValueError if discount <= terminal growth,
    where the Gordon model is undefined/negative.
    """
    if disc <= g_term:
        raise ValueError(
            f"discount rate ({disc:.1%}) must exceed terminal growth ({g_term:.1%}); "
            "the Gordon terminal value is undefined otherwise."
        )
    pv_stage1 = 0.0
    fcf = fcf0
    for t in range(1, years + 1):
        fcf = fcf * (1 + g1)
        pv_stage1 += fcf / (1 + disc) ** t
    fcf_terminal = fcf * (1 + g_term)
    tv = fcf_terminal / (disc - g_term)
    pv_terminal = tv / (1 + disc) ** years
    return pv_stage1 + pv_terminal, pv_stage1, pv_terminal


def per_share(fcf0, g1, years, g_term, disc, net_debt, shares):
    ev, _, _ = two_stage_value(fcf0, g1, years, g_term, disc)
    equity = ev - net_debt
    return equity / shares, ev, equity


def solve_implied_growth(price, fcf0, years, g_term, disc, net_debt, shares):
    """Bisect for the stage-1 growth rate (decimal) that makes IV/share == price."""
    target = price
    lo, hi = -0.95, 5.0

    def f(g):
        v, _, _ = per_share(fcf0, g, years, g_term, disc, net_debt, shares)
        return v - target

    flo, fhi = f(lo), f(hi)
    if flo > 0:
        return None, "below"   # even deep decline overshoots price -> price is very low
    if fhi < 0:
        return None, "above"   # even 500% growth can't reach price -> price is very high
    for _ in range(200):
        mid = (lo + hi) / 2
        fm = f(mid)
        if abs(fm) < 1e-9:
            return mid, "ok"
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2, "ok"


def main():
    p = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--mode", choices=["forward", "reverse"], default="forward",
                   help="forward: assumptions -> IV/share. reverse: price -> implied growth.")
    p.add_argument("--fcf0", type=float, required=True,
                   help="Base (normalized) free cash flow, in $M. Use owner earnings.")
    p.add_argument("--growth", type=str, default="10",
                   help="Stage-1 growth %% (forward only). Comma-separated for a sensitivity "
                        "table, e.g. 8,12,16 for bear/base/bull.")
    p.add_argument("--years", type=int, default=10, help="Stage-1 length in years (default 10).")
    p.add_argument("--terminal-growth", type=float, default=2.5,
                   help="Perpetual growth %% after stage 1 (default 2.5; keep <= long-run GDP).")
    p.add_argument("--discount", type=float, default=10.0,
                   help="Discount rate / WACC %% (default 10).")
    p.add_argument("--shares", type=float, required=True,
                   help="Diluted shares outstanding, same unit as --fcf0 (e.g. millions).")
    p.add_argument("--net-debt", type=float, default=0.0,
                   help="Net debt in $M (total debt - cash & securities). Negative = net cash.")
    p.add_argument("--price", type=float, default=None,
                   help="Current price/share. Required for --mode reverse; optional in forward "
                        "to print upside/downside.")
    args = p.parse_args()

    g_term = args.terminal_growth / 100.0
    disc = args.discount / 100.0

    print(f"# DCF ({args.mode}) — two-stage\n")
    print(f"- Base FCF: {args.fcf0:,.0f}   Years (stage 1): {args.years}   "
          f"Terminal growth: {args.terminal_growth:.1f}%   Discount: {args.discount:.1f}%")
    print(f"- Shares: {args.shares:,.1f}   Net debt: {args.net_debt:,.0f}"
          + (f"   Price: {args.price:,.2f}" if args.price is not None else ""))
    print()

    if args.mode == "reverse":
        if args.price is None:
            p.error("--price is required for --mode reverse")
        g, status = solve_implied_growth(args.price, args.fcf0, args.years, g_term, disc,
                                         args.net_debt, args.shares)
        if status == "above":
            print("**The current price implies growth above 500%/yr for the whole stage** — "
                  "i.e. the price cannot be justified by this model on these cash flows. The "
                  "market is pricing something structurally different (an asset, an option, a "
                  "much larger base). Re-examine the base FCF or the archetype.")
        elif status == "below":
            print("**The current price implies a steep perpetual *decline*** — the market is "
                  "pricing the cash flows away. If you believe the business is stable or "
                  "growing, that gap is the opportunity (or a warning you're missing a risk).")
        else:
            print(f"## Implied stage-1 growth: **{g*100:.1f}% / yr** for {args.years} years\n")
            print("That is the growth the current price already bakes in. The thesis question: "
                  "is that bar too high, about right, or too low versus what this business has "
                  "done and can do? Compare it to history and to peers before you trust the story.")
        return

    # forward
    growths = [float(x) for x in args.growth.split(",") if x.strip() != ""]
    print("## Intrinsic value per share")
    print()
    header = "| Stage-1 growth | IV / share | Enterprise value | Equity value |"
    if args.price is not None:
        header += " Upside vs price |"
    print(header)
    sep = "| :-- | --: | --: | --: |" + (" --: |" if args.price is not None else "")
    print(sep)
    ivs = []
    for g in growths:
        try:
            iv, ev, eq = per_share(args.fcf0, g / 100.0, args.years, g_term, disc,
                                   args.net_debt, args.shares)
        except ValueError as exc:
            p.error(str(exc))
        ivs.append(iv)
        row = f"| {g:.1f}% | {iv:,.2f} | {ev:,.0f} | {eq:,.0f} |"
        if args.price is not None:
            row += f" {(iv/args.price - 1)*100:+.1f}% |"
        print(row)
    print()
    if len(ivs) > 1:
        print(f"**Intrinsic-value range: {min(ivs):,.2f} – {max(ivs):,.2f} / share** "
              "(bear–bull across the growth cases above).")
    if args.price is not None:
        lo, hi = min(ivs), max(ivs)
        mos = (1 - args.price / hi) * 100 if hi > 0 else float("nan")
        print(f"\nAt {args.price:,.2f}: margin of safety to the high case is {mos:.0f}%. "
              "Require the thesis to survive the *low* end before you trust it.")


if __name__ == "__main__":
    main()
