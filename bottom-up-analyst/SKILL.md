---
name: bottom-up-analyst
description: >-
  Run a rigorous bottom-up fundamental deep dive on a single company and produce a
  pitch-ready investment memo. Use this skill whenever the user hands you one stock — a
  ticker or a name — and wants real due diligence: an investment thesis, a long/short
  case, "is this a buy?", a valuation, a bull/bear teardown, an earnings-quality check, or
  a full research write-up. Reach for it any time the task is "research this company",
  "should I own this", "what do you think of X", or "do a deep dive on Y" — even if
  neither "memo" nor "valuation" is said out loud.
---

# Bottom-Up Analyst

This skill is the **analyst** in a three-layer research stack. It turns *one name* into an
*earned thesis*, written up as a detailed, auditable investment memo that a reader can act
on. It does the work that sits between raw data and a finished pitch - the work of actually
deciding what the numbers mean.

## Where this sits - the seam with the other two skills

A bottom-up stack has three jobs, and they are deliberately kept separate:

- **The hands** - `sec-edgar-skill` (SEC filings and 13F institutional holder data) and
  `market-scout` (price, returns, the peer set, and earnings call transcripts):
  unopinionated data/tools layers. They fetch and extract token-efficiently; they *never*
  decide what matters.
- **The analyst - this skill.** It is both **the brain and the conductor.** It decides
  *what* to pull and *why*, reasons over it, values the business, stress-tests the
  conclusion, and writes the memo. The agent that chooses the evidence and the agent that
  judges it are the same agent - that is how real analysts work, and why this layer drives
  the tools rather than waiting to be handed numbers.
- **The voice** - `pitch-like-lou`: renders a *pitch* from a finished thesis. Short,
  compelling, "a pitch with conditions." A reader hooked by the pitch drops into **this
  skill's memo** for the full due diligence behind it.

So the production order is: **analyst → memo → (optionally) Lou pitches from it.** You
produce the substance. You do not need to invoke the voice skill yourself; your job is to
make the memo *pitch-ready* - complete and honest enough that a pitch can stand on it
without inventing anything.

## The prime directive: conviction must be earned, never manufactured

Every conclusion in the memo must trace to something you actually verified in a document
or computed yourself. This is not a style note - it is the whole point. A confident memo
built on an unchecked assumption is worse than no memo, because it *launders a guess into a
recommendation*.

The quality gate that prevents this is **Lou's honesty gate** - separate what you *know*
from what you *believe*, concede the weak points out loud, tag second-hand claims as
second-hand, and demand a margin of safety that survives the bad parts (governance,
dilution, cyclical risk). It is a **necessary condition on every memo regardless of company
type**. The gate lives in one place - `pitch-like-lou`, "the one inviolable rule" (with the
MCI QUIPS cautionary tale of a thesis nearly sunk by an unverified third-hand claim). Read
it there; apply it to every memo here.

Lou's gate is *necessary but not sufficient.* It does **not** dictate the analysis - this
skill researches companies Lou never touched (hypergrowth tech, regulatory-tailwind
inflections, turnarounds). The *method* below supplies the sufficiency; Lou's temperament
supplies the honesty.

## The loop

Work through these phases in order, but let the **archetype** decide where the weight goes -
a hypergrowth name lives in phases 3 and 6; a cyclical in 4; a special-situation in 5 and 7.

1. **Orient and scope - filings first, always, before any web search.** Run
   `sec-edgar-skill`'s `scripts/orient.py` as the **very first tool call** - before web
   search, before `market-scout`, before anything else. This is non-negotiable even when the
   user describes breaking news ("just reported," "a few hours ago," "announced today").
   orient.py takes seconds and immediately shows you what was filed today; a web search for
   the same information is slower, less authoritative, and often wrong about the company.

   **Breaking-news pattern:** if the user mentions a same-day event, orient.py will show the
   8-K filed today. Pull it and its press-release exhibit (Exhibit 99.1) via `sec-edgar-skill`,
   which documents the exact breaking-news fetch sequence. That exhibit is the primary
   source; read it rather than web-searching for what it contains.

   After orient, read the latest **annual report** (10-K, or 20-F for an FPI) - its business
   section and MD&A - and skim the most recent **interim/current** reports (10-Q/8-K, or 6-K
   for an FPI) to learn, in the company's own words, *how it makes money.* You cannot value a
   business you cannot explain in one plain sentence. Pull the market snapshot (price, market
   cap, **the peer set**, sector) from `market-scout` to frame size and comps - orientation,
   not evidence.

   **Pull the latest earnings call transcript** via `market-scout`, then read or grep it.
   The transcript is a **primary source** — management's own words on guidance, strategy,
   and tone. The Q&A section is especially valuable: analyst questions often target exactly
   the weak points you need to stress-test in phase 6.

2. **Classify the archetype.** Almost every company is dominated by one shape, and the
   shape decides which DD emphases, metrics, disqualifiers, and valuation method carry the
   weight. Pick one primary archetype (a secondary is fine) and **load that playbook** from
   `references/archetypes/`. See the routing table below. When nothing fits cleanly, the
   core spine here is the fallback - reason from first principles.

3. **Reconstruct the normalized economics.** GAAP rarely shows the real earning power.
   Drive `sec-edgar-skill` to pull the statements (XBRL → CSV), then *un-distort* them:
   separate maintenance from growth capex, pull deferred revenue back into the picture, undo
   one-offs, treat stock-comp and leases honestly, build owner earnings / FCF. Show capital
   allocation as a **year-by-year table** (share count, debt, reinvestment, returns on it) -
   a trend persuades where a single number cannot. See `references/guide_normalization.md`.

   **When the thesis depends on a new revenue stream** - a pre-revenue JV, a partnership
   product, a market entry unlocked by regulation, a post-restructuring margin profile -
   build a **unit-economics bridge** from per-unit inputs (price, cost, volume) to the
   stream's FCF contribution. A management TAM estimate plugged into a DCF growth rate is
   not a model; it launders a guess into a valuation. The bridge makes the assumption
   auditable: a reader who disagrees with your per-unit fee or customer count can re-run
   the math. See `references/guide_normalization.md` § "When the thesis depends on a new
   revenue stream."

4. **Read the competitive and industry position.** A number is only as good as the moat
   under it. Establish industry structure, the company's place in it, and - the hard part -
   *relative* competitive advantage. **SEC filings are the default and the grounding**: the
   10-K's competition and risk-factor sections, and crucially the **peers' own filings**
   (their 8-Ks, 10-Qs, 10-Ks) for management commentary, pricing, and sentiment you can
   cite. **Peers' earnings call transcripts** are equally valuable primary sources - a
   competitor's CEO discussing pricing pressure, capacity additions, or market-share wins
   on their own call is citable competitive intelligence - pull peer transcripts via
   `market-scout` and grep the cached file for the subject company's name, the product
   category, or pricing language. Use **web research only for what filings and transcripts genuinely
   cannot give you** - relative positioning, market-share dynamics, channel/customer
   checks - and label every web claim as such. See `references/guide_competitive.md`.

   **Quantify impact, don't just list forces.** Every competitive strength, threat, and
   moat mechanism must be *sized* - how big, how fast it's moving, and the dollar impact
   on this company. A force you can't size is one you haven't understood. See
   `guide_competitive.md` § "Quantify impact" for the full framework and examples.

5. **Value it - by triangulation, weighted by archetype.** Never a single point estimate.
   Converge on an intrinsic-value *range* from independent lenses, weighted by what the
   archetype makes trustworthy: a **reverse-DCF** ("what growth/margin does today's price
   already imply, and is that achievable?") is first-class - especially for hypergrowth,
   where it is often the *only* honest lens - alongside a forward DCF, an EPV no-growth
   floor, and peer multiples. End with an explicit **margin of safety**. Use the bundled
   `scripts/` and `references/guide_valuation.md`.

   **Discount rate: reason it, don't default it.** Derive the discount rate from the
   business's actual risk profile - never default to 10% or 12%. The memo's valuation
   section **must** include a "Discount Rate Derivation" subsection. See
   `references/guide_valuation.md` § "Discount rate" for the full methodology.

6. **Try to kill it - pre-mortem.** Assume it's a year later and the thesis failed; write
   down why. Run the **archetype's disqualifiers** (each playbook lists them) *and* Lou's
   honesty gate (above). Most candidates should die here or get marked down - that is the
   system working, not failing. Re-tag every surviving claim as verified vs. assumed.

   Before finalising the risk assessment, read the **ownership signal**: pull institutional
   (13F) and insider (Form 4) data via `sec-edgar-skill`, then interpret it against the
   thesis. This is where adverse selection surfaces - a concentrated holder base that can
   crater the float, smart money accumulating or quietly exiting, insiders buying with their
   own capital or selling into your long. Account for every cluster buy and every
   discretionary senior-officer sale; a signal you skip is a risk you took blind. See
   `references/guide_ownership_signals.md` for how to read each pattern (13F reports stale
   quarter-end prices, so use the **share counts** and divide by shares outstanding from the
   `market-scout` snapshot for ownership %).

7. **Reach a verdict at the conviction the work supports.** State the call - **Long /
   Short / Pass / Watch** - with an honest conviction level, the **variant perception**
   (what you believe that the market doesn't, and why you're right), the catalysts or
   monitorables that would confirm or break it, and the margin of safety. If the digging was
   thin, say so and dial conviction down; a hedged verdict is still a verdict.

8. **Write the memo.** Render everything into the standard-DD structure in
   `references/memo_template.md`. The memo *is* the deliverable; pitch-ready is the
   definition of done.

## Archetype routing

Classify in phase 2, then load exactly one playbook (Lou's three shapes are the
value-investing subset; the rest extend past where he worked). Read only the one in play -
each is loaded lazily so you carry just the lens you need.

| If the company is primarily... | Tell by... | Load |
| :-- | :-- | :-- |
| A **quality compounder** - high ROIC, long reinvestment runway | durable returns on capital well above cost, pricing power, low capital intensity | `references/archetypes/compounder.md` |
| A **hypergrowth** name - fast top-line, profits immature | >25-30% growth, heavy S&M, GAAP losses or thin margins, large TAM claim | `references/archetypes/hypergrowth.md` |
| A **cyclical** - earnings swing with a cycle | commodity/industrial/financial exposure, margins that breathe with demand | `references/archetypes/cyclical.md` |
| A **turnaround / inflection** - economics bending on a catalyst | margin or demand inflecting on a regulatory, sectoral, or self-help change | `references/archetypes/turnaround.md` |
| A **special situation** - a structural or legal fact drives it | spin-off, post-bankruptcy, merger/arb, seniority waterfall, squeeze-out | `references/archetypes/special_situation.md` |
| A **deep-value / asset play** - price below tangible value | net cash, net-net, hidden assets, liquidation/sum-of-parts angle | `references/archetypes/deep_value.md` |
| **None fits cleanly** ("anything") | - | Stay on the core spine above; reason from first principles. |

## Driving the tools - the conductor's job

You are the one deciding what the hands fetch. Be deliberate and frugal:

- **Reuse the cache.** `sec-edgar-skill` writes filings to `./sec-cache/{TICKER}/` with
  deterministic, accession-keyed names. `market-scout` caches transcripts to
  `./transcript-cache/{TICKER}/transcripts/`. Before fetching, glob the cache; re-use
  what's there rather than re-hitting the source.
- **Pull by section, not whole filings.** Use item codes (10-K Item 1/1A/7/8) and
  heading maps; grep the cached Markdown and read only the lines that matter. A 10-K can
  exceed 100k words - loading one whole buries the signal.
- **Transcripts are greppable too.** Once cached, grep a transcript for "guidance",
  "margin", a competitor's name, or a specific metric - you don't need to read the whole
  45-minute call to find the passage that matters.
- **Ownership data is cached like everything else.** `sec-edgar-skill` writes 13F and
  insider output to the same `sec-cache/{TICKER}/` tree under scope-keyed filenames. Glob
  the cache before re-fetching — if the window you need is already on disk, grep and read
  it rather than re-hitting the source.
- **Spend tokens where the archetype says the value hides.** Don't fetch a proxy's
  compensation tables for a hypergrowth TAM question, or a deferred-revenue footnote for a
  liquidation. Let the playbook route you.
- **For foreign private issuers** there is no 10-K/10-Q/DEF 14A - it's 20-F and 6-K, and the
  financials are IFRS. `sec-edgar-skill`'s guides cover the mechanics.

If a tool detail is unclear, defer to `sec-edgar-skill`'s and `market-scout`'s own guides
and `--help`; do not re-document the hands here. Keep the tools unopinionated; keep the
opinion in this skill.

## Web research - grounding first, web for the gaps

Filings are the spine of the memo because they are auditable and primary. Reach for the web
only when no filing can answer the question - chiefly *relative* competitive advantage,
real-time market share, pricing dynamics, and channel or customer checks. When you do:
**attribute and date every web claim**, prefer primary sources (company IR, regulators,
trade bodies) over aggregators, and never let a web assertion silently outrank a filing.
Mark web-sourced claims distinctly in the memo so the reader can weight them.

**Do not fire any web search until orient.py has returned and you have read at least one
filing section.** This applies even for breaking news: orient.py will surface the 8-K
filed today, and the 8-K's Exhibit 99.1 is the press release - the primary source that
any web article is merely summarising. Fetch the exhibit; don't search for the summary.

**When a tool errors, recover - don't escape to the web.** A failed `sec-edgar-skill` call
is a fixable usage detail, not a signal to pivot to web search. Re-run `orient.py`, read the
relevant guide, or query `.docs`, then retry. The web is a *supplement for what filings
cannot cover* - never a fallback for filings you failed to fetch.

## Valuation tooling

Run the bundled scripts rather than hand-rolling a DCF per memo. `--help` is the
authoritative flag reference; canonical invocations:

```bash
# Forward DCF (bear/base/bull sensitivity via comma-separated growth)
python scripts/dcf.py --fcf0 1200 --growth 8,12,16 --years 10 --terminal-growth 3 \
  --discount 10 --shares 500 --net-debt 200

# Three-stage DCF (add --growth2/--years2 when the trajectory bends)
python scripts/dcf.py --fcf0 5 --growth 25,35,50 --years 3 \
  --growth2 5,8 --years2 7 --terminal-growth 2.5 --discount 12 \
  --shares 30 --net-debt 66 --price 2.75

# Reverse DCF (what growth does today's price imply?)
python scripts/dcf.py --mode reverse --price 150 --fcf0 1200 --years 10 \
  --terminal-growth 3 --discount 10 --shares 500 --net-debt 200

# EPV (no-growth floor)
python scripts/epv.py --ebit 600 --tax 21 --wacc 9 --shares 500 --net-debt 200
```

`references/guide_valuation.md` explains which lens to weight for which archetype, when to
use three-stage vs two-stage, and how to set the discount rate and terminal value honestly.

## Bundled resources

| Resource | When to read / run |
| :-- | :-- |
| `references/memo_template.md` | The required output structure. Read before writing the memo. |
| `references/guide_normalization.md` | Phase 3 - un-distorting the financials into owner earnings. |
| `references/guide_competitive.md` | Phase 4 - SEC-first competitive work; when to go to the web. |
| `references/guide_valuation.md` | Phase 5 - triangulation, reverse-DCF, discount/terminal discipline. |
| `references/guide_ownership_signals.md` | Phase 6 - reading the 13F and insider ownership signal. |
| `references/archetypes/*.md` | Phase 2 - load the one matching the company's shape. |
| `scripts/dcf.py`, `scripts/epv.py` | Phase 5 - the valuation arithmetic. `--help` for flags. |

## Definition of done: pitch-ready

The memo ships when it passes **Lou's honesty gate** end to end - concretely:

1. every claim is verified in a document or computed yourself, and everything unverified is
   marked as such; and
2. you have been as honest and specific about what is wrong with the thesis as about what
   is right.

Both true - the memo is pitch-ready.
