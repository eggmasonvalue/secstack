import type {
  ExtensionAPI,
  Theme,
} from "@earendil-works/pi-coding-agent";
import { truncateToWidth } from "@earendil-works/pi-tui";

const WIDE_HEADER_WIDTH = 42;
const COMPACT_HEADER_WIDTH = 34;

function fit(lines: string[], width: number): string[] {
  return lines.map((line) => truncateToWidth(line, width, ""));
}

function renderWide(theme: Theme, width: number, expanded: boolean): string[] {
  const g = (text: string) => theme.fg("success", text);
  const gold = (text: string) => theme.fg("warning", text);
  const mark = (text: string) => theme.fg("accent", text);
  const ink = (text: string) => theme.bold(theme.fg("text", text));
  const tree = (text: string) => theme.fg("dim", text);
  const copy = (text: string) => theme.fg("muted", text);

  const corner = `${g("[")}${gold("$")}${g("]")}`;
  const billTop = `${g("╔═")}${corner}${g("════════════════")}${corner}${g("═╗")}`;
  const billMid = `${g("║")}        ${ink("SECSTACK")}        ${g("║")}`;
  const billBot = `${g("╚═")}${corner}${g("════════════════")}${corner}${g("═╝")}`;

  const lines = [
    "",
    `      ${mark("▄█▄")}`,
    `    ${mark("┌─────┐")}    ${billTop}`,
    `    ${mark("│ ")}${gold("█ █")}${mark(" │")}    ${billMid}`,
    `   ${mark("┌┴─────┴┐")}   ${billBot}`,
    `  ${mark("▀▀▀▀▀▀▀▀▀▀▀")}`,
  ];

  if (expanded) {
    if (width >= 62) {
      lines.push(
        "",
        `  ${tree("Research Pipeline:")}`,
        `  ${tree("├─ ")}${theme.fg("mdCode", "[EDGAR]")}       ${copy("10-K · 10-Q · 8-K · XBRL statements · Proxies")}`,
        `  ${tree("├─ ")}${gold("[SIGNALS]")}     ${copy("Form 4 insider buys · Schedule 13D blockholders")}`,
        `  ${tree("├─ ")}${mark("[MARKET]")}      ${copy("Live quotes · Comps · Earnings call transcripts")}`,
        `  ${tree("├─ ")}${theme.fg("mdHeading", "[ANALYSIS]")}    ${copy("Forensic MD&A · Unit economics · Margin of safety")}`,
        `  ${tree("└─ ")}${theme.fg("syntaxType", "[VIC PITCH]")}   ${copy("Norbert Lou numbers-first stock pitch")}`,
      );
    } else {
      lines.push(
        "",
        `  ${tree("Research Pipeline:")}`,
        `  ${tree("├─ ")}${theme.fg("mdCode", "[EDGAR]")}     ${copy("10-K · 10-Q · 8-K · Proxies")}`,
        `  ${tree("├─ ")}${gold("[SIGNALS]")}   ${copy("Form 4 insider buys · 13D")}`,
        `  ${tree("├─ ")}${mark("[MARKET]")}    ${copy("Quotes · Comps · Transcripts")}`,
        `  ${tree("├─ ")}${theme.fg("mdHeading", "[ANALYSIS]")}  ${copy("Forensic MD&A · Valuation")}`,
        `  ${tree("└─ ")}${theme.fg("syntaxType", "[VIC PITCH]")} ${copy("Norbert Lou VIC pitch")}`,
      );
    }
  }

  lines.push("");
  return fit(lines, width);
}

function renderCompact(theme: Theme, width: number, expanded: boolean): string[] {
  const g = (text: string) => theme.fg("success", text);
  const gold = (text: string) => theme.fg("warning", text);
  const mark = (text: string) => theme.fg("accent", text);
  const ink = (text: string) => theme.bold(theme.fg("text", text));
  const tree = (text: string) => theme.fg("dim", text);
  const copy = (text: string) => theme.fg("muted", text);

  const corner = `${g("[")}${gold("$")}${g("]")}`;
  const billTop = `${g("╔")}${corner}${g("═══════════")}${corner}${g("╗")}`;
  const billMid = `${g("║")}    ${ink("SECSTACK")}    ${g("║")}`;
  const billBot = `${g("╚")}${corner}${g("═══════════")}${corner}${g("╝")}`;

  const lines = [
    "",
    `      ${mark("▄█▄")}`,
    `    ${mark("┌─────┐")}   ${billTop}`,
    `    ${mark("│ ")}${gold("█ █")}${mark(" │")}   ${billMid}`,
    `   ${mark("┌┴─────┴┐")}  ${billBot}`,
    `  ${mark("▀▀▀▀▀▀▀▀▀▀▀")}`,
  ];

  if (expanded) {
    lines.push(
      "",
      `  ${tree("Research Pipeline:")}`,
      `  ${tree("├─ ")}${theme.fg("mdCode", "[EDGAR]")}     ${copy("10-K/Q/8-K · Proxies")}`,
      `  ${tree("├─ ")}${gold("[SIGNALS]")}   ${copy("Form 4 · 13D")}`,
      `  ${tree("├─ ")}${mark("[MARKET]")}    ${copy("Quotes · Calls")}`,
      `  ${tree("├─ ")}${theme.fg("mdHeading", "[ANALYSIS]")}  ${copy("MD&A · DCF")}`,
      `  ${tree("└─ ")}${theme.fg("syntaxType", "[VIC PITCH]")} ${copy("Norbert Lou pitch")}`,
    );
  }

  lines.push("");
  return fit(lines, width);
}

function renderNarrow(theme: Theme, width: number, expanded: boolean): string[] {
  const g = (text: string) => theme.fg("success", text);
  const gold = (text: string) => theme.fg("warning", text);
  const ink = (text: string) => theme.bold(theme.fg("text", text));
  const copy = (text: string) => theme.fg("muted", text);
  const tree = (text: string) => theme.fg("dim", text);

  const corner = `${g("[")}${gold("$")}${g("]")}`;
  const lines = [
    "",
    `${corner} ${ink("SECSTACK")} ${corner}`,
    copy("Bottom-Up Equity Research"),
  ];

  if (expanded) {
    lines.push(
      "",
      tree("• EDGAR Filings (10-K/Q/8-K)"),
      tree("• Signals (Form 4/13D)"),
      tree("• Market & Transcripts"),
      tree("• Analysis & Valuation"),
      tree("• Norbert Lou VIC Pitch"),
    );
  }

  lines.push("");
  return fit(lines, width);
}

export function renderStartupHeader(
  theme: Theme,
  width: number,
  expanded: boolean = false,
): string[] {
  if (width >= WIDE_HEADER_WIDTH) return renderWide(theme, width, expanded);
  if (width >= COMPACT_HEADER_WIDTH) return renderCompact(theme, width, expanded);
  return renderNarrow(theme, width, expanded);
}

export default function startupHeaderExtension(pi: ExtensionAPI) {
  pi.on("session_start", (_event, ctx) => {
    if (ctx.mode !== "tui") return;

    let expanded = false;

    ctx.ui.setHeader((tui, theme) => ({
      render: (width) => renderStartupHeader(theme, width, expanded),
      invalidate() {},
      setExpanded(value: boolean) {
        if (expanded === value) return;
        expanded = value;
        tui.requestRender();
      },
    }));
  });

  pi.on("session_shutdown", (_event, ctx) => {
    if (ctx.mode !== "tui") return;
    ctx.ui.setHeader(undefined);
  });
}
