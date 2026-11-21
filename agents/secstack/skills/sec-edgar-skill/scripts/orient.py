"""Survey a company's identity, filing mix, and recent accessions.

Use this when the relevant form or filing is not yet known. It resolves the
company, prints its compact ``.to_context()`` summary, tabulates forms over a
recent window, and lists recent filings. It does not download filing contents.
"""

import argparse
import datetime as _dt
import sys

import _common as c


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--ticker", required=True, help="Ticker, CIK, or company name.")
    p.add_argument(
        "--years",
        type=int,
        default=3,
        help="Survey the filing mix over the last N calendar years (default: 3).",
    )
    p.add_argument(
        "--recent", type=int, default=15, help="Also list the N most recent filings (default: 15)."
    )
    c.add_identity_arg(p)
    args = p.parse_args()
    if args.years <= 0:
        p.error("--years must be positive")
    if args.recent < 0:
        p.error("--recent cannot be negative")

    c.resolve_identity(args.identity)
    company = c.resolve_company(args.ticker)

    # 1) Cheap metadata summary.
    print(f"# Orientation: {args.ticker.upper()}\n")
    try:
        print(company.to_context())
    except Exception as exc:
        c.log(f"WARNING: .to_context() unavailable ({exc}); printing basic metadata.")
        print(f"COMPANY: {getattr(company, 'name', 'n/a')}")
        print(f"CIK: {getattr(company, 'cik', 'n/a')}")
        print(f"SIC: {getattr(company, 'sic', 'n/a')}")

    # 2) Filing-mix survey over the window.
    this_year = _dt.date.today().year
    start_year = this_year - max(args.years - 1, 0)
    date_range = f"{start_year}-01-01:{this_year}-12-31"
    try:
        df = company.get_filings(date=date_range).to_pandas()
    except Exception as exc:
        c.log(f"ERROR: could not survey filings for {date_range}: {exc}")
        sys.exit(1)

    print(f"\n## Filing mix {start_year}-{this_year}")
    if df is None or len(df) == 0:
        print("- (no filings in this window; widen --years)")
        return

    df = df.copy()
    df["_date"] = df["filing_date"].astype(str)

    rows = []
    for form, grp in df.groupby("form"):
        d = grp["_date"]
        rows.append((str(form), len(grp), d.min(), d.max()))
    rows.sort(key=lambda r: (r[1], r[3]), reverse=True)

    print("\n| Form | Count | Earliest | Latest |")
    print("| :-- | --: | :-- | :-- |")
    for form, n, lo, hi in rows:
        print(f"| {form} | {n} | {lo} | {hi} |")

    # 3) Most recent filings.
    n_recent = min(args.recent, len(df))
    print(f"\n## {n_recent} most recent filings")
    recent = df.sort_values("_date", ascending=False).head(n_recent)
    print("\n| Date | Form | Accession |")
    print("| :-- | :-- | :-- |")
    for _, row in recent.iterrows():
        print(f"| {row['_date']} | {row['form']} | {row.get('accession_number', '')} |")


if __name__ == "__main__":
    main()
