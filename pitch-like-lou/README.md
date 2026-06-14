# Pitch Like Norbert Lou

An [agent skill](SKILL.md) that teaches an LLM to **investigate and write an investment
pitch the way Norbert Lou** (username `charlie479` on Value Investors Club) did — the analyst
whose NVR, Quilmes, and Winmill write-ups Joel Greenblatt handed out to his students as
exemplars of high-conviction value investing.

The skill is deliberately scoped to two reproducible things: a **disposition** (where value
tends to hide, what to read, what to normalize) and a **voice** (how Lou structures and argues
a pitch, and the temperament that makes it credible). It does **not** invent a thesis — the raw
material comes from SEC-filing and market-data tools (it composes naturally with the
[`sec-edgar-skill`](../sec-edgar-skill/) and [`market-scout`](../market-scout/) data skills, and
with [`bottom-up-analyst`](../bottom-up-analyst/) as the framework), and the actual analytical
insight comes from reasoning over real filings. See [SKILL.md](SKILL.md) for the full design, or
the [stack overview](../README.md) for how the skills fit together.

## Layout

- `SKILL.md` — the skill itself (the only file an agent needs to load).
- `references/corpus/` — the seven primary-source pitches, used for voice calibration. They ship
  with the skill; an agent greps them for a specific rhetorical move rather than loading them whole.

## A note on the corpus

`references/corpus/` contains Markdown extractions of seven Value Investors Club write-ups (and
their public discussion threads) authored by `charlie479`:

| Pitch | Shape |
|---|---|
| NVR, Sportsman's Guide | quality compounder |
| Winmill | cigar-butt asset play |
| Quilmes, MCI, NII Holdings, Telemig | special situation / structural arbitrage |

These are **legacy ideas (2001–2009)** that VIC itself makes publicly available after a 45-day
delay, and which have circulated freely for years (they are widely reproduced verbatim — e.g.,
across investing newsletters and Substacks — and were distributed in classrooms by Joel
Greenblatt). They are archived here **solely** as a small, fixed reference set for an educational
tool, with **no commercial use** intended.

Copyright in the underlying write-ups remains with their respective authors and Value Investors
Club. This repository is a non-commercial, educational project and is not affiliated with or
endorsed by Value Investors Club. If you are a rights holder and would prefer a pitch not be
included, please open an issue or contact the maintainer and it will be removed promptly.
