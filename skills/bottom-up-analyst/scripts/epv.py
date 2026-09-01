"""Earnings Power Value for normalized no-growth operating earnings.

EPV capitalizes normalized after-tax operating cash earnings at WACC. It is a
no-growth lens, not a guaranteed floor. Monetary inputs use one common unit;
shares use the matching count unit. Rates are percentages.

Without the optional maintenance-capex refinement, the model assumes D&A and
maintenance capex offset:

    operating earnings = normalized EBIT * (1 - cash tax rate)

With both ``--da`` and ``--maint-capex``:

    operating cash earnings = EBIT * (1 - tax) + D&A - maintenance capex

The latter preserves the depreciation tax shield and does not tax the capex
adjustment a second time.
"""

import argparse
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ebit", type=float, required=True, help="Normalized operating EBIT.")
    parser.add_argument(
        "--tax", type=float, required=True, help="Normalized cash tax rate, in percent."
    )
    parser.add_argument(
        "--wacc", type=float, required=True, help="Weighted average cost of capital, in percent."
    )
    parser.add_argument(
        "--shares",
        type=float,
        required=True,
        help="Diluted shares; use the count unit matching the monetary inputs.",
    )
    parser.add_argument(
        "--net-claims",
        type=float,
        required=True,
        help=(
            "Debt and other senior claims minus excess cash and non-operating assets; "
            "negative means net additions to enterprise value."
        ),
    )
    parser.add_argument(
        "--da",
        type=float,
        help="Normalized depreciation and amortization; use with --maint-capex.",
    )
    parser.add_argument(
        "--maint-capex",
        type=float,
        help="Estimated maintenance capex; use with --da.",
    )
    parser.add_argument(
        "--price", type=float, help="Current price per share, to compare price with EPV."
    )
    return parser


def _validate(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if not 0 <= args.tax < 100:
        parser.error("--tax must be at least 0% and below 100%")
    if args.wacc <= 0:
        parser.error("--wacc must be positive")
    if args.shares <= 0:
        parser.error("--shares must be positive")
    if args.price is not None and args.price <= 0:
        parser.error("--price must be positive")
    if (args.da is None) != (args.maint_capex is None):
        parser.error("--da and --maint-capex must be supplied together")
    if args.da is not None and (args.da < 0 or args.maint_capex < 0):
        parser.error("--da and --maint-capex cannot be negative")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate(parser, args)

    tax_rate = args.tax / 100
    wacc = args.wacc / 100
    after_tax_ebit = args.ebit * (1 - tax_rate)
    operating_earnings = after_tax_ebit
    if args.da is not None:
        operating_earnings += args.da - args.maint_capex
    if operating_earnings <= 0:
        parser.error(
            "normalized after-tax operating earnings must be positive; "
            "a perpetuity cannot capitalize a non-positive base"
        )

    enterprise_value = operating_earnings / wacc
    equity_value = enterprise_value - args.net_claims
    value_per_share = equity_value / args.shares

    print("# Earnings Power Value — no-growth operating case\n")
    print(f"- Normalized EBIT: {args.ebit:,.2f}")
    print(f"- After-tax EBIT at {args.tax:.2f}%: {after_tax_ebit:,.2f}")
    if args.da is not None:
        print(f"- Add D&A: {args.da:,.2f}")
        print(f"- Less maintenance capex: {args.maint_capex:,.2f}")
    print(f"- Capitalized operating earnings: {operating_earnings:,.2f}")
    print(f"- WACC: {args.wacc:.2f}%")
    print(f"- Enterprise value: {enterprise_value:,.2f}")
    print(f"- Net claims: {args.net_claims:,.2f}")
    print(f"- Equity value: {equity_value:,.2f}")
    print(f"- EPV per diluted share: **{value_per_share:,.2f}**")

    if args.price is not None:
        if value_per_share <= 0:
            print(
                "\nPrice comparison is not meaningful because modeled equity value is non-positive."
            )
        else:
            discount = (1 - args.price / value_per_share) * 100
            print(f"\nPrice discount/(premium) to EPV: {discount:+.1f}%")


if __name__ == "__main__":
    main()
