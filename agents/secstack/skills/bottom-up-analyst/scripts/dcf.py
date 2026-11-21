"""Enterprise DCF for explicit FCFF assumptions.

The model has three routes:

``forward``
    Grow a positive base FCFF at one or two explicit rates.
``forecast``
    Discount an explicit annual FCFF sequence. This route can represent an
    initial loss and is preferable when margins or cash flow inflect.
``reverse``
    Solve for the first-stage FCFF growth rate implied by the share price.

All cash flows are free cash flow to the firm (FCFF), so they are discounted at
WACC to obtain enterprise value. Net claims are then subtracted to obtain equity
value. Net claims equal debt and other senior claims less excess cash and other
non-operating assets; use a negative number when additions exceed claims.
Monetary inputs must use one common unit; shares must use the matching count
unit. Rates are percentages.
"""

import argparse
import sys
from collections.abc import Sequence

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _percent_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated percentages") from exc
    if not values:
        raise argparse.ArgumentTypeError("provide at least one percentage")
    return values


def _number_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated numbers") from exc
    if not values:
        raise argparse.ArgumentTypeError("provide at least one cash flow")
    return values


def _validate_common(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.wacc <= 0:
        parser.error("--wacc must be positive")
    if args.terminal_growth <= -100:
        parser.error("--terminal-growth must exceed -100%")
    if args.wacc <= args.terminal_growth:
        parser.error("--wacc must exceed --terminal-growth")
    if args.shares <= 0:
        parser.error("--shares must be positive")
    if args.price is not None and args.price <= 0:
        parser.error("--price must be positive")


def _validate_growth(parser: argparse.ArgumentParser, values: Sequence[float], flag: str) -> None:
    if any(value <= -100 for value in values):
        parser.error(f"{flag} values must exceed -100%")


def _terminal_value(fcff: float, terminal_growth: float, wacc: float) -> float:
    next_year_fcff = fcff * (1 + terminal_growth)
    return next_year_fcff / (wacc - terminal_growth)


def growth_dcf(
    fcff0: float,
    growth1: float,
    years1: int,
    terminal_growth: float,
    wacc: float,
    growth2: float | None = None,
    years2: int | None = None,
) -> tuple[float, float, float, float]:
    """Return enterprise value and PVs of stages 1, 2, and terminal value."""
    fcff = fcff0
    elapsed = 0
    pv_stage1 = 0.0
    for _ in range(years1):
        elapsed += 1
        fcff *= 1 + growth1
        pv_stage1 += fcff / (1 + wacc) ** elapsed

    pv_stage2 = 0.0
    if growth2 is not None and years2 is not None:
        for _ in range(years2):
            elapsed += 1
            fcff *= 1 + growth2
            pv_stage2 += fcff / (1 + wacc) ** elapsed

    pv_terminal = _terminal_value(fcff, terminal_growth, wacc) / (1 + wacc) ** elapsed
    return pv_stage1 + pv_stage2 + pv_terminal, pv_stage1, pv_stage2, pv_terminal


def forecast_dcf(
    forecast: Sequence[float], terminal_growth: float, wacc: float
) -> tuple[float, float, float]:
    """Return enterprise value, PV of forecast FCFF, and PV of terminal value."""
    pv_forecast = sum(fcff / (1 + wacc) ** year for year, fcff in enumerate(forecast, 1))
    pv_terminal = _terminal_value(forecast[-1], terminal_growth, wacc) / (
        (1 + wacc) ** len(forecast)
    )
    return pv_forecast + pv_terminal, pv_forecast, pv_terminal


def _equity_value(enterprise_value: float, net_claims: float, shares: float) -> tuple[float, float]:
    equity_value = enterprise_value - net_claims
    return equity_value, equity_value / shares


def _solve_implied_growth(
    price: float,
    fcff0: float,
    years1: int,
    terminal_growth: float,
    wacc: float,
    net_claims: float,
    shares: float,
    growth2: float | None,
    years2: int | None,
) -> tuple[float | None, str]:
    def difference(growth1: float) -> float:
        enterprise_value, _, _, _ = growth_dcf(
            fcff0,
            growth1,
            years1,
            terminal_growth,
            wacc,
            growth2,
            years2,
        )
        _, value_per_share = _equity_value(enterprise_value, net_claims, shares)
        return value_per_share - price

    low, high = -0.99, 5.0
    low_difference = difference(low)
    high_difference = difference(high)
    if low_difference > 0:
        return None, "below"
    if high_difference < 0:
        return None, "above"

    for _ in range(200):
        midpoint = (low + high) / 2
        midpoint_difference = difference(midpoint)
        if abs(midpoint_difference) < 1e-9:
            return midpoint, "ok"
        if midpoint_difference > 0:
            high = midpoint
        else:
            low = midpoint
    return (low + high) / 2, "ok"


def _add_common_arguments(parser: argparse.ArgumentParser, *, price_required: bool) -> None:
    parser.add_argument(
        "--terminal-growth",
        type=float,
        required=True,
        help="Perpetual FCFF growth after the explicit forecast, in percent.",
    )
    parser.add_argument(
        "--wacc",
        type=float,
        required=True,
        help="Weighted average cost of capital, in percent.",
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
    price_help = (
        "Current price per share; required to solve implied growth."
        if price_required
        else "Current price per share; optional comparison with modeled value."
    )
    parser.add_argument("--price", type=float, required=price_required, help=price_help)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    forward = subparsers.add_parser(
        "forward", help="Value one- or two-stage growth in positive FCFF."
    )
    forward.add_argument("--fcff0", type=float, required=True, help="Normalized base FCFF.")
    forward.add_argument(
        "--growth",
        type=_percent_list,
        required=True,
        help="Stage-1 FCFF growth percentages; comma-separate sensitivity cases.",
    )
    forward.add_argument("--years", type=int, required=True, help="Stage-1 years.")
    forward.add_argument(
        "--growth2",
        type=_percent_list,
        help="Optional stage-2 growth percentages; comma-separate sensitivity cases.",
    )
    forward.add_argument("--years2", type=int, help="Stage-2 years; required with --growth2.")
    _add_common_arguments(forward, price_required=False)

    forecast = subparsers.add_parser(
        "forecast", help="Value an explicit annual FCFF forecast, including initial losses."
    )
    forecast.add_argument(
        "--fcff",
        type=_number_list,
        required=True,
        help="FCFF for years 1..N, comma-separated. Use --fcff=-10,20 for a negative first year.",
    )
    _add_common_arguments(forecast, price_required=False)

    reverse = subparsers.add_parser(
        "reverse", help="Solve for the stage-1 FCFF growth implied by price."
    )
    reverse.add_argument(
        "--fcff0", type=float, required=True, help="Positive normalized base FCFF."
    )
    reverse.add_argument("--years", type=int, required=True, help="Stage-1 years.")
    reverse.add_argument(
        "--growth2",
        type=float,
        help="Optional fixed stage-2 growth percentage after the implied stage 1.",
    )
    reverse.add_argument("--years2", type=int, help="Stage-2 years; required with --growth2.")
    _add_common_arguments(reverse, price_required=True)
    return parser


def _print_header(args: argparse.Namespace, route: str, horizon: int) -> None:
    print(f"# Enterprise DCF — {route}\n")
    print(f"- Explicit horizon: {horizon} years")
    print(f"- Terminal growth: {args.terminal_growth:.2f}%")
    print(f"- WACC: {args.wacc:.2f}%")
    print(f"- Diluted shares: {args.shares:,.2f}")
    print(f"- Net claims: {args.net_claims:,.2f}")
    if args.price is not None:
        print(f"- Price: {args.price:,.2f}")
    print()


def _price_comparison(price: float | None, values: Sequence[float]) -> None:
    if price is None:
        return
    low, high = min(values), max(values)
    if high <= 0:
        print("\nPrice comparison is not meaningful because modeled equity value is non-positive.")
        return
    if low <= 0:
        high_discount = (1 - price / high) * 100
        print(
            "\nThe low modeled equity value is non-positive. "
            f"Price discount/(premium) to the high value: {high_discount:+.1f}%."
        )
        return
    low_discount = (1 - price / low) * 100
    if abs(high - low) < 1e-12:
        print(f"\nPrice discount/(premium) to modeled value: {low_discount:+.1f}%")
        return
    high_discount = (1 - price / high) * 100
    print(
        f"\nPrice discount/(premium) to modeled value: {low_discount:+.1f}% at the "
        f"low value and {high_discount:+.1f}% at the high value."
    )


def _run_forward(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.fcff0 <= 0:
        parser.error("--fcff0 must be positive; use the forecast route for initial losses")
    if args.years <= 0:
        parser.error("--years must be positive")
    if (args.growth2 is None) != (args.years2 is None):
        parser.error("--growth2 and --years2 must be supplied together")
    if args.years2 is not None and args.years2 <= 0:
        parser.error("--years2 must be positive")
    _validate_growth(parser, args.growth, "--growth")
    if args.growth2 is not None:
        _validate_growth(parser, args.growth2, "--growth2")

    horizon = args.years + (args.years2 or 0)
    _print_header(args, "forward growth sensitivity", horizon)
    terminal_growth = args.terminal_growth / 100
    wacc = args.wacc / 100
    values: list[float] = []
    terminal_shares: list[float] = []

    if args.growth2 is None:
        print(
            "| Stage-1 growth | Enterprise value | Equity value | Value/share | Terminal % of EV |"
        )
        print("| :-- | --: | --: | --: | --: |")
        for growth in args.growth:
            enterprise_value, _, _, pv_terminal = growth_dcf(
                args.fcff0, growth / 100, args.years, terminal_growth, wacc
            )
            equity_value, value_per_share = _equity_value(
                enterprise_value, args.net_claims, args.shares
            )
            values.append(value_per_share)
            terminal_share = pv_terminal / enterprise_value * 100
            terminal_shares.append(terminal_share)
            print(
                f"| {growth:.2f}% | {enterprise_value:,.2f} | {equity_value:,.2f} | "
                f"{value_per_share:,.2f} | {terminal_share:.1f}% |"
            )
    else:
        print("| Stage 1 \\ Stage 2 | " + " | ".join(f"{g:.2f}%" for g in args.growth2) + " |")
        print("| :-- | " + " | ".join("--:" for _ in args.growth2) + " |")
        for growth1 in args.growth:
            row = [f"{growth1:.2f}%"]
            for growth2 in args.growth2:
                enterprise_value, _, _, pv_terminal = growth_dcf(
                    args.fcff0,
                    growth1 / 100,
                    args.years,
                    terminal_growth,
                    wacc,
                    growth2 / 100,
                    args.years2,
                )
                _, value_per_share = _equity_value(enterprise_value, args.net_claims, args.shares)
                values.append(value_per_share)
                terminal_shares.append(pv_terminal / enterprise_value * 100)
                row.append(f"{value_per_share:,.2f}")
            print("| " + " | ".join(row) + " |")
        print("\nValues in the matrix are equity value per diluted share.")

    print(f"\nModeled value/share range: **{min(values):,.2f} to {max(values):,.2f}**")
    if len(terminal_shares) > 1:
        print(
            f"Terminal value share of enterprise value: {min(terminal_shares):.1f}% "
            f"to {max(terminal_shares):.1f}%"
        )
    _price_comparison(args.price, values)


def _run_forecast(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.fcff[-1] <= 0:
        parser.error("the final explicit FCFF must be positive for a Gordon terminal value")
    _print_header(args, "explicit forecast", len(args.fcff))
    terminal_growth = args.terminal_growth / 100
    wacc = args.wacc / 100
    enterprise_value, pv_forecast, pv_terminal = forecast_dcf(args.fcff, terminal_growth, wacc)
    equity_value, value_per_share = _equity_value(enterprise_value, args.net_claims, args.shares)

    print("| Year | FCFF | Present value |")
    print("| --: | --: | --: |")
    for year, fcff in enumerate(args.fcff, 1):
        print(f"| {year} | {fcff:,.2f} | {fcff / (1 + wacc) ** year:,.2f} |")
    print(f"\n- PV of explicit FCFF: {pv_forecast:,.2f}")
    terminal_share = f"{pv_terminal / enterprise_value:.1%}" if enterprise_value > 0 else "n/m"
    print(f"- PV of terminal value: {pv_terminal:,.2f} ({terminal_share} of EV)")
    print(f"- Enterprise value: {enterprise_value:,.2f}")
    print(f"- Equity value: {equity_value:,.2f}")
    print(f"- Value per diluted share: **{value_per_share:,.2f}**")
    _price_comparison(args.price, [value_per_share])


def _run_reverse(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.fcff0 <= 0:
        parser.error("--fcff0 must be positive for reverse growth DCF")
    if args.years <= 0:
        parser.error("--years must be positive")
    if (args.growth2 is None) != (args.years2 is None):
        parser.error("--growth2 and --years2 must be supplied together")
    if args.years2 is not None and args.years2 <= 0:
        parser.error("--years2 must be positive")
    if args.growth2 is not None:
        _validate_growth(parser, [args.growth2], "--growth2")

    horizon = args.years + (args.years2 or 0)
    _print_header(args, "reverse growth", horizon)
    implied_enterprise_value = args.price * args.shares + args.net_claims
    if implied_enterprise_value <= 0:
        print(
            "Price implies non-positive operating enterprise value after the stated "
            "net claims; no positive-FCFF growth rate can reconcile this model."
        )
        return
    growth, status = _solve_implied_growth(
        args.price,
        args.fcff0,
        args.years,
        args.terminal_growth / 100,
        args.wacc / 100,
        args.net_claims,
        args.shares,
        args.growth2 / 100 if args.growth2 is not None else None,
        args.years2,
    )
    if status == "below":
        print("The implied stage-1 growth is below -99% per year, outside the search range.")
    elif status == "above":
        print("The implied stage-1 growth exceeds 500% per year, outside the search range.")
    else:
        print(f"Implied stage-1 FCFF growth: **{growth * 100:.2f}% per year**")
        print(f"Stage-1 duration: {args.years} years")
        if args.growth2 is not None:
            print(f"Fixed stage 2: {args.growth2:.2f}% for {args.years2} years")
    print(
        "\nThe implied rate is conditional on the stated base FCFF, horizon, terminal growth, "
        "WACC, net claims, and share count."
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_common(parser, args)
    if args.command == "forward":
        _run_forward(parser, args)
    elif args.command == "forecast":
        _run_forecast(parser, args)
    else:
        _run_reverse(parser, args)


if __name__ == "__main__":
    main()
