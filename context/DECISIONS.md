# DECISIONS.md

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
