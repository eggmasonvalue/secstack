# US Market Research Skills

A composable stack of [agent skills](https://www.skills.sh/) for rigorous bottom-up equity
research on US-listed companies — from primary data (SEC filings + market data), through an
analytical framework, to a finished pitch. Each skill stands on its own; together they form a
pipeline.

## The skills

| Layer | Skill | Job |
|---|---|---|
| **Data** | [`sec-edgar-skill`](sec-edgar-skill/) | Retrieve & extract SEC EDGAR filings (10-K/10-Q/8-K, 20-F/6-K, XBRL financials, ownership, holdings), token-efficiently. Unopinionated. |
| **Data** | [`market-scout`](market-scout/) | Pull price, returns, peers, and sector screens via Yahoo Finance. Unopinionated. |
| **Analysis** | [`bottom-up-analyst`](bottom-up-analyst/) | Turn one ticker into an earned, auditable investment memo — drives the data skills, classifies the archetype, values it, tries to kill it. |
| **Voice** | [`pitch-like-lou`](pitch-like-lou/) | Render a Norbert Lou–style Value Investors Club pitch from a finished thesis. |

## How they compose

- **The two data skills are independent and swappable.** `sec-edgar-skill` (filings) and
  `market-scout` (market data) know nothing of each other; either can be replaced — e.g. point
  the analyst at a paid data provider instead of `market-scout` and nothing else changes.
- **The analyst is the brain and the conductor.** `bottom-up-analyst` decides what to pull,
  reasons over it, values the business, and writes the memo. It drives the data skills; they
  never decide what matters.
- **The voice renders from a finished thesis.** `pitch-like-lou` turns the analyst's memo into a
  pitch; it is not an idea generator.

**Production order:** analyst → memo → (optionally) Lou pitches from it. The analyst and the
voice deliberately overlap on value-investing discipline, so they can be swapped for your own
framework or presentation layer.

## Install

Install the whole stack, or any single skill on its own, with [skills.sh](https://www.skills.sh/)
— point it at this repository, or at a single skill subfolder. Each skill is a self-contained
folder with its own `SKILL.md`.

## Setup

Each skill documents its own setup; in brief:

- **`sec-edgar-skill`** — `pip install -r sec-edgar-skill/requirements.txt`, and set an SEC
  identity: `EDGAR_IDENTITY="Name email@example.com"` (required by SEC fair-access policy).
- **`market-scout`** — `pip install -r market-scout/requirements.txt`. No API key or identity.
- **`bottom-up-analyst`** — valuation scripts are standard-library only; no install needed.
- **`pitch-like-lou`** — documentation and a reference corpus; nothing to install.

## A note on scope

These skills produce **research, not advice**. They are tools for doing diligence rigorously and
honestly; nothing they output is a recommendation to buy or sell a security. The whole design —
filings-first grounding, verified-vs-assumed tagging, the pre-mortem — exists to keep an LLM's
fluent prose tethered to auditable evidence so a human can reach their own judgment.
