# AGENTS.md

Universal entry point for agents working in this repo. Read this first.

## Guiding principle

Only document what an agent **cannot quickly recover by reading the code**. Code
is the source of truth for *what the code does*. Docs exist for *where things
live* (`context/MAP.md`) and *why the tradeoffs were made* (`context/DECISIONS.md`).
Everything else rots — do not write it.

## Hard guardrails

- **Never commit to `main` directly.** Always work on a branch and open a PR.
- **Never commit secrets.** `EDGAR_IDENTITY` and `DISCORD_WEBHOOK_URL` are
  supplied via environment / CI secrets, never hard-coded.
- **Never commit cache output.** `sec-cache/`, `signal-sweep-cache/`, and
  `transcript-cache/` are regenerated on demand and are git-ignored.
- **Lint and format must pass** before a PR (see `context/CONVENTIONS.md`). CI
  runs `ruff check`, `ruff format --check`, and `markdownlint-cli2`.

## Read routing

Do not read everything by default. Read on demand:

- Touching module structure or data flow → read `context/MAP.md` first.
- Changing or re-litigating a tradeoff → read `context/DECISIONS.md` first.
- Writing code → read `context/CONVENTIONS.md`.
- Starting any task → check the `todo` tool for open items.

## Write triggers (event-based)

- Module added / moved / removed, or data flow changed → update `context/MAP.md`.
- Intentional tradeoff made → **append to `context/DECISIONS.md`** (mandatory;
  this is the most-forgotten artifact).
- New repeatable pattern or standard adopted → add to `context/CONVENTIONS.md`.
- User-facing behavior or usage changed → update `README.md`.

## Do NOT document

- Changelog / worklog — that is git history.
- Feature or status lists — code already shows what exists.
- Restatements of what the code plainly does.
- Decisions with no real tradeoff.

## CONVENTIONS vs DECISIONS

A convention is **one imperative line with no "because"**. The moment it needs a
"because", it is a decision — move the rationale to `context/DECISIONS.md` and let
the convention link to it.

## Todos ↔ Decisions

Todos are ephemeral. When closing a todo that involved a real tradeoff,
**graduate the durable part into `context/DECISIONS.md`** before the todo
disappears.

## Definition of Done

A task is done only when the matching durable artifacts reflect the change. An
unrecorded tradeoff means **not done**.
