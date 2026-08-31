import type {
  ExtensionAPI,
  Theme,
} from "@earendil-works/pi-coding-agent";
import { truncateToWidth } from "@earendil-works/pi-tui";

const WIDE_HEADER_WIDTH = 50;
const COMPACT_HEADER_WIDTH = 38;

function fit(lines: string[], width: number): string[] {
  return lines.map((line) => truncateToWidth(line, width, ""));
}

function renderWide(theme: Theme, width: number): string[] {
  const border = (text: string) => theme.fg("borderMuted", text);
  const ink = (text: string) => theme.fg("text", text);
  const copy = (text: string) => theme.fg("muted", text);
  const mark = (text: string) => theme.fg("accent", text);

  return fit(
    [
      "",
      border("┌─────────────────────┐"),
      `${border("│")} ${ink(theme.bold("FORM 10-K · ITEM 7"))} ${border("◢│")}`,
      `${border("│")} ${copy("━━━━━━━━━━━━━━━    ")} ${border("│")}  ${mark("┏")}`,
      `${border("│")} ${copy("━━━━━━━━━━         ")} ${border("│")}  ${mark("┃")}     ${ink(theme.bold("S E C S T A C K"))}`,
      `${border("│")} ${mark("███████████████")}     ${border("│")}${mark("━━┫━━")}  ${mark(theme.bold("EVIDENCE → JUDGMENT"))}`,
      `${border("│")} ${copy("━━━━━━━━━━━━━━━━   ")} ${border("│")}  ${mark("┃")}`,
      `${border("│")} ${copy("━━━━━━━━━━━        ")} ${border("│")}  ${mark("┗")}`,
      border("└─────────────────────┘"),
      "",
    ],
    Math.min(width, WIDE_HEADER_WIDTH),
  );
}

function renderCompact(theme: Theme, width: number): string[] {
  const border = (text: string) => theme.fg("borderMuted", text);
  const ink = (text: string) => theme.fg("text", text);
  const copy = (text: string) => theme.fg("muted", text);
  const mark = (text: string) => theme.fg("accent", text);

  return fit(
    [
      "",
      `${border("┌───────────────┐")}  ${ink(theme.bold("SECSTACK"))}`,
      `${border("│")} ${ink(theme.bold("10-K · ITEM 7"))} ${border("◢│")}`,
      `${border("│")} ${copy("━━━━━━━━━━   ")} ${border("│")}  ${mark("┓")}`,
      `${border("│")} ${mark("██████████")}    ${border("│")}${mark("━━┫")}`,
      `${border("│")} ${copy("━━━━━━━━━━━━ ")} ${border("│")}  ${mark("┛")}`,
      `${border("└───────────────┘")}  ${mark("EVIDENCE → JUDGMENT")}`,
      "",
    ],
    Math.min(width, COMPACT_HEADER_WIDTH),
  );
}

function renderNarrow(theme: Theme, width: number): string[] {
  const ink = (text: string) => theme.fg("text", text);
  const mark = (text: string) => theme.fg("accent", text);

  return fit(
    [
      "",
      ink(theme.bold("SECSTACK")),
      `${mark("▰")} ${ink("10-K · ITEM 7")} ${mark("→")} ${mark(theme.bold("JUDGMENT"))}`,
      "",
    ],
    width,
  );
}

export function renderStartupHeader(theme: Theme, width: number): string[] {
  if (width >= WIDE_HEADER_WIDTH) return renderWide(theme, width);
  if (width >= COMPACT_HEADER_WIDTH) return renderCompact(theme, width);
  return renderNarrow(theme, width);
}

export default function startupHeaderExtension(pi: ExtensionAPI) {
  pi.on("session_start", (_event, ctx) => {
    if (ctx.mode !== "tui") return;

    ctx.ui.setHeader((_tui, theme) => ({
      render: (width) => renderStartupHeader(theme, width),
      invalidate() {},
    }));
  });
}
