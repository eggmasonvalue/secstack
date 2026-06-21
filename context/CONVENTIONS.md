# CONVENTIONS.md

Terse imperative code rules. No rationale here — rationale lives in
`DECISIONS.md`. Read while writing code.

## Tooling commands

- Lint Python: `uv run ruff check .`
- Format Python: `uv run ruff format .`
- Check formatting: `uv run ruff format --check .`
- Lint Markdown: `npx markdownlint-cli2 "**/*.md"`
- Run a skill's deps: `pip install -r <skill>/requirements.txt`

## Python

- Target Python 3.11; keep `line-length = 100`.
- Import the skill's `scripts/_common.py` for runtime setup and shared contracts.
- Send human-readable progress to stderr via `log`; send the machine-readable
  result (an absolute path) to stdout via `emit`.
- Write Google-style docstrings on public modules and classes.
- Keep each skill self-contained and independently installable.
- Qualify cross-skill script paths fully; never assume a shared CWD.
- Never hard-code `EDGAR_IDENTITY` or webhook URLs; read them from the environment.

## SEC / data

- Count only Form 4 open-market purchases (code `P`) as insider buys.
- Emit 13F share counts only — no dollar values.
- Write all cache under the git-ignored `*-cache/` dirs; never commit cache.

## Markdown / docs

- Keep each `SKILL.md` terse; defer detail to `references/` (progressive disclosure).
- Ensure `AGENTS.md`, `README.md`, and everything in `context/` pass markdownlint.

## Git

- Work on a branch; open a PR. Never commit to `main` directly.
