"""Run config-driven Yahoo Finance equity screens.

Definitions and universe bounds come from ``screens.json``. Each successful run
writes a Markdown report and emits its absolute path.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c


def _load_screens(path: Path) -> dict:
    """Load and parse a screen configuration."""
    if not path.exists():
        c.log(f"ERROR: screens file not found: {path}")
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        c.log(f"ERROR: invalid screens file {path}: {exc}")
        sys.exit(1)


def _build_query(screen: dict, universe: dict):
    """Build a yfinance EquityQuery from one definition and its universe."""
    import yfinance as yf

    conditions = [
        yf.EquityQuery("eq", ["region", universe.get("region", "us")]),
        yf.EquityQuery("gte", ["intradaymarketcap", universe.get("market_cap_min", 50_000_000)]),
        yf.EquityQuery(
            "lte", ["intradaymarketcap", universe.get("market_cap_max", 10_000_000_000)]
        ),
    ]
    for filter_ in screen.get("filters", []):
        value = filter_["value"]
        operands = (
            [filter_["field"], *value] if isinstance(value, list) else [filter_["field"], value]
        )
        conditions.append(yf.EquityQuery(filter_["op"], operands))
    return yf.EquityQuery("and", conditions)


def _enrich(quotes: list[dict], size: int) -> list[dict]:
    """Add report columns from Yahoo's per-ticker snapshot."""
    import yfinance as yf

    enriched = []
    for index, quote in enumerate(quotes[:size]):
        symbol = quote.get("symbol", "")
        c.log(f"  Enriching {index + 1}/{min(size, len(quotes))}: {symbol}")
        try:
            info = yf.Ticker(symbol).info or {}
        except Exception:
            info = {}

        quote["analyst_rating"] = info.get("averageAnalystRating", "n/a")
        quote["short_pct"] = info.get("shortPercentOfFloat")
        quote["insider_pct"] = info.get("heldPercentInsiders")
        quote["inst_pct"] = info.get("heldPercentInstitutions")
        quote["sector"] = info.get("sector", quote.get("sector", ""))
        quote["pe"] = info.get("trailingPE") or info.get("forwardPE")
        quote["current_price"] = info.get("currentPrice", quote.get("regularMarketPrice"))
        quote["market_cap"] = info.get("marketCap", quote.get("marketCap"))
        enriched.append(quote)
    return enriched


def _fmt_pct(value, *, decimal: bool = False) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100 if decimal else value:.1f}%"


def _fmt_num(value) -> str:
    return "n/a" if value is None else f"{value:.1f}"


def _render_markdown(
    screen: dict,
    quotes: list[dict],
    *,
    enriched: bool,
    universe: dict,
    total: int | str,
) -> str:
    """Render screen results as a Markdown table."""
    emoji = screen.get("emoji", "📊")
    name = screen.get("name", screen.get("id", "Screen"))
    lines = [f"# {emoji} Screen: {name} ({c.universe_label(universe)})\n"]
    if screen.get("description"):
        lines.append(f"_{screen['description']}_\n")
    lines.append(f"**Results returned:** {len(quotes)} of {total} matching\n")

    if not quotes:
        lines.append("No results matched this screen.\n")
        return "\n".join(lines)

    if enriched:
        lines += [
            "| # | Ticker | Company | Price | Mkt Cap | P/E | Short % | Insider % | Inst % | Analyst | Sector |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
        for index, quote in enumerate(quotes, 1):
            price = quote.get("current_price")
            lines.append(
                f"| {index} | {c.md_cell(quote.get('symbol', '?'))} | "
                f"{c.md_cell(quote.get('shortName') or quote.get('longName') or '?')} | "
                f"{f'${price:.2f}' if price is not None else 'n/a'} | "
                f"{c.fmt_mcap(quote.get('market_cap'))} | {_fmt_num(quote.get('pe'))} | "
                f"{_fmt_pct(quote.get('short_pct'), decimal=True)} | "
                f"{_fmt_pct(quote.get('insider_pct'), decimal=True)} | "
                f"{_fmt_pct(quote.get('inst_pct'), decimal=True)} | "
                f"{c.md_cell(quote.get('analyst_rating', 'n/a'))} | "
                f"{c.md_cell(quote.get('sector') or 'n/a')} |"
            )
    else:
        lines += [
            "| # | Ticker | Company | Price | Mkt Cap |",
            "|---|---|---|---:|---:|",
        ]
        for index, quote in enumerate(quotes, 1):
            price = quote.get("regularMarketPrice")
            lines.append(
                f"| {index} | {c.md_cell(quote.get('symbol', '?'))} | "
                f"{c.md_cell(quote.get('shortName') or quote.get('longName') or '?')} | "
                f"{f'${price:.2f}' if price is not None else 'n/a'} | "
                f"{c.fmt_mcap(quote.get('marketCap'))} |"
            )
    lines.append("")
    return "\n".join(lines)


def run_screen(
    screen: dict,
    universe: dict,
    size: int | None,
    do_enrich: bool,
) -> tuple[str, bool]:
    """Run one screen and return its report plus a success flag."""
    import yfinance as yf

    screen_id = screen.get("id", "unknown")
    screen_size = size if size is not None else screen.get("size", 25)
    c.log(f"Running screen: {screen_id} (size={screen_size})...")

    try:
        query = _build_query(screen, universe)
        kwargs = {"query": query, "size": screen_size}
        sort = screen.get("sort", {})
        if sort.get("field"):
            kwargs["sortField"] = sort["field"]
            kwargs["sortAsc"] = sort.get("asc", True)
        result = yf.screen(**kwargs)
    except Exception as exc:
        c.log(f"  ERROR: screen failed: {exc}")
        return f"# Screen: {screen_id}\n\nRetrieval failed: {exc}\n", False

    quotes = result.get("quotes", [])
    c.log(f"  Got {len(quotes)} results (total matching: {result.get('total', '?')})")
    should_enrich = do_enrich and screen.get("enrich", True)
    if should_enrich and quotes:
        quotes = _enrich(quotes, screen_size)
    return (
        _render_markdown(
            screen,
            quotes,
            enriched=should_enrich,
            universe=universe,
            total=result.get("total", "unknown"),
        ),
        True,
    )


def main() -> None:
    """Run the market-screen CLI."""
    parser = argparse.ArgumentParser(description="Config-driven market screens.")
    parser.add_argument("--screen", help="Screen ID from screens.json.")
    parser.add_argument("--all", action="store_true", help="Run all screens.")
    parser.add_argument("--list", action="store_true", help="List available screen IDs.")
    parser.add_argument("--size", type=int, help="Override the screen's result size.")
    parser.add_argument("--no-enrich", action="store_true", help="Skip enrichment.")
    parser.add_argument("--screens-file", help="Alternate screens.json path.")
    c.add_cache_arg(parser)
    args = parser.parse_args()

    if args.size is not None and args.size < 1:
        parser.error("--size must be at least 1.")

    screens_path = (
        Path(args.screens_file).resolve()
        if args.screens_file
        else Path(__file__).resolve().parent.parent / "screens.json"
    )
    config = _load_screens(screens_path)
    universe = config.get("universe", {})
    screens = config.get("screens", [])

    if args.list:
        print("Available screens:\n")
        for screen in screens:
            print(
                f"  {screen.get('emoji', '📊')} {screen['id']:25s} "
                f"{screen.get('name', '')} — {screen.get('description', '')}"
            )
        return
    if not args.screen and not args.all:
        parser.error("Specify --screen <id>, --all, or --list.")

    selected = screens if args.all else [next((s for s in screens if s["id"] == args.screen), None)]
    if selected == [None]:
        available = ", ".join(screen["id"] for screen in screens)
        c.log(f"ERROR: unknown screen {args.screen!r}. Available: {available}")
        sys.exit(1)

    reports = []
    failures = 0
    for screen in selected:
        report, ok = run_screen(screen, universe, args.size, not args.no_enrich)
        reports.append(report)
        failures += int(not ok)

    today = datetime.now().strftime("%Y-%m-%d")
    slug = f"all-screens_{today}" if args.all else f"{args.screen}_{today}"
    c.write_output(
        c.cache_root(args.cache_dir),
        "screens",
        slug,
        "\n---\n\n".join(reports),
    )
    if failures:
        c.log(f"ERROR: {failures} screen(s) failed; emitted report is incomplete.")
        sys.exit(1)


if __name__ == "__main__":
    main()
