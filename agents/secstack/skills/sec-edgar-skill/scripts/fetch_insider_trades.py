"""Fetch one company's Form 4 insider transactions.

The report distinguishes transaction dates from filing dates and includes only
successfully parsed filings. Valid no-data results are emitted; retrieval failure
or a period in which every filing failed to parse exits nonzero.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c

_CODE_LABELS = {
    "P": "Purchase",
    "S": "Sale",
    "M": "Option Exercise",
    "F": "Tax Withholding",
    "A": "Award/Grant",
    "G": "Gift",
    "D": "Disposition (non-sale)",
    "C": "Conversion",
    "J": "Other",
}


class FetchFailure(RuntimeError):
    """Raised when a Form 4 query cannot be completed."""


@dataclass
class FetchResult:
    """Transactions and completeness metadata for one Form 4 query."""

    transactions: list[dict]
    filings_found: int
    filings_parsed: int
    filings_failed: int


def _missing(value: object) -> bool:
    try:
        result = pd.isna(value)
        return bool(result) if not hasattr(result, "all") else bool(result.all())
    except (TypeError, ValueError):
        return value is None


def _number(value: object) -> float | None:
    if _missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _cell(value: object) -> str:
    if _missing(value):
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _date_text(value: object) -> str:
    if _missing(value):
        return "n/a"
    if hasattr(value, "date"):
        try:
            return value.date().isoformat()
        except (AttributeError, TypeError, ValueError):
            pass
    text = str(value)
    return text[:10] if len(text) >= 10 else text


def _code_label(code: str) -> str:
    return _CODE_LABELS.get(code, code or "Unknown")


def _fmt_shares(value: object) -> str:
    number = _number(value)
    if number is None:
        return "n/a"
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:,.2f}M"
    if abs(number) >= 1_000:
        return f"{number / 1_000:,.1f}K"
    return f"{number:,.0f}"


def _fmt_price(value: object) -> str:
    number = _number(value)
    if number in (None, 0):
        return "n/a"
    return f"${number:,.2f}"


def _fmt_value(shares: object, price: object) -> str:
    share_number = _number(shares)
    price_number = _number(price)
    if share_number is None or price_number in (None, 0):
        return "n/a"
    value = abs(share_number * price_number)
    if value >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.0f}"


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def fetch_insider_trades(
    ticker: str, start: date, end: date, buys_only: bool = False
) -> FetchResult:
    """Fetch and parse original Form 4 filings whose filing dates fall in the range."""
    company = c.resolve_company(ticker)
    date_range = f"{start.isoformat()}:{end.isoformat()}"
    c.log(f"Fetching Form 4 filings for {ticker} ({date_range})...")

    try:
        form4s = company.get_filings(form="4", date=date_range, amendments=False)
    except Exception as exc:
        raise FetchFailure(f"could not fetch Form 4 filings: {exc}") from exc

    total = len(form4s) if form4s is not None else 0
    if total == 0:
        c.log(f"No original Form 4 filings found for {ticker} in {date_range}.")
        return FetchResult([], 0, 0, 0)

    c.log(f"  Found {total} original Form 4 filings in range.")
    transactions = []
    parsed = 0
    errors = 0

    for filing in form4s:
        try:
            obj = filing.obj()
            transaction_frame = obj.to_dataframe()
        except Exception as exc:
            errors += 1
            c.log(f"  WARNING: could not parse {getattr(filing, 'accession_no', '')}: {exc}")
            continue

        parsed += 1
        if transaction_frame is None or len(transaction_frame) == 0:
            continue

        filed_date = _date_text(getattr(filing, "filing_date", ""))
        accession = str(
            getattr(filing, "accession_no", "") or getattr(filing, "accession_number", "")
        )
        default_name = getattr(obj, "insider_name", None) or "Unknown"
        default_position = getattr(obj, "position", None) or "Unknown"

        for _, row in transaction_frame.iterrows():
            code = _cell(row.get("Code", ""))
            if buys_only and code != "P":
                continue
            transactions.append(
                {
                    "transaction_date": _date_text(row.get("Date")),
                    "filed_date": filed_date,
                    "insider": _cell(row.get("Insider", default_name)) or _cell(default_name),
                    "role": _cell(row.get("Position", default_position)) or _cell(default_position),
                    "code": code,
                    "type": _code_label(code),
                    "shares": _number(row.get("Shares")),
                    "price": _number(row.get("Price")),
                    "remaining": _number(row.get("Remaining Shares")),
                    "accession": accession,
                }
            )

        if parsed % 25 == 0:
            c.log(f"  Parsed {parsed}/{total} filings...")

    transactions.sort(
        key=lambda item: (item["transaction_date"], item["filed_date"], item["accession"]),
        reverse=True,
    )
    c.log(f"  Parsed {parsed}/{total} filings and found {len(transactions)} transactions.")
    return FetchResult(transactions, total, parsed, errors)


def _build_markdown(
    ticker: str, result: FetchResult, start: date, end: date, buys_only: bool
) -> str:
    transactions = result.transactions
    lines = [
        f"# Insider Transactions: {ticker}",
        "",
        f"- **Form 4 filing period queried:** {start.isoformat()} to {end.isoformat()}",
        f"- **Filings found:** {result.filings_found}",
        f"- **Filings parsed:** {result.filings_parsed}",
        f"- **Filings failed:** {result.filings_failed}",
        f"- **Completeness:** {'Partial' if result.filings_failed else 'Complete'}",
        "",
    ]

    if not transactions:
        lines.append("No matching insider transactions were found in successfully parsed filings.")
        return "\n".join(lines)

    buys = [transaction for transaction in transactions if transaction["code"] == "P"]
    sells = [transaction for transaction in transactions if transaction["code"] == "S"]
    exercises = [transaction for transaction in transactions if transaction["code"] == "M"]

    buy_value = sum(
        abs(transaction["shares"] * transaction["price"])
        for transaction in buys
        if transaction["shares"] is not None and transaction["price"] is not None
    )
    sell_value = sum(
        abs(transaction["shares"] * transaction["price"])
        for transaction in sells
        if transaction["shares"] is not None and transaction["price"] is not None
    )

    lines.extend(
        [
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Open-market purchases | {len(buys)} |",
            f"| Unique buyers | {len({transaction['insider'] for transaction in buys})} |",
            f"| Total buy value | {_fmt_value(1, buy_value) if buy_value else 'n/a'} |",
        ]
    )
    if not buys_only:
        lines.extend(
            [
                f"| Open-market sales | {len(sells)} |",
                f"| Unique sellers | {len({transaction['insider'] for transaction in sells})} |",
                f"| Total sell value | {_fmt_value(1, sell_value) if sell_value else 'n/a'} |",
                f"| Option exercises | {len(exercises)} |",
            ]
        )
    lines.extend(
        [
            "",
            "## " + ("Open-Market Purchases" if buys_only else "Transactions"),
            "",
            "| Transaction Date | Filed | Insider | Role | Type | Shares | Price | Value | Remaining | Accession |",
            "|---|---|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for transaction in transactions:
        lines.append(
            f"| {transaction['transaction_date']} | {transaction['filed_date']} "
            f"| {transaction['insider']} | {transaction['role']} | {transaction['type']} "
            f"| {_fmt_shares(transaction['shares'])} | {_fmt_price(transaction['price'])} "
            f"| {_fmt_value(transaction['shares'], transaction['price'])} "
            f"| {_fmt_shares(transaction['remaining'])} | {transaction['accession']} |"
        )

    if buys:
        lines.extend(
            [
                "",
                "## Buyers",
                "",
                "| Insider | Role | Purchases | Total Shares | Total Value |",
                "|---|---|---:|---:|---:|",
            ]
        )
        buyer_data: dict[str, dict] = {}
        for transaction in buys:
            key = transaction["insider"]
            buyer = buyer_data.setdefault(
                key,
                {"role": transaction["role"], "count": 0, "shares": 0.0, "value": 0.0},
            )
            buyer["count"] += 1
            buyer["shares"] += abs(transaction["shares"] or 0)
            buyer["value"] += abs((transaction["shares"] or 0) * (transaction["price"] or 0))
        for name, buyer in sorted(
            buyer_data.items(), key=lambda item: item[1]["value"], reverse=True
        ):
            lines.append(
                f"| {name} | {buyer['role']} | {buyer['count']} "
                f"| {_fmt_shares(buyer['shares'])} | {_fmt_value(1, buyer['value'])} |"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ticker", required=True, help="Stock ticker to look up.")
    parser.add_argument(
        "--start", help="Form 4 filing-date start, YYYY-MM-DD (default: one year ago)."
    )
    parser.add_argument("--end", help="Form 4 filing-date end, YYYY-MM-DD (default: today).")
    parser.add_argument(
        "--buys-only", action="store_true", help="Keep only open-market purchases (code P)."
    )
    c.add_identity_arg(parser)
    c.add_cache_arg(parser)
    args = parser.parse_args()

    c.resolve_identity(args.identity)
    try:
        end = _parse_date(args.end) if args.end else date.today()
        start = _parse_date(args.start) if args.start else end - timedelta(days=365)
    except ValueError as exc:
        parser.error(f"dates must use YYYY-MM-DD: {exc}")
    if start > end:
        parser.error("--start cannot be later than --end")

    try:
        result = fetch_insider_trades(args.ticker, start=start, end=end, buys_only=args.buys_only)
    except FetchFailure as exc:
        c.log(f"ERROR: {exc}")
        sys.exit(1)
    if result.filings_found and result.filings_parsed == 0:
        c.log("ERROR: every Form 4 filing failed to parse; no report was written.")
        sys.exit(1)

    markdown = _build_markdown(args.ticker, result, start, end, args.buys_only)
    out_dir = c.company_dir(c.cache_root(args.cache_dir), None, ticker_hint=args.ticker)
    prefix = "insider-buys" if args.buys_only else "insider-trades"
    path = c.write_text(out_dir / f"{prefix}_{start.isoformat()}_{end.isoformat()}.md", markdown)
    c.emit(path)


if __name__ == "__main__":
    main()
