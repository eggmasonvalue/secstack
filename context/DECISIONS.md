# DECISIONS.md

This is a curated ADR file for durable, non-obvious project-level choices. It is not a changelog or implementation worklog.

Append-only log of intentional tradeoffs. Newest entries on top. Read before
changing or re-litigating a choice.

Format:

```text
## YYYY-MM-DD — <short decision title>
Context: what forced the choice
Decision: what we chose
Tradeoff: what we gave up / what we rejected and why
Status: active | superseded by <date/title>
```

---

## 2026-08-31 — Distill routine 13F queries while preserving SEC-level provenance

Context: SEC 13F filings are authoritative but awkward for reverse stock-holder lookup and
routine manager history, while 13f.info already resolves managers, CUSIPs, filing portfolios,
and position histories. Exposing provider URLs or low-level CUSIP flags would invite agents to
leave the tool surface and repeat work.
Decision: Use 13f.info behind the SEC skill's routine stock-, manager-, and manager-position
queries. Keep the agent-facing interface job-based, abstract the intermediary from generated
reports, and expose the underlying SEC period, CIK, and accession. Use raw EDGAR for fields the
distilled route omits, provider failure, discrepancies, or requested verification.
Tradeoff: Routine queries depend on an unofficial distilled backend and its HTML/JSON shape, but
agents get a smaller, more capable interface while retaining a direct path to the regulatory
record.
Status: active

## 2026-08-12 — Replace Pi's coding identity without duplicating tool or skill guidance

Context: A profile-level `SYSTEM.md` replaces Pi's default prompt, which removes the
coding-agent identity as required but also suppresses Pi's dynamic tool snippets and guidelines.
A copied system file would also become stale after `pi update --extensions`.
Decision: Keep a one-line research identity in the SecStack package; bootstrap creates a relative
profile `SYSTEM.md` symlink to it. A package extension reconstructs Pi's prompt envelope from
live tool metadata, leaving all research procedure in the matching skills.
Tradeoff: The extension mirrors a small, stable part of Pi's prompt assembly, but preserves
active-tool changes automatically and avoids a second copy of tool or research guidance.
Status: active

## 2026-08-12 — Keep the profile free of coding-task resources

Context: The shared `pi-setup` package now includes global coding guidance and coding-oriented
skills, but SecStack is a dedicated research profile.
Decision: Load only SecStack's selected `pi-setup` extensions and themes. Do not link
`AGENTS.md` or `APPEND_SYSTEM.md`, and exclude `repo-nav` and `bootstrap-docs` by keeping the
package's skill filter empty.
Tradeoff: The profile does not inherit general coding workflow improvements, preserving a
smaller research-specific context and avoiding unrelated instructions.
Status: active

## 2026-08-12 — Keep research in the primary Pi context

Context: Sub-agent tools consume substantial context for their descriptors, can hide vital
research context, and introduce uncertain quality and cost tradeoffs when only weaker models
are available for delegation.
Decision: Do not install or invoke `pi-subagent`; the research workflow runs in the primary
Pi context.
Tradeoff: Research cannot be split across independent agents, but the full evidence trail and
model judgement stay together without an extra model-selection or context-budget dependency.
Status: active

## 2025-06-21 — market-scout uses agent-browser instead of a direct HTTP client

Context: Yahoo Finance transcript and market endpoints are unstable and
bot-hostile when scraped with a plain HTTP client.
Decision: Drive market-scout's transcript fetching through `agent-browser`.
Tradeoff: Adds a Node/`agent-browser` install step (no SEC identity needed but
an extra dependency) in exchange for reliable access to dynamic pages.
Status: active

## 2025-06-20 — Insider signals are volatility-adjusted via z-score

Context: A fixed percentage move (e.g. -20%) is routine for a biotech but
exceptional for a utility, so a flat threshold misfires across the universe.
Decision: Tag dip/rip buys by the stock's trailing 30-day return z-score
(default ±1.5σ) rather than a fixed percent move; only Form 4 open-market
purchases (code `P`) are counted.
Tradeoff: Requires per-stock volatility history and tuning of the z-score
threshold; rejects the simpler but universe-blind fixed-percent rule.
Status: active

## 2025-06-18 — Drop dollar values from 13F holdings output

Context: 13F dollar figures are stale (quarter-lagged, snapshot-priced) and
invited false precision in downstream memos.
Decision: Emit share counts only; the analyst divides 13F shares by shares
outstanding to derive ownership percentage.
Tradeoff: Loses an at-a-glance dollar figure in exchange for not anchoring on
misleading stale values.
Status: active

## 2025-06-16 — Progressive disclosure across all SKILL.md files

Context: Loading every reference and guide into context up front is token-heavy
and drowns the model's own judgement.
Decision: Each `SKILL.md` stays terse and points to `references/` guides the
agent loads only when needed; capabilities are framed around jobs, not file types.
Tradeoff: An agent must take an extra hop to load detail; gains a smaller,
sharper default context window.
Status: active

## 2025-06-15 — Consolidate the skills into a single monorepo

Context: Five related skills were drifting independently with duplicated
bootstrap and cross-references.
Decision: Keep all skills in one repo with shared root tooling (ruff,
markdownlint, CI) while each skill stays self-contained and independently
installable.
Tradeoff: One repo's CI gates every skill; gains shared conventions and a single
source of truth for cross-skill paths.
Status: active

## 2025-06-15 — Centralize runtime bootstrap in each skill's `_common.py`

Context: Windows consoles raise `UnicodeEncodeError` on emoji-rich output, and
corporate TLS-inspecting proxies break HTTPS with `CERTIFICATE_VERIFY_FAILED`.
Decision: On import, `_common.py` reconfigures stdout/stderr to UTF-8 on Windows
and injects `truststore` into SSL when available; it also owns the SEC identity
contract and cache layout shared across scripts.
Tradeoff: Import has side effects (frowned upon generally) in exchange for every
script getting identical, correct runtime setup with zero duplication.
Status: active
