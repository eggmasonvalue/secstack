"""Extract XBRL financial statements from one exact SEC report to CSV.

Select by accession, or by company and filing period. Period selection is strict:
the command never substitutes a more recent report. Ambiguous financial 6-Ks are
listed with their accessions so the caller can select one exactly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _common as c

STATEMENTS = {
    "income": ("income_statement", "income"),
    "balance": ("balance_sheet", "balance"),
    "cashflow": ("cashflow_statement", "cashflow"),
}

_FINANCIAL_TERMS = (
    "financial statement",
    "financial results",
    "interim results",
    "quarterly results",
    "half-year",
    "half year",
    "six month",
    "nine month",
    "earnings release",
    "operating and financial review",
)


def _accession(filing) -> str:
    return str(getattr(filing, "accession_no", "") or getattr(filing, "accession_number", ""))


def _available_statements(xbrl) -> list[str]:
    available = []
    for key, (accessor, _) in STATEMENTS.items():
        method = getattr(xbrl.statements, accessor, None)
        if method is None:
            continue
        try:
            if method():
                available.append(key)
        except Exception:
            continue
    return available


def _xbrl_period(xbrl) -> str:
    info = getattr(xbrl, "entity_info", None) or {}
    fiscal_period = info.get("fiscal_period")
    fiscal_year = info.get("fiscal_year")
    period_end = getattr(xbrl, "period_of_report", None) or info.get("document_period_end_date")
    label = " ".join(str(value) for value in (fiscal_period, fiscal_year) if value)
    if period_end:
        return f"XBRL period {label + ' ' if label else ''}ending {period_end}".strip()
    return f"XBRL period {label}".strip() if label else ""


def _financial_evidence(filing) -> list[str]:
    evidence = []
    if getattr(filing, "is_xbrl", False) or getattr(filing, "is_inline_xbrl", False):
        evidence.append("XBRL metadata")
    try:
        for attachment in list(filing.attachments):
            document = str(getattr(attachment, "document", "") or "")
            description = str(getattr(attachment, "description", "") or "")
            text = f"{document} {description}".lower()
            matched = next((term for term in _FINANCIAL_TERMS if term in text), None)
            if matched:
                evidence.append(description or document or matched)
            if "101.ins" in text or "inline xbrl" in text:
                evidence.append("Inline XBRL attachment")
    except Exception:
        pass
    return list(dict.fromkeys(evidence))


def _log_candidates(title: str, rows: list[tuple[object, list[str], list[str]]]) -> None:
    c.log(title)
    c.log("Filed      Form     Accession                  Statements       Evidence")
    for filing, statements, evidence in rows:
        c.log(
            f"{getattr(filing, 'filing_date', '')!s:<10} "
            f"{getattr(filing, 'form', '')!s:<8} "
            f"{_accession(filing):<26} "
            f"{','.join(statements) or '-':<16} "
            f"{'; '.join(evidence) or '-'}"
        )


def _nearby_filings(company, forms: list[str]) -> None:
    try:
        nearby = list(company.get_filings(form=forms, amendments=False))[:5]
    except Exception:
        return
    if not nearby:
        return
    c.log("Nearby original filings:")
    for filing in nearby:
        c.log(f"  {filing.filing_date}  {filing.form:<8}  {_accession(filing)}")


def _select_company_filing(args: argparse.Namespace, company):
    six_k_mode = False
    if args.form:
        forms = [args.form]
        six_k_mode = args.form.upper() in {"6-K", "6-K/A"}
        amendments = six_k_mode
        filings = list(
            company.get_filings(
                form=forms,
                year=args.year,
                quarter=args.quarter,
                amendments=amendments,
            )
        )
    elif args.quarter:
        forms = ["10-Q"]
        filings = list(
            company.get_filings(
                form=forms,
                year=args.year,
                quarter=args.quarter,
                amendments=False,
            )
        )
        if not filings:
            forms = ["6-K"]
            six_k_mode = True
            filings = list(
                company.get_filings(
                    form=forms,
                    year=args.year,
                    quarter=args.quarter,
                    amendments=True,
                )
            )
    else:
        forms = ["10-K", "20-F", "40-F"]
        filings = list(company.get_filings(form=forms, year=args.year, amendments=False))

    if not filings:
        c.log(
            f"ERROR: no {'/'.join(forms)} filing found in filing year {args.year}"
            + (f" Q{args.quarter}" if args.quarter else "")
            + "."
        )
        _nearby_filings(company, forms)
        sys.exit(1)

    parsed: list[tuple[object, object, list[str], list[str]]] = []
    likely_textual = []
    for filing in sorted(filings, key=lambda item: item.filing_date, reverse=True):
        evidence = _financial_evidence(filing) if six_k_mode else []
        try:
            xbrl = filing.xbrl()
            statements = _available_statements(xbrl) if xbrl else []
        except Exception:
            xbrl = None
            statements = []
        if xbrl and statements:
            period = _xbrl_period(xbrl)
            if period:
                evidence.append(period)
            parsed.append((filing, xbrl, statements, evidence))
        elif evidence:
            likely_textual.append((filing, statements, evidence))

    if len(parsed) == 1:
        filing, xbrl, statements, _ = parsed[0]
        period = _xbrl_period(xbrl)
        c.log(
            f"Structured statements available: {', '.join(statements)}"
            + (f"; {period}." if period else ".")
        )
        return filing, xbrl

    if len(parsed) > 1:
        _log_candidates(
            "ERROR: multiple filings contain structured statements; rerun with --accession.",
            [(filing, statements, evidence) for filing, _, statements, evidence in parsed],
        )
        sys.exit(1)

    if six_k_mode and likely_textual:
        _log_candidates(
            "ERROR: no parseable XBRL statements found. These 6-Ks may contain textual "
            "financial disclosures; fetch the relevant accession and inspect its attachments.",
            likely_textual,
        )
    else:
        _log_candidates(
            "ERROR: matching filing(s) were found, but none produced structured statements.",
            [(filing, [], _financial_evidence(filing)) for filing in filings],
        )
    sys.exit(1)


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.accession:
        conflicting = [
            flag
            for flag, value in (
                ("--ticker", args.ticker),
                ("--year", args.year),
                ("--quarter", args.quarter),
                ("--form", args.form),
            )
            if value is not None
        ]
        if conflicting:
            parser.error(f"--accession cannot be combined with {', '.join(conflicting)}")
    elif not args.ticker or args.year is None:
        parser.error("provide --accession, or provide both --ticker and --year")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--accession",
        help="Exact SEC accession. Cannot be combined with company/period selectors.",
    )
    parser.add_argument("--ticker", help="Ticker, CIK, or company name.")
    parser.add_argument("--year", type=int, help="Calendar filing year.")
    parser.add_argument(
        "--quarter", type=int, choices=[1, 2, 3, 4], help="Calendar filing quarter."
    )
    parser.add_argument(
        "--form",
        help="Form type. By default, infer annual forms or prefer 10-Q before scanning 6-K.",
    )
    parser.add_argument(
        "--statement",
        choices=["income", "balance", "cashflow", "all"],
        default="all",
        help="Statement(s) to extract (default: all).",
    )
    c.add_identity_arg(parser)
    c.add_cache_arg(parser)
    c.add_force_arg(parser)
    args = parser.parse_args()
    _validate_args(parser, args)

    c.resolve_identity(args.identity)
    wanted = ["income", "balance", "cashflow"] if args.statement == "all" else [args.statement]

    if args.accession:
        filing = c.resolve_filing(args.accession)
        company = c.company_for_filing(filing)
        xbrl = None
    else:
        company = c.resolve_company(args.ticker)
        try:
            filing, xbrl = _select_company_filing(args, company)
        except Exception as exc:
            c.log(f"ERROR: could not select a financial filing: {exc}")
            sys.exit(1)

    out_dir = c.company_dir(
        c.cache_root(args.cache_dir),
        company,
        ticker_hint=args.ticker if not args.accession else None,
    )
    stem = c.filing_stem(filing)
    paths = {key: out_dir / f"{stem}__{STATEMENTS[key][1]}.csv" for key in wanted}

    if not args.force and all(
        path.is_file() and path.stat().st_size > 0 for path in paths.values()
    ):
        for path in paths.values():
            c.log(f"Using cached artifact: {path.resolve()}")
            c.emit(path)
        return

    if xbrl is None:
        try:
            xbrl = filing.xbrl()
        except Exception as exc:
            c.log(f"ERROR: accession {_accession(filing)} could not be parsed as XBRL: {exc}")
            sys.exit(1)
    if not xbrl:
        c.log(f"ERROR: accession {_accession(filing)} contains no parsed XBRL data.")
        sys.exit(1)

    c.log(f"Resolved {filing.form} filed {filing.filing_date} (accession {_accession(filing)}).")
    saved: list[Path] = []
    missing = []
    for key in wanted:
        path = paths[key]
        if not args.force and path.is_file() and path.stat().st_size > 0:
            c.log(f"Using cached artifact: {path.resolve()}")
            saved.append(path)
            continue
        accessor, _ = STATEMENTS[key]
        method = getattr(xbrl.statements, accessor, None)
        if method is None:
            missing.append(key)
            continue
        try:
            statement = method()
            if not statement:
                missing.append(key)
                continue
            dataframe = statement.to_dataframe()
            dataframe.to_csv(path, index=True)
            saved.append(path)
            c.log(f"  saved {path.name} ({len(dataframe)} rows)")
        except Exception as exc:
            c.log(f"WARNING: {accessor} failed: {exc}")
            missing.append(key)

    if missing:
        c.log(f"WARNING: unavailable statement(s): {', '.join(missing)}.")
    if not saved or (args.statement != "all" and missing):
        c.log("ERROR: the requested statement could not be extracted.")
        sys.exit(1)
    for path in saved:
        c.emit(path)


if __name__ == "__main__":
    main()
