# Conference Classifier — Development Notes

**Last updated:** 2026-06-20  
**Status:** Working classifier in production. Autoresearch loop ready but not yet run (see §5).

This file is for humans and developer agents doing further work on the conference
detection feature. It is intentionally NOT referenced from SKILL.md or any script
docstring — the agent using the skill in production doesn't need to read this.

---

## 1. What this feature does

`scripts/scan_conferences.py` scans a date range of SEC 8-K filings to surface
companies that are presenting at investor conferences. Output is a markdown table
of ticker / company / sector / market cap / conference name.

The intended use is as a top-of-funnel signal — a company presenting at a conference
often means investor access, IR activity, and potential inflection points worth
investigating with the deeper research skills.

---

## 2. Why the original script was broken

The script that existed before this rewrite had two fundamental bugs:

**Bug 1 — Wrong item filter.**  
It searched only `items="8.01"` (Other Events). Empirical analysis showed ~75% of
real conference attendance filings use **Item 7.01** (Reg FD Disclosure) — companies
furnishing a presentation they shared at a third-party conference are making a Reg FD
disclosure, not an "other event". The old script was structurally blind to the majority
of its target population.

**Bug 2 — Keyword matching against metadata, not text.**  
The old Stage 2 did `_CONF_PATTERN.search(str(r))` where `r` is an EFTS result
object. `str(r)` is the Python string representation of the metadata dict — company
name, accession number, items list — not the filing text. So the keyword filter was
matching on things like `"conference"` appearing in the company name field of an
unrelated filing. It was effectively random.

---

## 3. How the new classifier works

### Stage 1 — EFTS server-side pre-filter

Six queries run against EDGAR's full-text search index, merged and deduplicated by
accession number (first-match wins). This is cheap — no filing downloads.

| Query | Item filter | ~Weekly vol | Rationale |
|---|---|---|---|
| `conference` | none | ~226 | Backbone. Catches ~75% of all conference filings via "presenting at the XYZ Conference" language |
| `"fireside chat"` | none | ~8 | Near-zero noise. Companies say exactly this. |
| `symposium` | none | ~4 | Clean. Medical/scientific conferences. |
| `"forum"` | `7.01` | ~60 | Genuine recall (AGA Financial Forum, Precision Medicine Forum, etc.) that "conference" misses. Item filter cuts boilerplate volume from 408→manageable. |
| `"investor day"` | `8.01` | ~2 | Companies hosting *their own* investor days file under 8.01. Skip Stage 2 (see below). |
| `"capital markets day"` | none | <1 | European-listed US names use this term exclusively. Skip Stage 2. |

**Queries deliberately excluded:**

- `summit` — 100% FPs. Summit Therapeutics, Summit Hotel, Summit Midstream flood it at all item levels. Their company name appears in every filing.
- `presentation` — 995/week, far too broad.
- `"analyst day"` — only 2 hits/week in tested period, both keyword-in-exhibit only. No incremental recall over `conference`.
- `"investor day"` without item filter — 2,999 raw hits, mostly unrelated filings where "investor day" appears in exhibits or boilerplate. Item filter `8.01` cuts this to ~14/week of clean own-hosted events.

### Stage 2 — Client-side text classification

For each candidate, download the actual filing HTML (`r.get_filing().text()`) and run:

**2a. Exclusion check** (`_all_occurrences_excluded`):  
Find every occurrence of the signal word in the text. If EVERY occurrence sits inside
a known false-positive phrase (±60 char window), reject. Key insight: if a filing says
"conference call" three times AND "presenting at the Goldman Sachs Conference" once,
the single non-excluded occurrence is enough to pass. Only reject if there is zero
non-excluded occurrence.

Current exclusion list:

```python
["conference call", "conference call and webcast",
 "exclusive forum", "forum selection", "alternative forum"]
```

**2b. Attendance verb check** (`_has_attendance_verb`):  
Require at least one regex pattern to match:

```python
["will present", "presenting at", "participate in",
 "scheduled to present", "speak at", "participation at",
 "will attend", "will be attending"]
```

`"will attend"` was added after a live test showed the AGA Financial Forum filing
("Unitil Corporation will attend the American Gas Association Financial Forum")
failing with only the original 6 patterns.

**Stage 2 exceptions** (`no_text_check_queries`):  
`"investor day"` and `"capital markets day"` skip Stage 2 entirely. Reason: for
these event types, the announcement language is often only in the attached exhibit
(PDF presentation deck), not in the HTML body. The EFTS match + item filter is
reliable enough signal on its own. Attempting Stage 2 would produce false negatives.

### Ticker extraction

The EFTS result `company` field already contains the ticker in parentheses:
`"LCI INDUSTRIES  (LCII)  (CIK 0000763744)"`. Extract with `r'\(([A-Z]{1,5})\)'`,
first match. No API fallback needed. Companies without a parenthesised ticker
(foreign filers, government entities, private companies) are skipped — they won't
be in-universe anyway.

---

## 4. Empirical findings that shaped the design

All of these were verified by running live EFTS queries and inspecting actual filing
text during a research session in June 2026.

**Conference seasonality** (relevant for label building and performance expectations):

- **Jan 6-17**: Highest density. JPM Healthcare Conference alone generates 100+
  filings in one week.
- **May-June**: Highest overall volume. Goldman, JPMorgan TMC, BofA, Wells Fargo,
  Needham, Baird all cluster here. ~226 "conference" hits/week.
- **Sep 8-26**: Back-to-school season. Deutsche Bank, Barclays, Jefferies.
- **Late Jul/Aug**: Dead zone. Avoid for labelling.
- **Mid-Oct to mid-Nov**: Pre-earnings blackout. Very few conferences.

**"forum" noise structure** (informed the exclusion list):  
Of 20 sampled `"forum"` + items=7.01 results:

- 4 TPs (Precision Medicine Forum, AGA Financial Forum, etc.) — 0% overlap with "conference"
- 4 FPs from bylaw boilerplate ("exclusive forum", "forum selection amendment",
  "alternative forum") — all filterable with the 3 exclusion phrases added
- 3 FPs from "Investor Forum" (Acadian Asset Management's own investor event, filed
  repeatedly) — borderline TP, acceptable to let through
- 9 keyword-in-exhibit only — correctly handled by SKIP_NO_TEXT

**"investor day" item behaviour**:  
`items='7.01'` returns 0 results; `items='8.01'` returns ~14/week. This is because
companies hosting their OWN investor day file it as an "other event" (8.01), whereas
companies presenting at a THIRD-PARTY conference file under Reg FD (7.01). This
distinction is important for the query design.

---

## 5. Autoresearch plan (ready to execute when viable)

The goal: use an iterative Jules-powered loop to tune the `exclusions` and `patterns`
lists against a precision/recall target, rather than hand-tuning them.

### What needs to exist in this repo first

**a) `data/labels.json`** — ground truth dataset.

Jules built a partial labels dataset on branch
`rewrite-conference-classifier-2032772644618132070` (269 JSONL entries from
Jan 2026). Format:

```json
{"id": "accession_number", "company": "...", "ticker": "...", "filed": "...",
 "items": [...], "matched_query": "...", "text": "...", "label": "CONFERENCE_ATTENDANCE|OTHER",
 "confidence": "high|medium|low"}
```

**Recommended expansion**: supplement with ~100 filings from Jun 2-6, 2026
(BofA Global Technology + Jefferies Global Healthcare week). This adds cross-sector
diversity and is representative of production conditions. Target 150-200 total labels,
balanced between CONFERENCE_ATTENDANCE and OTHER.

**b) `scripts/eval_harness.py`** — scoring script.

Accepts `--params '{"exclusions": [...], "patterns": [...]}'`, runs the two-stage
classifier against `labels.json`, prints:

```json
{"metric_value": <precision>, "target_met": <precision>=0.90 AND recall>=0.70>,
 "details": {"precision": ..., "recall": ..., "f1": ...,
              "false_positive_ids": [...], "false_negative_ids": [...]}}
```

A template is in the `jules-autoresearch` skill at
`references/eval_harness_template.py`.

### Loop invocation

```bash
python <jules-autoresearch>/scripts/autoresearch.py \
  --source "sources/github/eggmasonvalue/secstack" \
  --eval-script "signal-sweep/scripts/eval_harness.py" \
  --params '{
    "exclusions": ["conference call", "conference call and webcast",
                   "exclusive forum", "forum selection", "alternative forum"],
    "patterns": ["will present", "presenting at", "participate in",
                 "scheduled to present", "speak at", "participation at",
                 "will attend", "will be attending"]
  }' \
  --target "precision >= 0.90 with recall >= 0.70" \
  --metric-type numeric \
  --target-value 0.90 \
  --parallel 3 \
  --max-iterations 8 \
  --output-dir autoresearch_results/conference_classifier
```

**What Jules tunes**: `exclusions` list and `patterns` list only. The EFTS queries
(Stage 1) are fixed — they define the recall ceiling and should not be modified by
the loop.

**What "parallel 3" means here**: Jules evaluates current params + 2 ablation
variants in a single session (not 3 separate sessions). 1 Jules session per
iteration.

**Why autoresearch wasn't run yet**: the loop was designed, the infra was built
(`autoresearch.py`, `jules_client.py`), but `labels.json` was incomplete (Jules
built 269 entries but only from Jan 2026, single-sector heavy) and `eval_harness.py`
doesn't exist yet. These are ~1 hour of Jules work to complete before the loop
can run.

### Expected convergence

Starting precision is unknown but likely 0.70-0.80 based on manual inspection.
The patterns list is probably under-specified (missing verbs like "invited to present",
"will be hosting", "plan to present"). The exclusion list may need 1-2 more phrases
for "conference call" variants ("quarterly conference call", "earnings conference
call"). The loop should converge in 3-5 iterations.

---

## 6. Known remaining issues

**Conference name extractor is rough.** `_extract_conference_name` sometimes returns
phrases like "materials to be used during the conference" or truncates at 120 chars.
This is cosmetic — doesn't affect precision/recall — but the output table looks bad.
A tighter regex or extracting from a specific sentence pattern would help. Not worth
fixing until the classifier precision is tuned.

**`"forum"` query still has ~60% reject rate** at Stage 2. This is expected — the
bylaw boilerplate is getting filtered correctly. But it means 60% of the 408/week
forum candidates are wasted downloads. A potential optimisation: add a quick
pre-screen for forum bylaw language before downloading the full text (check if
the accession's items list includes `5.03` — bylaws amendment — and skip those).

**EFTS caching** (`edgartools` caches responses in `~/.edgar/_tcache/`). If a query
fails silently on first run (e.g., SSL not yet configured), it caches 0 results.
Subsequent runs with warm cache return 0 even after the SSL issue is resolved.
Workaround: delete the relevant cache file or wait for cache expiry.

**yfinance 404s** for valid tickers that aren't in Yahoo's database (e.g., YICC,
MODG) are expected and benign — they're caught by `except Exception` in the enrichment
block and the filing still appears in output with missing price/sector data.
