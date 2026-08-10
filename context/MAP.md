# MAP.md

Where things live and how data flows. Read before touching structure or data flow.

## Repository shape

A Git Pi package containing five self-contained agent skills. The skills live under
`skills/` so the root of the repository can focus on package/profile setup.

```text
package.json          Pi package manifest for the five SecStack skills
scripts/bootstrap.mjs Isolated-profile bootstrap
skills/               Skill collection and skill-level documentation
  signal-sweep/       Discovery — scan the universe, surface tickers
  sec-edgar-skill/    Data — SEC EDGAR filings, ownership, 13F holders
  market-scout/       Data — price, peers, transcripts (Yahoo Finance)
  bottom-up-analyst/  Analysis — one ticker → auditable memo (the conductor)
  pitch-like-lou/     Voice — finished thesis → VIC-style pitch
context/              Agent-maintained project documentation
```

The package manifest exposes the five individual directories under `skills/`. It does not
expose `skills/README.md` as a skill.

## Pi profile data flow

The bootstrap configures the isolated profile at `~/.pi/secstack-agent`. Its
`settings.json` owns separate top-level package entries for:

- this SecStack package;
- the filtered `pi-setup` package;
- `pi-subagent`; and
- `agent-browser`.

Pi installs and updates each source independently. The bootstrap manages only those package
entries, the profile's Pi-managed shell path, the profile-local Python environment, and the
`APPEND_SYSTEM.md` link. Authentication, model selection, provider configuration, sessions,
and unrelated settings remain profile-local and untouched.

## Skill internals

- `skills/signal-sweep/` — `scripts/scan_insiders.py`, `scan_market.py`,
  `scan_conferences.py`, `search_themes.py`; universe config in `screens.json`; shared
  bootstrap in `scripts/_common.py`.
- `skills/sec-edgar-skill/` — `scripts/fetch_*.py`, `parse_financials.py`, `orient.py`,
  `list_headings.py`; guides in `references/`; shared bootstrap in `scripts/_common.py`.
- `skills/market-scout/` — `scripts/fetch_market_data.py`, `fetch_transcripts.py`, and shared
  `scripts/_common.py`.
- `skills/bottom-up-analyst/` — valuation `scripts/dcf.py`, `epv.py`; archetypes and guides in
  `references/`.
- `skills/pitch-like-lou/` — reference corpus only, no scripts.

## Data flow

```mermaid
flowchart TD
    SS[signal-sweep<br/>surfaces tickers] --> BUA[bottom-up-analyst<br/>deep dive + memo]
    BUA --> SEC[sec-edgar-skill<br/>filings]
    BUA --> MS[market-scout<br/>price / peers / transcripts]
    BUA --> PLL[pitch-like-lou<br/>renders pitch]
```

- `bottom-up-analyst` is the brain and conductor: it decides what to pull, reasons over it,
  and writes the memo. The data skills never decide what matters.
- The two filing/market data skills know nothing of each other and are swappable.
- `signal-sweep` and `sec-edgar-skill` both read `EDGAR_IDENTITY` and share on-disk cache
  contracts defined in their `_common.py` modules.

## Production order

`signal-sweep` → `bottom-up-analyst` → memo → optionally `pitch-like-lou`.

For the package installation and isolated-profile workflow, start at the root
[`README.md`](../README.md). For the collection overview, start at
[`skills/README.md`](../skills/README.md).
