"""Scan Form 4 purchases and Schedule 13D filings.

Form 4 transaction code ``P`` rows are preserved individually. Clusters use
distinct reporting-owner identities, and price-move context is measured as of
the transaction date rather than the day the script runs.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c

_TRADING_DAYS_IN_MONTH = 22


def _weekdays(end_date: str, lookback: int) -> list[str]:
    """Return the requested number of weekdays ending on or before a date."""
    end = datetime.strptime(end_date, "%Y-%m-%d")
    dates = []
    current = end
    while len(dates) < lookback:
        if current.weekday() < 5:
            dates.append(current.strftime("%Y-%m-%d"))
        current -= timedelta(days=1)
    return list(reversed(dates))


def _post_discord(webhook_url: str, embeds: list[dict]) -> None:
    """Post Discord embeds in API-sized batches."""
    import requests

    for index in range(0, len(embeds), 10):
        try:
            response = requests.post(
                webhook_url, json={"embeds": embeds[index : index + 10]}, timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Discord webhook failed: {exc}") from exc


def _number(value) -> float | None:
    """Return a finite float or None."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _date(value, fallback: str) -> str:
    """Return a YYYY-MM-DD date from a dataframe value."""
    try:
        import pandas as pd

        parsed = pd.to_datetime(value, errors="coerce")
        if not pd.isna(parsed):
            return parsed.date().isoformat()
    except Exception:
        pass
    return fallback


def _owner_identity(ownership, insider_name: str) -> tuple[str, str]:
    """Return a stable reporting-owner identity and optional CIK."""
    owners = list(getattr(getattr(ownership, "reporting_owners", None), "owners", []) or [])
    normalized = "".join(ch for ch in insider_name.upper() if ch.isalnum())
    for owner in owners:
        owner_name = str(getattr(owner, "name", ""))
        owner_normalized = "".join(ch for ch in owner_name.upper() if ch.isalnum())
        if len(owners) == 1 or owner_normalized == normalized:
            cik = str(getattr(owner, "cik", "") or "").lstrip("0")
            if cik:
                return f"cik:{cik}", cik
    return f"name:{normalized}", ""


def compute_move_context(ticker: str, as_of_dates: list[str]) -> dict[str, dict | None]:
    """Compute event-date 22-trading-day returns and rolling-return z-scores."""
    import pandas as pd
    import yfinance as yf

    unique_dates = sorted(set(as_of_dates))
    if not unique_dates:
        return {}
    first = datetime.strptime(unique_dates[0], "%Y-%m-%d") - timedelta(days=450)
    last = datetime.strptime(unique_dates[-1], "%Y-%m-%d") + timedelta(days=1)

    try:
        history = yf.Ticker(ticker).history(
            start=first.strftime("%Y-%m-%d"),
            end=last.strftime("%Y-%m-%d"),
            auto_adjust=True,
        )
        close = history["Close"].dropna().copy()
        close.index = pd.DatetimeIndex(close.index).tz_localize(None).normalize()
    except Exception:
        return {date: None for date in unique_dates}

    contexts: dict[str, dict | None] = {}
    for date in unique_dates:
        cutoff = pd.Timestamp(date)
        series = close[close.index <= cutoff]
        if len(series) < 80:
            contexts[date] = None
            continue

        rolling_returns = series.pct_change(_TRADING_DAYS_IN_MONTH).dropna()
        if len(rolling_returns) < 41:
            contexts[date] = None
            continue
        current_return = float(rolling_returns.iloc[-1])
        baseline = rolling_returns.iloc[:-1].tail(252)
        baseline_std = float(baseline.std())
        if not math.isfinite(baseline_std) or baseline_std == 0:
            contexts[date] = None
            continue
        baseline_mean = float(baseline.mean())
        contexts[date] = {
            "return_22d": current_return,
            "baseline_mean": baseline_mean,
            "baseline_std": baseline_std,
            "zscore": (current_return - baseline_mean) / baseline_std,
        }
    return contexts


def tag_move_context(
    purchases_by_ticker: dict[str, list[dict]],
    zscore_threshold: float = 1.5,
) -> None:
    """Attach event-date price context and dip/rip labels to purchases."""
    c.log(f"Computing event-date move context for {len(purchases_by_ticker)} tickers...")
    for index, (ticker, purchases) in enumerate(purchases_by_ticker.items()):
        if index and index % 20 == 0:
            c.log(f"  Move context: {index}/{len(purchases_by_ticker)}...")
        contexts = compute_move_context(
            ticker, [purchase["transaction_date"] for purchase in purchases]
        )
        for purchase in purchases:
            context = contexts.get(purchase["transaction_date"])
            purchase["return_22d"] = context["return_22d"] if context else None
            purchase["zscore"] = context["zscore"] if context else None
            zscore = purchase["zscore"]
            if zscore is not None and zscore >= zscore_threshold:
                purchase["signal"] = "rip"
            elif zscore is not None and zscore <= -zscore_threshold:
                purchase["signal"] = "dip"
            else:
                purchase["signal"] = None


def scan_form4s(dates: list[str], mcap_data: dict) -> tuple[dict[str, list[dict]], dict]:
    """Collect code-P transactions from Form 4 filings received on given dates."""
    import edgar

    purchases_by_ticker: dict[str, list[dict]] = defaultdict(list)
    stats = {
        "failed_dates": [],
        "filings_seen": 0,
        "filings_parsed": 0,
        "parse_errors": 0,
        "unresolved_market_cap": 0,
    }

    for requested_date in dates:
        c.log(f"Fetching Form 4 index for {requested_date}...")
        try:
            parsed_date = datetime.strptime(requested_date, "%Y-%m-%d")
            filings = edgar.get_filings(
                year=parsed_date.year,
                quarter=(parsed_date.month - 1) // 3 + 1,
                form="4",
                filing_date=requested_date,
                amendments=False,
            )
        except Exception as exc:
            c.log(f"  ERROR: could not fetch Form 4 index: {exc}")
            stats["failed_dates"].append(requested_date)
            continue
        if filings is None:
            continue

        c.log(f"  Found {len(filings)} Form 4 filings")
        for index, filing in enumerate(filings):
            stats["filings_seen"] += 1
            try:
                ownership = filing.obj()
                transactions = ownership.to_dataframe()
                stats["filings_parsed"] += 1
            except Exception:
                stats["parse_errors"] += 1
                continue
            if transactions is None or transactions.empty or "Code" not in transactions:
                continue
            purchases = transactions[transactions["Code"] == "P"]
            if purchases.empty:
                continue

            ticker = str(getattr(ownership.issuer, "ticker", "") or "").upper().strip()
            if not ticker:
                continue
            mcap = c.get_market_cap(ticker, mcap_data)
            if mcap is None:
                stats["unresolved_market_cap"] += 1
                continue
            if not c.in_universe(mcap):
                continue

            filing_date = str(getattr(filing, "filing_date", requested_date))
            accession = str(
                getattr(filing, "accession_no", "") or getattr(filing, "accession_number", "") or ""
            )
            cik = str(getattr(ownership.issuer, "cik", "") or "").lstrip("0")
            source_url = c.sec_filing_url(cik, accession) if cik and accession else ""

            for _, row in purchases.iterrows():
                shares = _number(row.get("Shares"))
                if shares is None or shares <= 0:
                    continue
                price = _number(row.get("Price"))
                remaining = _number(row.get("Remaining Shares"))
                insider = str(row.get("Insider") or getattr(ownership, "insider_name", "Unknown"))
                owner_id, owner_cik = _owner_identity(ownership, insider)
                role = str(row.get("Position") or getattr(ownership, "position", "Unknown"))
                transaction_date = _date(row.get("Date"), filing_date)
                purchases_by_ticker[ticker].append(
                    {
                        "insider": insider,
                        "insider_id": owner_id,
                        "insider_cik": owner_cik,
                        "role": role,
                        "shares": shares,
                        "price": price,
                        "transaction_date": transaction_date,
                        "filing_date": filing_date,
                        "company": str(getattr(ownership.issuer, "name", ticker)),
                        "mcap": mcap,
                        "remaining": remaining,
                        "shares_out": c.get_cached_shares_out(ticker, mcap_data),
                        "accession": accession,
                        "source_url": source_url,
                    }
                )
            if index and index % 50 == 0:
                c.log(f"  Parsed {index}/{len(filings)} filings...")

    return dict(purchases_by_ticker), stats


def detect_clusters(purchases_by_ticker: dict[str, list[dict]]) -> list[dict]:
    """Find tickers with purchases by at least two reporting owners."""
    clusters = []
    for ticker, purchases in purchases_by_ticker.items():
        distinct_owners = {purchase["insider_id"] for purchase in purchases}
        if len(distinct_owners) < 2:
            continue
        clusters.append(
            {
                "ticker": ticker,
                "company": purchases[0]["company"],
                "mcap": purchases[0]["mcap"],
                "insiders": purchases,
                "num_insiders": len(distinct_owners),
                "date_range": (
                    f"{min(p['transaction_date'] for p in purchases)} to "
                    f"{max(p['transaction_date'] for p in purchases)}"
                ),
                "signals": sorted({p["signal"] for p in purchases if p.get("signal")}),
            }
        )
    clusters.sort(key=lambda cluster: cluster["num_insiders"], reverse=True)
    return clusters


def collect_notable_singles(
    purchases_by_ticker: dict[str, list[dict]], cluster_tickers: set[str]
) -> list[dict]:
    """Collect event-context labels outside cluster tickers."""
    notable = [
        {**purchase, "ticker": ticker}
        for ticker, purchases in purchases_by_ticker.items()
        if ticker not in cluster_tickers
        for purchase in purchases
        if purchase.get("signal")
    ]
    notable.sort(key=lambda purchase: abs(purchase.get("zscore") or 0), reverse=True)
    return notable


def scan_13d(dates: list[str], mcap_data: dict) -> tuple[list[dict], dict]:
    """Collect Schedule 13D and 13D/A filings without presuming activism."""
    import edgar

    results = []
    stats = {"failed_dates": [], "unresolved_ticker": 0, "unresolved_market_cap": 0}
    for requested_date in dates:
        c.log(f"Fetching Schedule 13D index for {requested_date}...")
        try:
            parsed_date = datetime.strptime(requested_date, "%Y-%m-%d")
            filings = edgar.get_filings(
                year=parsed_date.year,
                quarter=(parsed_date.month - 1) // 3 + 1,
                form=["SC 13D", "SC 13D/A"],
                filing_date=requested_date,
            )
        except Exception as exc:
            c.log(f"  ERROR: could not fetch Schedule 13D index: {exc}")
            stats["failed_dates"].append(requested_date)
            continue
        if filings is None:
            continue

        for filing in filings:
            issuer_cik = str(getattr(filing, "cik", "") or "").lstrip("0")
            ticker = None
            try:
                from edgar import Company

                tickers = getattr(Company(int(issuer_cik)), "tickers", [])
                if tickers:
                    ticker = str(next(iter(tickers))).upper().replace(".", "-")
            except Exception:
                pass
            if not ticker:
                stats["unresolved_ticker"] += 1
                continue

            mcap = c.get_market_cap(ticker, mcap_data)
            if mcap is None:
                stats["unresolved_market_cap"] += 1
                continue
            if not c.in_universe(mcap):
                continue

            blockholders = "(see filing)"
            try:
                schedule = filing.obj()
                names = [
                    str(person.name)
                    for person in (getattr(schedule, "reporting_persons", []) or [])
                    if getattr(person, "name", None)
                ]
                if names:
                    blockholders = "; ".join(dict.fromkeys(names))
            except Exception:
                pass

            accession = str(
                getattr(filing, "accession_no", "") or getattr(filing, "accession_number", "") or ""
            )
            results.append(
                {
                    "ticker": ticker,
                    "company": str(getattr(filing, "company", "Unknown")),
                    "mcap": mcap,
                    "blockholders": blockholders,
                    "filing_date": str(getattr(filing, "filing_date", requested_date)),
                    "form": str(getattr(filing, "form", "SC 13D")),
                    "accession": accession,
                    "source_url": c.sec_filing_url(issuer_cik, accession),
                }
            )
    return results, stats


def _signal_badge(signal: str | None) -> str:
    return " 🚀" if signal == "rip" else " 🔻" if signal == "dip" else ""


def _zscore(value: float | None) -> str:
    return "n/a" if value is None else f"{value:+.1f}σ"


def _return(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:+.1f}%"


def _price(value: float | None) -> str:
    return "n/a" if value is None else f"${value:.2f}"


def _pct_of_holding(shares: float, remaining: float | None) -> str:
    return "n/a" if not remaining or remaining <= 0 else f"{shares / remaining * 100:.1f}%"


def _pct_of_outstanding(shares: float, shares_out: int | None) -> str:
    if not shares_out or shares_out <= 0:
        return "n/a"
    percentage = shares / shares_out * 100
    return "<0.01%" if percentage < 0.01 else f"{percentage:.2f}%"


def _build_summary(
    purchases_by_ticker: dict[str, list[dict]],
    clusters: list[dict],
    filings_13d: list[dict],
    mcap_data: dict,
    threshold: float,
) -> list[str]:
    """Build report-level counts and sector totals."""
    purchases = [purchase for rows in purchases_by_ticker.values() for purchase in rows]
    priced = [purchase for purchase in purchases if purchase["price"] is not None]
    total_dollar = sum(purchase["shares"] * purchase["price"] for purchase in priced)
    lines = [
        "## Summary\n",
        "| Metric | Value |",
        "|---|---:|",
        f"| Code-P transaction rows ({c.universe_label()}) | {len(purchases)} |",
        f"| Unique tickers | {len(purchases_by_ticker)} |",
        f"| Distinct reporting owners | {len({p['insider_id'] for p in purchases})} |",
        f"| Priced purchase value | ${total_dollar:,.0f} |",
        f"| Cluster tickers | {len(clusters)} |",
        f"| Dip rows (≤ -{threshold}σ) | {sum(p.get('signal') == 'dip' for p in purchases)} |",
        f"| Rip rows (≥ +{threshold}σ) | {sum(p.get('signal') == 'rip' for p in purchases)} |",
        f"| Schedule 13D filings | {len(filings_13d)} |",
        "",
    ]

    if priced:
        largest = max(priced, key=lambda purchase: purchase["shares"] * purchase["price"])
        ticker = next(t for t, rows in purchases_by_ticker.items() if largest in rows)
        lines.append(
            f"**Largest priced row:** {c.md_cell(largest['insider'])} bought "
            f"${largest['shares'] * largest['price']:,.0f} of {ticker}.\n"
        )

    sector_counts: dict[str, int] = defaultdict(int)
    sector_dollars: dict[str, float] = defaultdict(float)
    for ticker, rows in purchases_by_ticker.items():
        sector = c.get_cached_sector(ticker, mcap_data)
        sector_counts[sector] += len(rows)
        sector_dollars[sector] += sum(
            row["shares"] * row["price"] for row in rows if row["price"] is not None
        )
    if sector_counts:
        lines += [
            "### Sector breakdown\n",
            "| Sector | Transaction rows | Priced value |",
            "|---|---:|---:|",
        ]
        for sector, dollars in sorted(
            sector_dollars.items(), key=lambda item: item[1], reverse=True
        ):
            lines.append(f"| {c.md_cell(sector)} | {sector_counts[sector]} | ${dollars:,.0f} |")
        lines.append("")
    return lines


def _coverage_notes(form4_stats: dict, schedule_stats: dict) -> list[str]:
    """Render omissions that affect interpretation of an otherwise valid report."""
    notes = []
    if form4_stats["failed_dates"]:
        notes.append(
            f"Form 4 index retrieval failed for: {', '.join(form4_stats['failed_dates'])}."
        )
    if schedule_stats["failed_dates"]:
        notes.append(
            f"Schedule 13D index retrieval failed for: {', '.join(schedule_stats['failed_dates'])}."
        )
    if form4_stats["parse_errors"]:
        notes.append(
            f"{form4_stats['parse_errors']} of {form4_stats['filings_seen']} Form 4 filings could not be parsed."
        )
    if schedule_stats["unresolved_ticker"]:
        notes.append(
            f"No current ticker resolved for {schedule_stats['unresolved_ticker']} Schedule 13D filing(s); "
            "those were omitted."
        )
    unresolved = form4_stats["unresolved_market_cap"] + schedule_stats["unresolved_market_cap"]
    if unresolved:
        notes.append(
            f"Yahoo market cap was unavailable for {unresolved} filing ticker lookup(s); those were omitted."
        )
    if not notes:
        return []
    return ["## Coverage notes\n", *[f"- {note}" for note in notes], ""]


def _source(purchase: dict) -> str:
    accession = purchase.get("accession") or "filing"
    url = purchase.get("source_url")
    return f"[{accession}]({url})" if url else accession


def _build_markdown(
    purchases_by_ticker: dict[str, list[dict]],
    clusters: list[dict],
    notable: list[dict],
    filings_13d: list[dict],
    dates: list[str],
    mcap_data: dict,
    form4_stats: dict,
    schedule_stats: dict,
    threshold: float,
) -> str:
    """Build the source-linked scan report."""
    date_range = f"{dates[0]} to {dates[-1]}" if len(dates) > 1 else dates[0]
    lines = [f"# Insider Filing Scan ({date_range})\n"]
    lines.extend(_coverage_notes(form4_stats, schedule_stats))
    lines.extend(_build_summary(purchases_by_ticker, clusters, filings_13d, mcap_data, threshold))

    lines.append(f"## Cluster purchases ({len(clusters)} tickers)\n")
    lines.append(
        "A cluster has code-P rows from at least two distinct reporting owners in Form 4 filings received during the scan window.\n"
    )
    if not clusters:
        lines.append("No clusters were detected in completed coverage.\n")
    for cluster in clusters:
        badges = "".join(_signal_badge(signal) for signal in cluster["signals"])
        lines += [
            f"### {cluster['ticker']} — {c.md_cell(cluster['company'])}{badges}",
            f"- **Market cap:** {c.fmt_mcap(cluster['mcap'])}",
            f"- **Distinct reporting owners:** {cluster['num_insiders']}",
            f"- **Transaction-date range:** {cluster['date_range']}",
            "",
            "| Insider | Role | Shares | Price | % of Holding | % of O/S | Transaction date | Filed | Source |",
            "|---|---|---:|---:|---:|---:|---|---|---|",
        ]
        for purchase in cluster["insiders"]:
            lines.append(
                f"| {c.md_cell(purchase['insider'])} | {c.md_cell(purchase['role'])} | "
                f"{purchase['shares']:,.0f} | {_price(purchase['price'])} | "
                f"{_pct_of_holding(purchase['shares'], purchase['remaining'])} | "
                f"{_pct_of_outstanding(purchase['shares'], purchase['shares_out'])} | "
                f"{purchase['transaction_date']} | {purchase['filing_date']} | {_source(purchase)} |"
            )
        lines.append("")

    if notable:
        dips = [purchase for purchase in notable if purchase["signal"] == "dip"]
        rips = [purchase for purchase in notable if purchase["signal"] == "rip"]
        lines += [
            f"## Event-date move context ({len(dips)} dip, {len(rips)} rip)\n",
            "The 22-trading-day return is compared with the stock's prior rolling 22-day returns as of the transaction date.\n",
        ]
        for label, rows in (("Dip", dips), ("Rip", rips)):
            if not rows:
                continue
            lines += [
                f"### {label} rows\n",
                "| Ticker | Company | Insider | Shares | Price | 22d Move | Z-score | Transaction date | Filed | Source |",
                "|---|---|---|---:|---:|---:|---:|---|---|---|",
            ]
            for purchase in rows:
                lines.append(
                    f"| {purchase['ticker']} | {c.md_cell(purchase['company'])} | "
                    f"{c.md_cell(purchase['insider'])} | {purchase['shares']:,.0f} | "
                    f"{_price(purchase['price'])} | {_return(purchase['return_22d'])} | "
                    f"{_zscore(purchase['zscore'])} | {purchase['transaction_date']} | "
                    f"{purchase['filing_date']} | {_source(purchase)} |"
                )
            lines.append("")

    lines.append(f"## Schedule 13D filings ({len(filings_13d)})\n")
    lines.append(
        "A Schedule 13D is a beneficial-ownership filing under Section 13(d); it does not by itself establish an activist campaign.\n"
    )
    if not filings_13d:
        lines.append("No Schedule 13D or 13D/A filings were found in completed coverage.\n")
    else:
        lines += [
            "| Ticker | Issuer | Market Cap | Reporting person(s) | Filed | Form | Source |",
            "|---|---|---:|---|---|---|---|",
        ]
        for filing in filings_13d:
            lines.append(
                f"| {filing['ticker']} | {c.md_cell(filing['company'])} | "
                f"{c.fmt_mcap(filing['mcap'])} | {c.md_cell(filing['blockholders'])} | "
                f"{filing['filing_date']} | {filing['form']} | "
                f"[{filing['accession']}]({filing['source_url']}) |"
            )
        lines.append("")
    return "\n".join(lines)


def _build_discord_embeds(
    clusters: list[dict], notable: list[dict], filings_13d: list[dict]
) -> list[dict]:
    """Build concise, source-linked Discord alerts."""
    embeds = []
    for cluster in clusters:
        descriptions = [
            f"• {row['insider']} ({row['role']}) — {row['shares']:,.0f} shares @ {_price(row['price'])}"
            for row in cluster["insiders"]
        ]
        embeds.append(
            {
                "title": f"Insider purchase cluster — {cluster['ticker']} ({cluster['company']})",
                "url": cluster["insiders"][0]["source_url"],
                "color": 0x2ECC71,
                "description": "\n".join(descriptions),
                "fields": [
                    {"name": "Market Cap", "value": c.fmt_mcap(cluster["mcap"]), "inline": True},
                    {"name": "Owners", "value": str(cluster["num_insiders"]), "inline": True},
                    {"name": "Transaction dates", "value": cluster["date_range"], "inline": True},
                ],
            }
        )
    for purchase in notable:
        label = "Dip" if purchase["signal"] == "dip" else "Rip"
        embeds.append(
            {
                "title": f"{label} purchase context — {purchase['ticker']} ({purchase['company']})",
                "url": purchase["source_url"],
                "color": 0x3498DB if label == "Dip" else 0xE74C3C,
                "description": (
                    f"{purchase['insider']} ({purchase['role']}) — "
                    f"{purchase['shares']:,.0f} shares @ {_price(purchase['price'])}"
                ),
                "fields": [
                    {"name": "22d move", "value": _return(purchase["return_22d"]), "inline": True},
                    {"name": "Z-score", "value": _zscore(purchase["zscore"]), "inline": True},
                    {
                        "name": "Transaction date",
                        "value": purchase["transaction_date"],
                        "inline": True,
                    },
                ],
            }
        )
    for filing in filings_13d:
        embeds.append(
            {
                "title": f"Schedule 13D filing — {filing['ticker']} ({filing['company']})",
                "url": filing["source_url"],
                "color": 0xE67E22,
                "fields": [
                    {
                        "name": "Reporting person(s)",
                        "value": filing["blockholders"],
                        "inline": False,
                    },
                    {"name": "Market Cap", "value": c.fmt_mcap(filing["mcap"]), "inline": True},
                    {"name": "Filed", "value": filing["filing_date"], "inline": True},
                ],
            }
        )
    return embeds


def main() -> None:
    """Run the insider-filing scan CLI."""
    parser = argparse.ArgumentParser(description="Scan Form 4 purchases and Schedule 13D filings.")
    parser.add_argument(
        "--date", required=True, help='End filing date (YYYY-MM-DD, "today", or "yesterday").'
    )
    parser.add_argument("--lookback", type=int, default=5, help="Weekdays to scan (default: 5).")
    parser.add_argument(
        "--zscore", type=float, default=1.5, help="Absolute dip/rip threshold (default: 1.5)."
    )
    parser.add_argument("--webhook", help="Discord webhook URL (else $DISCORD_WEBHOOK_URL).")
    c.add_identity_arg(parser)
    c.add_cache_arg(parser)
    args = parser.parse_args()

    if args.lookback < 1:
        parser.error("--lookback must be at least 1.")
    if args.zscore <= 0:
        parser.error("--zscore must be greater than zero.")

    c.resolve_identity(args.identity)
    cache = c.cache_root(args.cache_dir)
    end_date = c.parse_date(args.date)
    dates = _weekdays(end_date, args.lookback)
    c.log(f"Scanning {len(dates)} weekdays: {dates[0]} to {dates[-1]}")

    mcap_data = c.load_mcap_cache(cache)
    try:
        purchases, form4_stats = scan_form4s(dates, mcap_data)
        filings_13d, schedule_stats = scan_13d(dates, mcap_data)
        if purchases:
            tag_move_context(purchases, args.zscore)
        clusters = detect_clusters(purchases)
        notable = collect_notable_singles(purchases, {cluster["ticker"] for cluster in clusters})
    finally:
        c.save_mcap_cache(cache, mcap_data)

    report = _build_markdown(
        purchases,
        clusters,
        notable,
        filings_13d,
        dates,
        mcap_data,
        form4_stats,
        schedule_stats,
        args.zscore,
    )
    c.write_output(cache, "insiders", end_date, report)

    webhook = args.webhook or os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook:
        embeds = _build_discord_embeds(clusters, notable, filings_13d)
        if embeds:
            try:
                _post_discord(webhook, embeds)
            except RuntimeError as exc:
                c.log(f"ERROR: {exc}")
                sys.exit(1)

    total_parser_failure = form4_stats["filings_seen"] > 0 and form4_stats["filings_parsed"] == 0
    if form4_stats["failed_dates"] or schedule_stats["failed_dates"] or total_parser_failure:
        c.log("ERROR: emitted report has incomplete SEC index or parser coverage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
