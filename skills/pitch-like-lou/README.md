# Pitch Like Norbert Lou

An [agent skill](SKILL.md) for rendering an already-researched investment thesis as a concise,
numbers-first pitch inspired by Norbert Lou's Value Investors Club writing. It focuses on the
transferable craft: document-level specificity, reproducible arithmetic, a fair statement of the
objection, and candor about weak evidence.

The skill is a presentation layer. It does not source a company, form a thesis, or confer conviction
on incomplete work. Within [SecStack](../README.md), [`bottom-up-analyst`](../bottom-up-analyst/)
owns the research and valuation workflow; [`sec-edgar-skill`](../sec-edgar-skill/) and
[`market-scout`](../market-scout/) retrieve source material.

## Layout

- `SKILL.md` — the rendering workflow, voice guidance, and evidence pass.
- `references/corpus/` — seven primary-source pitches and public discussion threads for targeted
  style calibration. The skill tells the agent when and how narrowly to consult them.

## Corpus

The corpus contains Markdown extractions of Value Investors Club write-ups authored by
`charlie479`:

| Pitch | Broad situation |
|---|---|
| NVR, Sportsman's Guide | Operating business / compounder |
| Winmill | Asset discount |
| Quilmes, MCI, NII Holdings, Telemig | Special situation / capital structure |

They are legacy ideas from 2001–2009, not current research or templates whose facts and metrics
should be copied into a new pitch. They are included as a small educational reference set; an
agent should retrieve only the passage needed to calibrate a specific writing move.

Copyright in the underlying write-ups remains with their respective authors and Value Investors
Club. This repository is a non-commercial educational project and is not affiliated with or
endorsed by Value Investors Club. A rights holder may open an issue or contact the maintainer to
request removal.
