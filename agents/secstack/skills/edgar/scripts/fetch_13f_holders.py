"""Fetch distilled SEC Form 13F data for a stock, manager, or manager-stock pair.

The normal interface accepts tickers and manager names (or exact manager CIKs),
resolving lower-level CUSIPs internally. Reports expose the underlying SEC period,
CIK, and accession rather than the retrieval provider. No SEC identity is required.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import _common as c
import pandas as pd

_BASE = "https://13f.info"
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class FetchFailure(RuntimeError):
    """Raised when the distilled 13F backend cannot complete a request."""


@dataclass
class ManagerFiling:
    """One filing row and its linked distilled portfolio page."""

    url: str
    period: str
    holdings: str
    form_type: str
    filed: str
    filing_id: str


def _get_json(url: str) -> dict | list:
    request = Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise FetchFailure(f"13F data request failed: {exc}") from exc


def _get_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": _UA, "Accept": "text/html"})
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise FetchFailure(f"13F page request failed: {exc}") from exc


def _autocomplete(query: str) -> dict:
    data = _get_json(f"{_BASE}/data/autocomplete?q={quote(query)}")
    return data if isinstance(data, dict) else {}


def _holders_for_quarter(cusip: str, year: int, quarter: int) -> dict:
    data = _get_json(f"{_BASE}/data/cusip/{cusip}/{year}/{quarter}")
    return data if isinstance(data, dict) else {}


def _manager_cusip_history(cik: str, cusip: str) -> dict:
    data = _get_json(f"{_BASE}/data/manager/{cik}/cusip/{cusip}")
    return data if isinstance(data, dict) else {}


def _resolve_cusip(ticker: str) -> tuple[str, str, str] | None:
    data = _autocomplete(ticker)
    for entry in data.get("cusips", []):
        name = entry.get("name", "")
        extra = entry.get("extra", "")
        parts = name.split(" - ", 1)
        symbol = parts[0].strip() if parts else ""
        issuer = parts[1].strip() if len(parts) > 1 else name
        cusip = extra.split(" - ")[0].strip() if " - " in extra else extra.strip()
        if cusip and symbol.upper() == ticker.upper():
            return cusip, symbol, issuer
    return None


def _manager_name_from_html(html: str, fallback: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if not match:
        return fallback
    return re.sub(r"<[^>]+>", "", unescape(match.group(1))).strip() or fallback


def _resolve_manager(query: str) -> tuple[str, str, str, str] | None:
    digits = "".join(character for character in query if character.isdigit())
    if len(digits) == 10 and query.strip().replace("-", "").isdigit():
        url = f"/manager/{digits}"
        html = _get_html(f"{_BASE}{url}")
        return digits, _manager_name_from_html(html, digits), url, html

    data = _autocomplete(query)
    managers = data.get("managers", [])
    if not managers:
        return None

    normalized = query.casefold().strip()
    exact = [
        entry for entry in managers if str(entry.get("name", "")).casefold().strip() == normalized
    ]
    candidates = [
        entry for entry in managers if normalized in str(entry.get("name", "")).casefold()
    ] or managers
    if len(exact) == 1:
        entry = exact[0]
    elif len(candidates) == 1:
        entry = candidates[0]
    else:
        choices = []
        for candidate in candidates[:5]:
            candidate_url = str(candidate.get("url", ""))
            candidate_cik = candidate_url.split("/")[-1].split("-")[0]
            choices.append(f"{candidate.get('name', '')} ({candidate_cik})")
        raise FetchFailure(
            f"manager name '{query}' is ambiguous; rerun --manager with one of these CIKs: "
            + "; ".join(choices)
        )
    name = str(entry.get("name", "")).strip()
    url = str(entry.get("url", "")).strip()
    cik = url.split("/")[-1].split("-")[0] if url else ""
    if not cik or not url:
        return None
    html = _get_html(f"{_BASE}{url}")
    return cik, name or _manager_name_from_html(html, query), url, html


def _fmt_shares(value: object) -> str:
    try:
        if pd.isna(value):
            return "n/a"
        number = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return str(value)
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:,.2f}M"
    if abs(number) >= 1_000:
        return f"{number / 1_000:,.1f}K"
    return f"{number:,.0f}"


def _fmt_percent(value: object) -> str:
    try:
        if pd.isna(value):
            return "n/a"
        return f"{float(value):,.1f}%"
    except (TypeError, ValueError):
        return "n/a"


def _cell(value: object) -> str:
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _accession_digits(value: object) -> str:
    match = re.search(r"(?:/13f/)?(\d{18})", str(value or ""))
    return match.group(1) if match else ""


def _format_accession(value: object) -> str:
    digits = _accession_digits(value)
    if len(digits) == 18:
        return f"{digits[:10]}-{digits[10:12]}-{digits[12:]}"
    return str(value or "")


def _iso_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%m/%d/%Y").date().isoformat()
    except ValueError:
        return value


def _quarter_end(year: int, quarter: int) -> str:
    return {
        1: f"{year}-03-31",
        2: f"{year}-06-30",
        3: f"{year}-09-30",
        4: f"{year}-12-31",
    }[quarter]


def _latest_quarter() -> tuple[int, int]:
    today = date.today()
    quarters = []
    for year in (today.year, today.year - 1):
        quarters.extend(
            [
                (date(year, 3, 31), year, 1),
                (date(year, 6, 30), year, 2),
                (date(year, 9, 30), year, 3),
                (date(year, 12, 31), year, 4),
            ]
        )
    for end_date, year, quarter in sorted(quarters, reverse=True):
        if today - end_date >= timedelta(days=50):
            return year, quarter
    return today.year - 1, 4


def _build_stock_holders(
    ticker: str, cusip: str, issuer: str, year: int, quarter: int, top_n: int
) -> str | None:
    data = _holders_for_quarter(cusip, year, quarter)
    holders = data.get("data", [])
    if not holders:
        return None

    period_end = _quarter_end(year, quarter)
    if isinstance(holders[0][1], list) and holders[0][1]:
        period_end = holders[0][1][0]
    ranked = sorted(holders, key=lambda holder: holder[3] or 0, reverse=True)
    lines = [
        f"# 13F Institutional Holders: {ticker} ({issuer})",
        "",
        f"- **CUSIP:** {cusip}",
        f"- **Reporting period:** Q{quarter} {year}",
        f"- **Holdings as of:** {period_end}",
        f"- **Reporting managers found:** {len(holders)}",
        "- **Underlying records:** SEC Form 13F filings",
        "",
        f"## Top {min(top_n, len(holders))} Reporting Managers by Shares",
        "",
        "| # | Manager | Shares | CIK | SEC Accession |",
        "|---:|---|---:|---|---|",
    ]
    for index, holder in enumerate(ranked[:top_n], 1):
        manager_info = holder[0]
        filing_info = holder[1]
        name = manager_info[0] if isinstance(manager_info, list) else str(manager_info)
        cik = manager_info[1] if isinstance(manager_info, list) and len(manager_info) > 1 else ""
        filing_slug = (
            filing_info[1] if isinstance(filing_info, list) and len(filing_info) > 1 else ""
        )
        lines.append(
            f"| {index} | {_cell(name)} | {_fmt_shares(holder[3])} | {cik} "
            f"| {_format_accession(filing_slug)} |"
        )
    if len(holders) > top_n:
        lines.extend(["", f"*Showing {top_n} of {len(holders)} reporting managers.*"])
    return "\n".join(lines)


def _build_stock_history(ticker: str, cusip: str, issuer: str) -> str | None:
    html = _get_html(f"{_BASE}/cusip/{cusip}")
    pattern = re.compile(
        r"<tr[^>]*>\s*"
        r"<td[^>]*>\s*<a[^>]*>(\d{4}\s+Q\d)</a>\s*</td>\s*"
        r"<td[^>]*>\s*([\d,]+)\s*</td>\s*"
        r"<td[^>]*>\s*([^<]+?)\s*</td>",
        re.DOTALL,
    )
    rows = [tuple(value.strip() for value in match.groups()) for match in pattern.finditer(html)]
    if not rows:
        return None
    lines = [
        f"# 13F Holder History: {ticker} ({issuer})",
        "",
        f"- **CUSIP:** {cusip}",
        "- **Underlying records:** SEC Form 13F filings",
        "",
        "| Period | Reporting Managers | Shares (excluding options) |",
        "|---|---:|---:|",
    ]
    lines.extend(f"| {period} | {filings} | {shares} |" for period, filings, shares in rows)
    return "\n".join(lines)


def _parse_manager_filings(html: str) -> list[ManagerFiling]:
    pattern = re.compile(
        r'<a[^>]*href="(/13f/[^"]+)"[^>]*>\s*(Q\d\s+\d{4})\s*</a>'
        r".*?<td[^>]*>\s*(\d+)\s*</td>"
        r".*?<td[^>]*>\s*([\d,]+)\s*</td>"
        r'.*?<td[^>]*title="([^"]*)"[^>]*>.*?</td>'
        r'.*?<td[^>]*title="([^"]*)"[^>]*>.*?</td>'
        r".*?<td[^>]*>\s*([\d/]+)\s*</td>",
        re.DOTALL,
    )
    filings = []
    for match in pattern.finditer(html):
        url, period, holdings, _value, _top, form_type, filed = match.groups()
        filings.append(
            ManagerFiling(
                url=url,
                period=period,
                holdings=holdings,
                form_type=form_type,
                filed=filed,
                filing_id=url,
            )
        )
    return filings


def _select_manager_filing(
    filings: list[ManagerFiling], year: int | None, quarter: int | None
) -> ManagerFiling | None:
    eligible = [
        filing for filing in filings if filing.form_type.upper() in {"13F-HR", "RESTATEMENT"}
    ]
    if year is not None and quarter is not None:
        target = f"Q{quarter} {year}"
        eligible = [filing for filing in eligible if filing.period == target]
    return eligible[0] if eligible else None


def _build_manager_holdings(cik: str, manager_name: str, filing: ManagerFiling) -> str | None:
    filing_digits = _accession_digits(filing.url)
    if not filing_digits:
        return None
    data = _get_json(f"{_BASE}/data/13f/{filing_digits}")
    rows = data.get("data", []) if isinstance(data, dict) else []
    if not rows:
        return None

    lines = [
        f"# 13F Portfolio: {manager_name}",
        "",
        f"- **Manager CIK:** {cik}",
        f"- **Reporting period:** {filing.period}",
        f"- **Filed:** {_iso_date(filing.filed)}",
        f"- **SEC accession:** {_format_accession(filing.filing_id)}",
        "- **Underlying record:** SEC Form 13F",
        "",
        f"## Disclosed Holdings ({len(rows)})",
        "",
        "| Symbol | Issuer | Class | CUSIP | Shares/Principal | Option Type |",
        "|---|---|---|---|---:|---|",
    ]
    # Row shape: symbol, issuer, class, CUSIP, value, portfolio %, shares,
    # principal, option type. Dollar value and portfolio percentage are omitted.
    for row in sorted(rows, key=lambda item: str(item[0] or "")):
        symbol, issuer, security_class, cusip = row[:4]
        shares = row[6] if len(row) > 6 else None
        principal = row[7] if len(row) > 7 else None
        option_type = row[8] if len(row) > 8 else None
        amount = shares if shares is not None else principal
        lines.append(
            f"| {_cell(symbol)} | {_cell(issuer)} | {_cell(security_class)} | {_cell(cusip)} "
            f"| {_fmt_shares(amount)} | {_cell(option_type)} |"
        )
    return "\n".join(lines)


def _build_manager_history(cik: str, manager_name: str, filings: list[ManagerFiling]) -> str | None:
    complete = [
        filing for filing in filings if filing.form_type.upper() in {"13F-HR", "RESTATEMENT"}
    ]
    if not complete:
        return None

    lines = [
        f"# 13F Portfolio History: {manager_name}",
        "",
        f"- **Manager CIK:** {cik}",
        "- **Underlying records:** SEC Form 13F filings",
    ]
    if len(complete) >= 2:
        current, previous = complete[:2]
        current_id = _accession_digits(current.filing_id)
        previous_id = _accession_digits(previous.filing_id)
        comparison = _get_json(f"{_BASE}/data/13f/{current_id}/compare/{previous_id}")
        rows = comparison.get("data", []) if isinstance(comparison, dict) else []
        if rows:
            lines.extend(
                [
                    "",
                    f"## Share Changes: {previous.period} to {current.period}",
                    "",
                    "| Symbol | Issuer | Class | CUSIP | Option | Previous | Current | Change | Change % |",
                    "|---|---|---|---|---|---:|---:|---:|---:|",
                ]
            )
            for row in sorted(rows, key=lambda item: str(item[0] or "")):
                symbol, issuer, security_class, cusip, option_type = row[:5]
                previous_shares, current_shares, change, change_pct = row[5:9]
                lines.append(
                    f"| {_cell(symbol)} | {_cell(issuer)} | {_cell(security_class)} "
                    f"| {_cell(cusip)} | {_cell(option_type)} | {_fmt_shares(previous_shares)} "
                    f"| {_fmt_shares(current_shares)} | {_fmt_shares(change)} "
                    f"| {_fmt_percent(change_pct)} |"
                )

    lines.extend(
        [
            "",
            "## Filing History",
            "",
            "| Period | Holdings | Filing Type | Filed | SEC Accession |",
            "|---|---:|---|---|---|",
        ]
    )
    for filing in filings[:20]:
        lines.append(
            f"| {filing.period} | {filing.holdings} | {filing.form_type} | {_iso_date(filing.filed)} "
            f"| {_format_accession(filing.filing_id)} |"
        )
    return "\n".join(lines)


def _build_manager_stock_history(
    cik: str, cusip: str, manager_name: str, ticker: str
) -> str | None:
    entries = _manager_cusip_history(cik, cusip).get("data", [])
    if not entries:
        return None
    lines = [
        f"# Position History: {manager_name} → {ticker}",
        "",
        f"- **Manager CIK:** {cik}",
        f"- **CUSIP:** {cusip}",
        "- **Underlying records:** SEC Form 13F filings",
        "",
        "| Period | Shares | Filed | SEC Accession |",
        "|---|---:|---|---|",
    ]
    for entry in entries:
        period_info = entry[6]
        filing_info = entry[0]
        filing_slug = (
            filing_info[1] if isinstance(filing_info, list) and len(filing_info) > 1 else ""
        )
        lines.append(
            f"| Q{period_info[1]} {period_info[0]} | {_fmt_shares(entry[3])} | {entry[5]} "
            f"| {_format_accession(filing_slug)} |"
        )
    return "\n".join(lines)


def _write_or_fail(path, markdown: str | None, description: str) -> None:
    if not markdown:
        c.log(f"ERROR: no {description} data could be extracted.")
        sys.exit(1)
    c.emit(c.write_text(path, markdown))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ticker", help="Stock ticker for holder or manager-position queries.")
    parser.add_argument("--manager", help="Manager name or exact 10-digit CIK.")
    parser.add_argument(
        "--history", action="store_true", help="Show history for a stock or manager."
    )
    parser.add_argument("--year", type=int, help="Specific 13F reporting year.")
    parser.add_argument("--quarter", type=int, choices=[1, 2, 3, 4], help="Specific quarter.")
    parser.add_argument("--top", type=int, help="Top stock holders to show (default: 25).")
    c.add_cache_arg(parser)
    args = parser.parse_args()

    if not args.ticker and not args.manager:
        parser.error("provide --ticker, --manager, or both")
    if (args.year is None) != (args.quarter is None):
        parser.error("--year and --quarter must be supplied together")
    if args.top is not None and args.top <= 0:
        parser.error("--top must be positive")
    if args.manager and args.top is not None:
        parser.error("--top applies only to stock-holder queries")
    if args.manager and args.ticker and args.history:
        parser.error("a manager-plus-ticker query already returns position history")

    cache = c.cache_root(args.cache_dir)
    try:
        manager_data = _resolve_manager(args.manager) if args.manager else None
        if args.manager and not manager_data:
            c.log(f"ERROR: could not resolve manager '{args.manager}'.")
            sys.exit(1)

        if args.manager and args.ticker:
            cik, manager_name, _, _ = manager_data
            resolved = _resolve_cusip(args.ticker)
            if not resolved:
                c.log(f"ERROR: could not resolve an exact CUSIP for ticker '{args.ticker}'.")
                sys.exit(1)
            cusip, _, _ = resolved
            markdown = _build_manager_stock_history(cik, cusip, manager_name, args.ticker.upper())
            out_dir = c.company_dir(cache, None, ticker_hint=args.ticker)
            _write_or_fail(
                out_dir / f"13f-position-history_{c.safe_component(cik)}.md",
                markdown,
                "manager-position history",
            )
            return

        if args.ticker:
            resolved = _resolve_cusip(args.ticker)
            if not resolved:
                c.log(f"ERROR: could not resolve an exact CUSIP for ticker '{args.ticker}'.")
                sys.exit(1)
            cusip, _symbol, issuer = resolved
            out_dir = c.company_dir(cache, None, ticker_hint=args.ticker)
            if args.history:
                _write_or_fail(
                    out_dir / f"13f-history_{args.ticker.upper()}.md",
                    _build_stock_history(args.ticker.upper(), cusip, issuer),
                    "stock-holder history",
                )
                return
            year, quarter = (
                (args.year, args.quarter) if args.year is not None else _latest_quarter()
            )
            _write_or_fail(
                out_dir / f"13f-holders_{year}-Q{quarter}.md",
                _build_stock_holders(
                    args.ticker.upper(), cusip, issuer, year, quarter, args.top or 25
                ),
                f"Q{quarter} {year} holder",
            )
            return

        cik, manager_name, _, manager_html = manager_data
        filings = _parse_manager_filings(manager_html)
        out_dir = cache / "managers"
        out_dir.mkdir(parents=True, exist_ok=True)
        if args.history:
            _write_or_fail(
                out_dir / f"13f-manager-history_{c.safe_component(cik)}.md",
                _build_manager_history(cik, manager_name, filings),
                "manager filing-history",
            )
            return
        selected = _select_manager_filing(filings, args.year, args.quarter)
        if not selected:
            period = f"Q{args.quarter} {args.year}" if args.year else "latest period"
            c.log(f"ERROR: no complete manager portfolio found for {period}.")
            sys.exit(1)
        _write_or_fail(
            out_dir / f"13f-manager_{c.safe_component(cik)}_{selected.period.replace(' ', '-')}.md",
            _build_manager_holdings(cik, manager_name, selected),
            "manager holding",
        )
    except FetchFailure as exc:
        c.log(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
