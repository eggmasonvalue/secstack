"""Fetch one SEC filing, section, or attachment as Markdown.

Select either by accession, or by company plus form and optional period. Artifacts
are written to ``<cache>/<TICKER>/<FORM>_<DATE>_<ACCESSION>[__<suffix>].md``;
run with ``--help`` for the complete selector contract.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import _common as c


def _attachment_filename(stem: str, document: str, fallback: str) -> str:
    name = c.safe_component(document or fallback)
    return f"{stem}__{name if name.endswith('.md') else name + '.md'}"


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.accession:
        conflicting = [
            flag
            for flag, value in (
                ("--ticker", args.ticker),
                ("--form", args.form),
                ("--year", args.year),
                ("--quarter", args.quarter),
                ("--on-or-before", args.on_or_before),
            )
            if value is not None
        ]
        if conflicting:
            parser.error(f"--accession cannot be combined with {', '.join(conflicting)}")
    elif not args.ticker or not args.form:
        parser.error("provide --accession, or provide both --ticker and --form")

    if args.attachment and args.section:
        parser.error("--attachment and --section select different document types; choose one")


def _select_by_company(args: argparse.Namespace):
    company = c.resolve_company(args.ticker)
    kwargs: dict[str, object] = {"form": args.form, "amendments": False}
    if args.year is not None:
        kwargs["year"] = args.year
    if args.quarter is not None:
        kwargs["quarter"] = args.quarter

    try:
        filings = list(company.get_filings(**kwargs))
    except Exception as exc:
        c.log(f"ERROR: failed to list {args.form} filings: {exc}")
        sys.exit(1)
    if not filings:
        c.log(
            f"ERROR: no {args.form} filings for {args.ticker} "
            f"(year={args.year}, quarter={args.quarter})."
        )
        sys.exit(1)

    filings.sort(key=lambda filing: filing.filing_date, reverse=True)
    if args.on_or_before:
        try:
            date.fromisoformat(args.on_or_before)
        except ValueError:
            c.log(f"ERROR: --on-or-before must be YYYY-MM-DD, got '{args.on_or_before}'.")
            sys.exit(1)
        filings = [
            filing
            for filing in filings
            if str(getattr(filing, "filing_date", "")) <= args.on_or_before
        ]
        if not filings:
            c.log(
                f"ERROR: no {args.form} filings for {args.ticker} on or before {args.on_or_before}."
            )
            sys.exit(1)
        c.log(
            f"--on-or-before {args.on_or_before}: selected filing dated {filings[0].filing_date}."
        )
    return company, filings[0]


def _cache_hit(path: Path, *, force: bool) -> bool:
    if not force and path.is_file() and path.stat().st_size > 0:
        c.log(f"Using cached artifact: {path.resolve()}")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--accession",
        help="Exact SEC accession. Cannot be combined with company/period selectors.",
    )
    parser.add_argument("--ticker", help="Ticker, CIK, or company name.")
    parser.add_argument("--form", help="Form type, e.g. 10-K, 10-Q, 8-K, 20-F, 40-F, 6-K, DEF 14A.")
    parser.add_argument("--year", type=int, help="Calendar year of the filing.")
    parser.add_argument("--quarter", type=int, choices=[1, 2, 3, 4], help="Calendar quarter.")
    parser.add_argument(
        "--on-or-before",
        help="Select the most recent matching filing on or before YYYY-MM-DD.",
    )
    parser.add_argument(
        "--section",
        help='Extract an SEC item code, or pass "list" to print available item codes.',
    )
    parser.add_argument(
        "--attachment",
        help='Attachment selector: "list", "all", zero-based index, or document/description text.',
    )
    c.add_identity_arg(parser)
    c.add_cache_arg(parser)
    c.add_force_arg(parser)
    args = parser.parse_args()
    _validate_args(parser, args)

    c.resolve_identity(args.identity)
    if args.accession:
        filing = c.resolve_filing(args.accession)
        company = c.company_for_filing(filing)
    else:
        company, filing = _select_by_company(args)

    accession = getattr(filing, "accession_no", "") or getattr(filing, "accession_number", "")
    c.log(f"Resolved {filing.form} filed {filing.filing_date} (accession {accession}).")

    out_dir = c.company_dir(
        c.cache_root(args.cache_dir),
        company,
        ticker_hint=args.ticker if not args.accession else None,
    )
    stem = c.filing_stem(filing)

    if args.attachment:
        attachments = list(filing.attachments)
        if not attachments:
            c.log("ERROR: this filing has no attachments/exhibits.")
            sys.exit(1)

        selector = args.attachment.lower()
        if selector == "list":
            c.log(f"{len(attachments)} attachment(s): index\tdocument\tdescription")
            for index, attachment in enumerate(attachments):
                print(
                    f"{index}\t{getattr(attachment, 'document', '') or ''}"
                    f"\t{getattr(attachment, 'description', '') or ''}"
                )
            return

        if selector == "all":
            saved: list[Path] = []
            for index, attachment in enumerate(attachments):
                filename = _attachment_filename(
                    stem, getattr(attachment, "document", ""), f"attachment_{index}"
                )
                path = out_dir / filename
                if _cache_hit(path, force=args.force):
                    saved.append(path)
                    continue
                try:
                    content = attachment.markdown()
                    if not content:
                        raise ValueError("attachment produced no text")
                    saved.append(c.write_text(path, content))
                    c.log(f"  saved {filename}")
                except Exception as exc:
                    c.log(f"  WARNING: attachment {index} failed: {exc}")
            if not saved:
                c.log("ERROR: no attachments could be converted.")
                sys.exit(1)
            for path in saved:
                c.emit(path)
            return

        selected = None
        if args.attachment.isdigit():
            index = int(args.attachment)
            if not 0 <= index < len(attachments):
                c.log(f"ERROR: attachment index {index} out of range (0-{len(attachments) - 1}).")
                sys.exit(1)
            selected = attachments[index]
        else:
            for attachment in attachments:
                document = (getattr(attachment, "document", "") or "").lower()
                description = (getattr(attachment, "description", "") or "").lower()
                if selector in document or selector in description:
                    selected = attachment
                    break
        if selected is None:
            c.log(f"ERROR: no attachment matched '{args.attachment}'.")
            sys.exit(1)

        filename = _attachment_filename(stem, getattr(selected, "document", ""), "attachment")
        path = out_dir / filename
        if c.emit_cached(path, force=args.force):
            return
        content = selected.markdown()
        if not content:
            c.log("ERROR: selected attachment produced no text.")
            sys.exit(1)
        c.emit(c.write_text(path, content))
        return

    if args.section:
        if args.section.strip().lower() != "list":
            suffix = c.safe_component(args.section).lower()
            path = out_dir / f"{stem}__{suffix}.md"
            if c.emit_cached(path, force=args.force):
                return
        try:
            obj = filing.obj()
        except Exception as exc:
            c.log(f"ERROR: could not parse {filing.form} into an item-addressable object: {exc}")
            sys.exit(1)
        items = list(getattr(obj, "items", None) or [])
        addressable = bool(items) and hasattr(obj, "__getitem__")

        if args.section.strip().lower() == "list":
            if not addressable:
                c.log(
                    f"{filing.form} is not item-addressable. Fetch the full filing and "
                    "navigate its contents or attachments."
                )
                return
            c.log(f"{filing.form} contains {len(items)} item(s):")
            for item in items:
                print(item)
            return

        if not addressable:
            c.log(
                f"ERROR: {filing.form} is not item-addressable. Fetch the full filing or "
                "an attachment instead."
            )
            sys.exit(1)
        content = obj[args.section]
        if content is None or not str(content).strip():
            c.log(f"ERROR: item '{args.section}' is absent. Available items: {', '.join(items)}")
            sys.exit(1)
        c.emit(c.write_text(path, str(content)))
        return

    path = out_dir / f"{stem}.md"
    if c.emit_cached(path, force=args.force):
        return
    content = filing.markdown()
    if not content:
        c.log("ERROR: filing produced no Markdown; it may be exhibit-only. Try --attachment list.")
        sys.exit(1)
    c.emit(c.write_text(path, content))


if __name__ == "__main__":
    main()
