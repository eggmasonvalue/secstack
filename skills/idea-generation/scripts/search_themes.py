"""Discover issuers through SEC EFTS full-text keyword matches.

The report distinguishes matching filing documents from keyword occurrences and
discloses when ``--limit`` truncates the server result set.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c


def _resolve_ticker_for_cik(cik: str) -> str | None:
    """Resolve the first issuer ticker exposed by edgartools."""
    try:
        from edgar import Company

        company = Company(int(cik.lstrip("0")))
        tickers = getattr(company, "tickers", [])
        if tickers:
            return str(next(iter(tickers))).upper().replace(".", "-")
    except Exception:
        pass
    return None


def search_and_filter(
    keyword: str, since: str, until: str, limit: int, mcap_data: dict
) -> tuple[list[dict], dict]:
    """Search EFTS, deduplicate by CIK, and apply the configured universe."""
    import edgar

    c.log(f"Searching EFTS for {keyword!r} ({since} to {until}, limit={limit})...")
    try:
        search = edgar.search_filings(
            keyword,
            start_date=since,
            end_date=until,
            limit=min(limit, 100),
        )
    except Exception as exc:
        raise RuntimeError(f"EFTS search failed: {exc}") from exc

    if search is None:
        raise RuntimeError("EFTS returned no search object")

    server_total = int(getattr(search, "total", 0) or 0)
    fetched = len(list(search))
    if fetched < min(limit, server_total):
        try:
            search = search.fetch_more(min(limit, server_total) - fetched)
        except Exception as exc:
            raise RuntimeError(f"EFTS pagination failed after {fetched} results: {exc}") from exc
    rows = list(search)[:limit]
    fetched = len(rows)
    c.log(f"  Fetched {fetched} of {server_total} matching filing documents")

    companies: dict[str, dict] = {}
    for result in rows:
        cik = str(getattr(result, "cik", "")).lstrip("0")
        if not cik:
            continue
        company_name = str(getattr(result, "company", "Unknown"))
        form = str(getattr(result, "form", ""))
        filed = str(getattr(result, "filed", ""))
        accession = str(getattr(result, "accession_number", "") or "")

        entry = companies.setdefault(
            cik,
            {
                "cik": cik,
                "company_raw": company_name,
                "matching_documents": 0,
                "latest_date": "",
                "latest_form": "",
                "latest_accession": "",
            },
        )
        entry["matching_documents"] += 1
        if filed > entry["latest_date"]:
            entry["latest_date"] = filed
            entry["latest_form"] = form
            entry["latest_accession"] = accession

    total_unique = len(companies)
    c.log(f"  {total_unique} unique CIKs in the fetched result set")

    enriched = []
    unresolved_tickers = 0
    unresolved_market_caps = 0
    outside_universe = 0
    for index, (cik, info) in enumerate(companies.items()):
        if index % 20 == 0:
            c.log(f"  Resolving tickers/market caps: {index}/{total_unique}...")

        ticker = c.extract_ticker(info["company_raw"]) or _resolve_ticker_for_cik(cik)
        if not ticker:
            unresolved_tickers += 1
            continue

        mcap = c.get_market_cap(ticker, mcap_data)
        if mcap is None:
            unresolved_market_caps += 1
            continue
        if not c.in_universe(mcap):
            outside_universe += 1
            continue

        import yfinance as yf

        try:
            yahoo = yf.Ticker(ticker).info or {}
        except Exception:
            yahoo = {}

        accession = info["latest_accession"]
        enriched.append(
            {
                "ticker": ticker,
                "company": yahoo.get("shortName") or yahoo.get("longName") or info["company_raw"],
                "sector": yahoo.get("sector", "n/a"),
                "mcap": mcap,
                "price": yahoo.get("currentPrice") or yahoo.get("regularMarketPrice"),
                "matching_documents": info["matching_documents"],
                "latest_date": info["latest_date"],
                "latest_form": info["latest_form"],
                "latest_accession": accession,
                "source_url": c.sec_filing_url(cik, accession) if accession else "",
            }
        )

    enriched.sort(key=lambda item: item["latest_date"], reverse=True)
    coverage = {
        "server_total": server_total,
        "fetched": fetched,
        "unique_ciks": total_unique,
        "truncated_by_limit": server_total > limit,
        "pagination_incomplete": fetched < min(server_total, limit),
        "unresolved_tickers": unresolved_tickers,
        "unresolved_market_caps": unresolved_market_caps,
        "outside_universe": outside_universe,
    }
    return enriched, coverage


def _render_markdown(
    keyword: str,
    since: str,
    until: str,
    results: list[dict],
    coverage: dict,
) -> str:
    """Render a source-linked theme-search report."""
    lines = [f'# Theme Search: "{keyword}" ({since} to {until})\n']
    lines.append(
        f"EFTS returned **{coverage['fetched']} of {coverage['server_total']}** matching filing "
        f"documents, representing **{coverage['unique_ciks']} unique CIKs** in the fetched set."
    )
    if coverage["truncated_by_limit"]:
        lines.append(
            "\n_Coverage is truncated by `--limit`; issuer counts and rankings are not complete._"
        )
    if coverage["pagination_incomplete"]:
        lines.append(
            "\n_EFTS returned fewer documents than requested; source coverage is incomplete._"
        )
    lines.append(
        f"\nAfter the configured universe filter ({c.universe_label()}): "
        f"**{len(results)} companies**.\n"
    )
    if coverage["unresolved_tickers"] or coverage["unresolved_market_caps"]:
        lines.append(
            f"_Omitted for unresolved current metadata: {coverage['unresolved_tickers']} CIK(s) "
            f"without a ticker and {coverage['unresolved_market_caps']} ticker(s) without a Yahoo "
            "market cap._\n"
        )
    lines.append(
        "A full-text match shows that the filing contains the term; inspect the linked source to "
        "determine context and materiality.\n"
    )

    if not results:
        lines.append("No companies in the configured universe appeared in the fetched matches.\n")
        return "\n".join(lines)

    lines += [
        "| # | Ticker | Company | Sector | Mkt Cap | Price | Matching documents | Latest source |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for index, result in enumerate(results, 1):
        price = result.get("price")
        price_text = f"${price:.2f}" if price is not None else "n/a"
        accession = result["latest_accession"] or "source"
        source = (
            f"[{result['latest_form']} {result['latest_date']} · {accession}]({result['source_url']})"
            if result["source_url"]
            else f"{result['latest_form']} {result['latest_date']}"
        )
        lines.append(
            f"| {index} | {c.md_cell(result['ticker'])} | {c.md_cell(result['company'])} | "
            f"{c.md_cell(result['sector'])} | {c.fmt_mcap(result['mcap'])} | {price_text} | "
            f"{result['matching_documents']} | {source} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Run the theme-search CLI."""
    parser = argparse.ArgumentParser(description="Keyword/theme discovery via SEC EFTS.")
    parser.add_argument("--keyword", required=True, help="Search term.")
    parser.add_argument("--since", required=True, help="Start date YYYY-MM-DD.")
    parser.add_argument("--until", help="End date YYYY-MM-DD (default: today).")
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Maximum matching filing documents before issuer deduplication (default: 200).",
    )
    c.add_identity_arg(parser)
    c.add_cache_arg(parser)
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1.")
    try:
        since = datetime.strptime(args.since, "%Y-%m-%d").date()
        until = (
            datetime.strptime(args.until, "%Y-%m-%d").date()
            if args.until
            else datetime.now().date()
        )
    except ValueError as exc:
        parser.error(str(exc))
    if since > until:
        parser.error("--since must not be later than --until.")

    c.resolve_identity(args.identity)
    cache = c.cache_root(args.cache_dir)
    mcap_data = c.load_mcap_cache(cache)

    try:
        results, coverage = search_and_filter(
            args.keyword,
            since.isoformat(),
            until.isoformat(),
            args.limit,
            mcap_data,
        )
    except RuntimeError as exc:
        c.log(f"ERROR: {exc}")
        sys.exit(1)
    finally:
        c.save_mcap_cache(cache, mcap_data)

    c.log(f"Final: {len(results)} companies in universe")
    markdown = _render_markdown(
        args.keyword,
        since.isoformat(),
        until.isoformat(),
        results,
        coverage,
    )
    slug_keyword = re.sub(r"[^a-zA-Z0-9]+", "-", args.keyword).strip("-").lower() or "search"
    slug = f"{slug_keyword}_{since.isoformat()}_to_{until.isoformat()}"
    c.write_output(cache, "themes", slug, markdown)
    if coverage["pagination_incomplete"]:
        c.log("ERROR: emitted report has incomplete EFTS pagination coverage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
