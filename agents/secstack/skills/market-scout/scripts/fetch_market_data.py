"""Fetch a Yahoo Finance snapshot, trailing returns, industry, and peers.

The report is printed to stdout because market data is compact and time-sensitive.
Run ``--help`` for the flag reference.
"""

from __future__ import annotations

import argparse
import sys

import _common as c

_RETURN_WINDOWS = [("1M", 30), ("3M", 91), ("6M", 182), ("1Y", 365), ("3Y", 1095), ("5Y", 1825)]


def _num(value, *, money: bool = False, pct: bool = False) -> str:
    if value is None:
        return "n/a"
    try:
        if pct:
            return f"{value:+.1f}%"
        if money:
            return f"{value:,.0f}"
        return f"{value:,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _first(mapping: dict, *keys: str):
    for key in keys:
        value = mapping.get(key)
        if value is not None:
            return value
    return None


def main() -> None:
    """Run the market-data CLI."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ticker", required=True, help="Stock ticker (Yahoo symbol).")
    parser.add_argument("--period", default="5y", help="History period for returns (default: 5y).")
    parser.add_argument("--industry", action="store_true", help="Also print the industry overview.")
    parser.add_argument(
        "--peers", action="store_true", help="Also print Yahoo's industry peer table."
    )
    args = parser.parse_args()

    try:
        import pandas as pd
        import yfinance as yf
    except Exception as exc:
        c.log(f"ERROR: yfinance/pandas not installed: {exc}")
        sys.exit(1)

    symbol = args.ticker.upper()
    ticker = yf.Ticker(symbol)

    try:
        info = ticker.info or {}
    except Exception as exc:
        c.log(f"WARNING: Yahoo snapshot unavailable: {exc}")
        info = {}

    close = None
    history_error = None
    try:
        history = ticker.history(period=args.period)
        if history is not None and "Close" in history:
            close = history["Close"].dropna()
    except Exception as exc:
        history_error = exc

    snapshot_fields = (
        "currentPrice",
        "regularMarketPrice",
        "marketCap",
        "sharesOutstanding",
        "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
    )
    has_snapshot = any(info.get(field) is not None for field in snapshot_fields)
    if not has_snapshot and (close is None or close.empty):
        detail = f": {history_error}" if history_error else ""
        c.log(f"ERROR: Yahoo returned no usable snapshot or price history for {symbol}{detail}")
        sys.exit(1)
    if history_error:
        c.log(f"WARNING: price history unavailable: {history_error}")

    price = _first(info, "currentPrice", "regularMarketPrice")
    if price is None and close is not None and not close.empty:
        price = close.iloc[-1]
    currency = _first(info, "currency", "financialCurrency")

    print(f"# Market data: {symbol}\n")
    print("## Snapshot")
    price_label = _num(price)
    if currency:
        price_label += f" {currency}"
    print(f"- Price: {price_label}")
    print(f"- Market cap: {_num(info.get('marketCap'), money=True)}")
    print(f"- Shares outstanding: {_num(info.get('sharesOutstanding'), money=True)}")
    print(
        f"- 52-week high / low: {_num(info.get('fiftyTwoWeekHigh'))} / "
        f"{_num(info.get('fiftyTwoWeekLow'))}"
    )
    if info.get("sector") or info.get("industry"):
        print(
            f"- Sector / industry: {info.get('sector') or 'n/a'} / {info.get('industry') or 'n/a'}"
        )

    if close is not None and len(close) > 1:
        last = close.iloc[-1]
        last_date = close.index[-1]
        rendered = []
        for label, days in _RETURN_WINDOWS:
            prior = close[close.index <= last_date - pd.Timedelta(days=days)]
            if len(prior):
                rendered.append(f"- {label}: {_num((last / prior.iloc[-1] - 1) * 100, pct=True)}")
        if rendered:
            print(f"\n## Trailing returns (through {last_date.date()})")
            print("\n".join(rendered))

    if args.industry or args.peers:
        industry_key = info.get("industryKey")
        if not industry_key:
            c.log("WARNING: Yahoo returned no industryKey; industry and peers are unavailable.")
            return
        try:
            industry = yf.Industry(industry_key)
            if args.industry:
                overview = industry.overview or {}
                print(f"\n## Industry: {getattr(industry, 'name', industry_key)}")
                if overview.get("market_cap") is not None:
                    print(f"- Total market cap: {_num(overview['market_cap'], money=True)}")
                if overview.get("companies_count") is not None:
                    print(f"- Companies: {overview['companies_count']}")
                if overview.get("description"):
                    print(f"- {overview['description']}")
            if args.peers:
                top = industry.top_companies
                if top is not None and len(top):
                    print("\n## Yahoo industry peers")
                    try:
                        print(top.to_markdown())
                    except Exception:
                        print(top.to_string())
                else:
                    c.log("WARNING: Yahoo returned no industry peers.")
        except Exception as exc:
            c.log(f"WARNING: industry/peers unavailable: {exc}")


if __name__ == "__main__":
    main()
