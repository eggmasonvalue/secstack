"""Bulk-fetch SEC filings and attachments across a filing-date range.

Bulk retrieval intentionally includes both original filings and amendments. Each
saved or reused artifact is emitted as an absolute path; run with ``--help`` for
all selectors.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _common as c

_BINARY = (".jpg", ".jpeg", ".png", ".gif", ".zip", ".pdf", ".xlsx", ".xls")


def _cached(path: Path, *, force: bool) -> bool:
    return not force and path.is_file() and path.stat().st_size > 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ticker", required=True, help="Ticker, CIK, or company name.")
    parser.add_argument("--form", required=True, help="Form type, e.g. 10-Q, 8-K, 6-K.")
    parser.add_argument("--start-year", type=int, help="First calendar year (inclusive).")
    parser.add_argument("--end-year", type=int, help="Last calendar year (inclusive).")
    parser.add_argument(
        "--attachments", action="store_true", help="Also save each filing's text attachments."
    )
    c.add_identity_arg(parser)
    c.add_cache_arg(parser)
    c.add_force_arg(parser)
    args = parser.parse_args()

    if args.start_year and args.end_year and args.start_year > args.end_year:
        parser.error("--start-year cannot be later than --end-year")

    c.resolve_identity(args.identity)
    company = c.resolve_company(args.ticker)

    # A bulk archive should preserve the full record: original and amended forms.
    kwargs: dict[str, object] = {"form": args.form, "amendments": True}
    if args.start_year or args.end_year:
        start = f"{args.start_year}-01-01" if args.start_year else "1994-01-01"
        end = f"{args.end_year}-12-31" if args.end_year else "2100-12-31"
        kwargs["date"] = f"{start}:{end}"
    try:
        filings = list(company.get_filings(**kwargs))
    except Exception as exc:
        c.log(f"ERROR: failed to list {args.form} filings: {exc}")
        sys.exit(1)
    if not filings:
        c.log("ERROR: no filings matched the requested form and date range.")
        sys.exit(1)

    out_dir = c.company_dir(c.cache_root(args.cache_dir), company, ticker_hint=args.ticker)
    c.log(
        f"Found {len(filings)} {args.form} filing(s), including amendments when present, "
        f"-> {out_dir}"
    )

    saved: list[Path] = []
    failures = 0
    for index, filing in enumerate(filings, 1):
        stem = c.filing_stem(filing)
        c.log(f"[{index}/{len(filings)}] {filing.form} {filing.filing_date}")
        body_path = out_dir / f"{stem}.md"
        if _cached(body_path, force=args.force):
            c.log(f"  using cached {body_path.name}")
            saved.append(body_path)
        else:
            try:
                content = filing.markdown()
                if content:
                    saved.append(c.write_text(body_path, content))
                else:
                    c.log("  empty body — likely exhibit-only; use --attachments")
            except Exception as exc:
                failures += 1
                c.log(f"  WARNING: main body failed: {exc}")

        if not args.attachments:
            continue
        try:
            attachments = list(filing.attachments)
        except Exception as exc:
            failures += 1
            c.log(f"  WARNING: could not list attachments: {exc}")
            continue

        for attachment_index, attachment in enumerate(attachments):
            document = getattr(attachment, "document", "") or f"attachment_{attachment_index}"
            if document.lower().endswith(_BINARY):
                continue
            name = c.safe_component(document)
            name = name if name.endswith(".md") else name + ".md"
            attachment_path = out_dir / f"{stem}__{name}"
            if _cached(attachment_path, force=args.force):
                c.log(f"  using cached {attachment_path.name}")
                saved.append(attachment_path)
                continue
            try:
                content = attachment.markdown()
                if not content:
                    raise ValueError("attachment produced no text")
                saved.append(c.write_text(attachment_path, content))
            except Exception as exc:
                failures += 1
                c.log(f"  WARNING: attachment {attachment_index} ({document}) failed: {exc}")

    if not saved:
        c.log("ERROR: no filing bodies or attachments could be saved.")
        sys.exit(1)
    if failures:
        c.log(f"WARNING: completed with {failures} failed conversion(s).")
    for path in dict.fromkeys(saved):
        c.emit(path)


if __name__ == "__main__":
    main()
