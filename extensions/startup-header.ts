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

function renderWide(theme: Theme, width: number, showPipeline: boolean): string[] {
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

  if (showPipeline) {
    if (width >= 77) {
      lines.push(
        "",
        `  ${tree("Research Pipeline:")}`,
        `  ${tree("├─ ")}${gold("[SIGNALS]")}     ${copy("Insider clusters · 13D blocks · Market screens · Themes")}`,
        `  ${tree("├─ ")}${theme.fg("mdCode", "[EDGAR]")}       ${copy("10-K/Q/8-K · XBRL financials · 13F holders · Proxies")}`,
        `  ${tree("├─ ")}${mark("[MARKET]")}      ${copy("Live quotes · Peer comps · Trailing returns · Transcripts")}`,
        `  ${tree("├─ ")}${theme.fg("mdHeading", "[ANALYSIS]")}    ${copy("Normalized FCFF · Reverse DCF / EPV · Moats · Pre-mortem")}`,
        `  ${tree("└─ ")}${theme.fg("syntaxType", "[VIC PITCH]")}   ${copy("Norbert Lou VIC style · Hard arithmetic · Falsification")}`,
      );
    } else {
      lines.push(
        "",
        `  ${tree("Research Pipeline:")}`,
        `  ${tree("├─ ")}${gold("[SIGNALS]")}   ${copy("Insider clusters · 13Ds · Screens")}`,
        `  ${tree("├─ ")}${theme.fg("mdCode", "[EDGAR]")}     ${copy("10-K/Q/8-K · XBRL · 13F holders")}`,
        `  ${tree("├─ ")}${mark("[MARKET]")}    ${copy("Quotes · Peer comps · Transcripts")}`,
        `  ${tree("├─ ")}${theme.fg("mdHeading", "[ANALYSIS]")}  ${copy("Normalized FCFF · DCF · Pre-mortem")}`,
        `  ${tree("└─ ")}${theme.fg("syntaxType", "[VIC PITCH]")} ${copy("Norbert Lou VIC pitch · Math")}`,
      );
    }
  }

  lines.push("");
  return fit(lines, width);
}

function renderCompact(theme: Theme, width: number, showPipeline: boolean): string[] {
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

  if (showPipeline) {
    lines.push(
      "",
      `  ${tree("Research Pipeline:")}`,
      `  ${tree("├─ ")}${gold("[SIGNALS]")}   ${copy("Insiders · 13Ds · Screens")}`,
      `  ${tree("├─ ")}${theme.fg("mdCode", "[EDGAR]")}     ${copy("10-K/Q · XBRL · 13F")}`,
      `  ${tree("├─ ")}${mark("[MARKET]")}    ${copy("Quotes · Comps · Calls")}`,
      `  ${tree("├─ ")}${theme.fg("mdHeading", "[ANALYSIS]")}  ${copy("FCFF · DCF · Moats")}`,
      `  ${tree("└─ ")}${theme.fg("syntaxType", "[VIC PITCH]")} ${copy("Norbert Lou pitch")}`,
    );
  }

  lines.push("");
  return fit(lines, width);
}

function renderNarrow(theme: Theme, width: number, showPipeline: boolean): string[] {
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

  if (showPipeline) {
    lines.push(
      "",
      tree("• Signals & Discovery"),
      tree("• EDGAR Filings & 13F"),
      tree("• Market & Transcripts"),
      tree("• Bottom-Up Valuation"),
      tree("• Norbert Lou VIC Pitch"),
    );
  }

  lines.push("");
  return fit(lines, width);
}

export function renderStartupHeader(
  theme: Theme,
  width: number,
  showPipeline: boolean = true,
): string[] {
  if (width >= WIDE_HEADER_WIDTH) return renderWide(theme, width, showPipeline);
  if (width >= COMPACT_HEADER_WIDTH) return renderCompact(theme, width, showPipeline);
  return renderNarrow(theme, width, showPipeline);
}

export default function startupHeaderExtension(pi: ExtensionAPI) {
  pi.on("session_start", (_event, ctx) => {
    if (ctx.mode !== "tui") return;

    let showPipeline = true;

    ctx.ui.setHeader((tui, theme) => ({
      render: (width) => renderStartupHeader(theme, width, showPipeline),
      invalidate() {},
      setExpanded(toolsExpanded: boolean) {
        // Invert: when tools are expanded for deeper inspection, collapse the
        // header to yield vertical screen space. When tools are collapsed,
        // show the full research capability pipeline.
        const next = !toolsExpanded;
        if (showPipeline === next) return;
        showPipeline = next;
        tui.requestRender();
      },
    }));
  });

  pi.on("session_shutdown", (_event, ctx) => {
    if (ctx.mode !== "tui") return;
    ctx.ui.setHeader(undefined);
  });
}
