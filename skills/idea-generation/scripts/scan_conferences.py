"""Discover investor-event announcements through SEC 8-K full-text search.

Targeted EFTS queries produce candidates. Most candidates are then classified
against filing text; exact investor-day queries can survive unavailable primary
text because the indexed phrase and item filter are the signal. Reports disclose
pagination caps and retrieval failures.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c

_MAX_RESULTS_PER_QUERY = 300

# Specific queries precede the broad ``conference`` query because candidate
# deduplication retains the first matching route.
_CLASSIFIER: dict = {
    "queries": {
        '"investor day"': "8.01",
        '"capital markets day"': None,
        '"fireside chat"': None,
        "symposium": None,
        '"forum"': "7.01",
        "conference": None,
    },
    "trusted_index_queries": ['"investor day"', '"capital markets day"'],
    "exclusions": [
        "conference call",
        "conference call and webcast",
        "exclusive forum",
        "forum selection",
        "alternative forum",
    ],
    "attendance_patterns": [
        r"will present",
        r"presenting at",
        r"participate in",
        r"scheduled to present",
        r"speak at",
        r"participation at",
        r"will attend",
        r"will be attending",
    ],
}


def _all_occurrences_excluded(text: str, signal_word: str, exclusions: list[str]) -> bool:
    """Return whether every signal occurrence lies near an excluded phrase."""
    positions = [
        match.start() for match in re.finditer(re.escape(signal_word), text, re.IGNORECASE)
    ]
    if not positions:
        return False
    for position in positions:
        window = text[max(0, position - 60) : position + 60 + len(signal_word)].lower()
        if not any(exclusion.lower() in window for exclusion in exclusions):
            return False
    return True


def _classify(text: str, query: str, params: dict) -> str:
    """Classify a downloaded candidate filing."""
    if query in params["trusted_index_queries"]:
        return "ACCEPT"

    signal_word = query.strip('"').split()[0]
    if not re.search(re.escape(signal_word), text, re.IGNORECASE):
        return "REJECT_NO_PRIMARY_TEXT_MATCH"
    if _all_occurrences_excluded(text, signal_word, params["exclusions"]):
        return "REJECT_EXCLUSION"
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in params["attendance_patterns"]):
        return "ACCEPT"
    return "REJECT_NO_ATTENDANCE_PATTERN"


def _get_candidates(
    start: str,
    end: str,
    params: dict,
    max_per_query: int = _MAX_RESULTS_PER_QUERY,
) -> tuple[dict[str, dict], list[dict]]:
    """Search, paginate, and deduplicate EFTS candidates by accession."""
    import edgar

    candidates: dict[str, dict] = {}
    query_stats = []

    for query, item_filter in params["queries"].items():
        label = f"{query!r}" + (f" items={item_filter!r}" if item_filter else "")
        c.log(f"  EFTS: {label} ...")
        stat = {
            "query": query,
            "item_filter": item_filter,
            "total": 0,
            "fetched": 0,
            "truncated": False,
            "error": "",
        }
        try:
            search = edgar.search_filings(
                query=query,
                forms="8-K",
                items=item_filter,
                start_date=start,
                end_date=end,
                limit=min(max_per_query, 100),
            )
            if search is None:
                raise RuntimeError("EFTS returned no search object")
            stat["total"] = int(getattr(search, "total", 0) or 0)
            fetched = len(list(search))
            target = min(stat["total"], max_per_query)
            if fetched < target:
                search = search.fetch_more(target - fetched)
            rows = list(search)[:max_per_query]
            stat["fetched"] = len(rows)
            stat["truncated"] = stat["fetched"] < stat["total"]
        except Exception as exc:
            stat["error"] = str(exc)
            c.log(f"    ERROR: {exc}")
            query_stats.append(stat)
            continue

        new_count = 0
        for result in rows:
            accession = str(getattr(result, "accession_number", "") or "")
            if accession and accession not in candidates:
                candidates[accession] = {"result": result, "query": query}
                new_count += 1
        c.log(f"    → {new_count} new candidates; fetched {stat['fetched']} of {stat['total']}")
        query_stats.append(stat)

    return candidates, query_stats


def _extract_event_name(text: str) -> str | None:
    """Extract a best-effort event name from filing text."""
    patterns = [
        r"(?:at|the)\s+([\w\s&\-']{10,80}?"
        r"(?:Conference|Forum|Symposium|Investor Day|Capital Markets Day|Fireside Chat))",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = re.sub(r"[.,;:\s]+$", "", match.group(1)).strip()
            if len(name) >= 10:
                return name[:120]
    return None


def scan_conferences(
    start: str,
    end: str,
    params: dict,
    mcap_data: dict,
) -> tuple[list[dict], dict]:
    """Run candidate retrieval, classification, and enrichment."""
    c.log(f"Scanning 8-K filings for investor events: {start} to {end}")
    candidates, query_stats = _get_candidates(start, end, params)
    if query_stats and all(stat["error"] for stat in query_stats):
        raise RuntimeError("all EFTS event queries failed")

    c.log(f"  {len(candidates)} unique candidates after EFTS deduplication")
    stats = {
        "checked": 0,
        "no_ticker": 0,
        "out_of_universe_or_unresolved": 0,
        "text_retrieval_errors": 0,
        "rejected": 0,
        "accepted": 0,
        "query_stats": query_stats,
    }
    events = []

    for accession, candidate in candidates.items():
        result = candidate["result"]
        query = candidate["query"]
        stats["checked"] += 1

        company_raw = str(getattr(result, "company", "Unknown"))
        cik = str(getattr(result, "cik", "")).lstrip("0")
        filed = str(getattr(result, "filed", ""))
        ticker = c.extract_ticker(company_raw)
        if not ticker:
            stats["no_ticker"] += 1
            continue

        mcap = c.get_market_cap(ticker, mcap_data)
        if not c.in_universe(mcap):
            stats["out_of_universe_or_unresolved"] += 1
            continue

        trusted_index_match = query in params["trusted_index_queries"]
        filing_text = ""
        try:
            filing_text = result.get_filing().text() or ""
        except Exception as exc:
            stats["text_retrieval_errors"] += 1
            c.log(f"  WARNING: could not fetch filing text for {accession}: {exc}")

        if trusted_index_match:
            verdict = "ACCEPT"
        elif not filing_text:
            continue
        else:
            verdict = _classify(filing_text, query, params)

        if verdict != "ACCEPT":
            stats["rejected"] += 1
            continue
        stats["accepted"] += 1

        try:
            import yfinance as yf

            info = yf.Ticker(ticker).info or {}
        except Exception:
            info = {}

        events.append(
            {
                "ticker": ticker,
                "company": info.get("shortName") or info.get("longName") or company_raw,
                "sector": info.get("sector", "n/a"),
                "mcap": mcap,
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "filed": filed,
                "event": _extract_event_name(filing_text) or "(see filing)",
                "matched_query": query.strip('"'),
                "accession": accession,
                "source_url": c.sec_filing_url(cik, accession),
            }
        )

    events.sort(key=lambda event: (event["filed"], event["ticker"]), reverse=True)
    c.log(f"  Done — {stats}")
    return events, stats


def _render_markdown(start: str, end: str, events: list[dict], stats: dict) -> str:
    """Render event candidates with source and coverage notes."""
    lines = [
        f"# Investor-Event Discovery: {start} to {end}\n",
        f"Found **{len(events)}** companies in the {c.universe_label()} universe.\n",
        "Matches are heuristic leads. Verify the event name, date, and participation in the linked filing.\n",
    ]

    truncated = [stat for stat in stats["query_stats"] if stat["truncated"]]
    query_errors = [stat for stat in stats["query_stats"] if stat["error"]]
    metadata_omissions = stats["no_ticker"] or stats["out_of_universe_or_unresolved"]
    if truncated or query_errors or stats["text_retrieval_errors"] or metadata_omissions:
        lines.append("## Coverage notes\n")
        for stat in truncated:
            lines.append(
                f"- Query `{stat['query']}` fetched {stat['fetched']} of {stat['total']} matches."
            )
        for stat in query_errors:
            lines.append(f"- Query `{stat['query']}` failed: {stat['error']}")
        if stats["text_retrieval_errors"]:
            lines.append(
                f"- Filing text retrieval failed for {stats['text_retrieval_errors']} candidate(s)."
            )
        if stats["no_ticker"]:
            lines.append(
                f"- EFTS supplied no parseable ticker for {stats['no_ticker']} candidate(s)."
            )
        if stats["out_of_universe_or_unresolved"]:
            lines.append(
                f"- {stats['out_of_universe_or_unresolved']} candidate(s) were outside the "
                "market-cap bounds or lacked a Yahoo market cap."
            )
        lines.append("")

    if not events:
        lines.append(
            "No classified investor-event announcements were found in completed coverage.\n"
        )
        return "\n".join(lines)

    lines += [
        "| # | Ticker | Company | Sector | Mkt Cap | Price | Filed | Matched query | Event | Source |",
        "|---|---|---|---|---:|---:|---|---|---|---|",
    ]
    for index, event in enumerate(events, 1):
        price = event.get("price")
        lines.append(
            f"| {index} | {c.md_cell(event['ticker'])} | {c.md_cell(event['company'])} | "
            f"{c.md_cell(event['sector'])} | {c.fmt_mcap(event['mcap'])} | "
            f"{f'${price:.2f}' if price is not None else 'n/a'} | {event['filed']} | "
            f"{c.md_cell(event['matched_query'])} | {c.md_cell(event['event'])} | "
            f"[{event['accession']}]({event['source_url']}) |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Run the investor-event discovery CLI."""
    parser = argparse.ArgumentParser(description="Investor-event discovery via 8-K filings.")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD.")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD.")
    c.add_identity_arg(parser)
    c.add_cache_arg(parser)
    args = parser.parse_args()

    try:
        start = datetime.strptime(args.start, "%Y-%m-%d").date()
        end = datetime.strptime(args.end, "%Y-%m-%d").date()
    except ValueError as exc:
        parser.error(str(exc))
    if start > end:
        parser.error("--start must not be later than --end.")

    c.resolve_identity(args.identity)
    cache = c.cache_root(args.cache_dir)
    mcap_data = c.load_mcap_cache(cache)
    try:
        events, stats = scan_conferences(
            start.isoformat(),
            end.isoformat(),
            _CLASSIFIER,
            mcap_data,
        )
    except RuntimeError as exc:
        c.log(f"ERROR: {exc}")
        sys.exit(1)
    finally:
        c.save_mcap_cache(cache, mcap_data)

    report = _render_markdown(start.isoformat(), end.isoformat(), events, stats)
    c.write_output(cache, "conferences", f"{start.isoformat()}_to_{end.isoformat()}", report)

    incomplete = (
        any(stat["truncated"] or stat["error"] for stat in stats["query_stats"])
        or stats["text_retrieval_errors"] > 0
    )
    if incomplete:
        c.log("ERROR: emitted report has incomplete source coverage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
