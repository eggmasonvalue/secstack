# SecStack

SecStack is an isolated [Pi](https://github.com/badlogic/pi-mono) profile for rigorous
bottom-up research on US-listed companies. It bundles five composable skills, selected
Pi extensions and themes, and Pi-managed `agent-browser`.

The normal Pi profile is not modified. SecStack uses:

```text
~/.pi/secstack-agent
```

## Install

Prerequisites:

- Git
- Node.js
- Pi
- Bash (Git Bash on Windows)
- Python 3.11 or newer
- uv

From Bash, bootstrap the profile with one command:

```bash
(tmp=$(mktemp -d) && git clone --depth 1 https://github.com/eggmasonvalue/secstack "$tmp" && node "$tmp/scripts/bootstrap.mjs"; status=$?; rm -rf "$tmp"; [ "$status" -eq 0 ])
```

The bootstrap is safe to rerun. It installs the unpinned top-level Pi package sources,
merges only SecStack-managed package entries and shell-path configuration into the
SecStack profile's `settings.json` and creates a profile-local Python environment. It links the
profile's `SYSTEM.md` to the installed SecStack package, so `pi update --extensions` updates the
research-agent identity and prompt envelope. It does not install coding-task guidance or link
global `AGENTS.md` or `APPEND_SYSTEM.md` files into the profile.

It does not overwrite the profile's `auth.json`, `models.json`, provider settings,
model selections, UI preferences, sessions, or unrelated settings.

## Launch

The bootstrap offers to add a `secstack-pi` Bash function to `~/.bashrc`. After opening a
new Bash shell (or running `source ~/.bashrc`), use:

```bash
secstack-pi
```

The launcher activates the SecStack virtual environment, exposes the Pi-managed npm
binaries, and starts Pi with the isolated profile. It accepts normal Pi arguments:

```bash
secstack-pi --mode json -p "Summarize the current research workflow."
```

Without the launcher, start the profile directly:

```bash
PI_CODING_AGENT_DIR="$HOME/.pi/secstack-agent" pi
```

## Update

Update every Pi-managed package in the SecStack profile with:

```bash
PI_CODING_AGENT_DIR="$HOME/.pi/secstack-agent" pi update --extensions
```

After updating, use `/reload` inside Pi to load the new resources without restarting the
machine.

Python dependencies are installed or refreshed with `uv` when the bootstrap is rerun. They
are not part of Pi's `pi update --extensions` lifecycle.

## One-time runtime setup

The bootstrap installs `agent-browser` as a Pi-managed npm package. Its browser/runtime
installation is a separate one-time step. Start the SecStack profile, then run:

```bash
agent-browser install
agent-browser --version
```

SEC-facing skills require an identity string for the SEC fair-access policy. Set it in the
shell before using those skills; do not commit it:

```bash
export EDGAR_IDENTITY="Jane Analyst jane@example.com"
```

The insider scan can optionally post to Discord. Set the webhook in the environment when
using that feature:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## Included packages

The SecStack profile manages these as separate top-level Pi packages:

- `git:github.com/eggmasonvalue/secstack` — this repository's five skills
- `git:github.com/eggmasonvalue/pi-setup` — selected extensions and themes only
- `git:github.com/eggmasonvalue/pi-system-prompt-viewer` — `/system-prompt` overlay
- `npm:agent-browser`

The selected `pi-setup` resources are `btw`, `notify`, `session-context`, `tavily-web`,
`vibe-spinner`, and the `midnight-pastel`, `pastel-dark`, and `pastel-light` themes. Its
coding-oriented skills, including `repo-nav` and `bootstrap-docs`, are excluded.

Each independently managed source remains a top-level profile package so
`pi update --extensions` can update it independently. Third-party resources are not copied
into this repository or bundled as nested dependencies. Research runs in the primary Pi
context; the profile does not install or invoke sub-agents.

## Skills

The five skills are documented in [`skills/README.md`](skills/README.md). The production
flow is:

```text
signal-sweep → bottom-up-analyst → sec-edgar-skill / market-scout → pitch-like-lou
```

## Development

The repository layout and data flow are documented in [`context/MAP.md`](context/MAP.md).
Project conventions are in [`context/CONVENTIONS.md`](context/CONVENTIONS.md). Run the
following checks before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
npx markdownlint-cli2 "**/*.md"
```

## Scope

These skills produce research, not investment advice. They are tools for doing diligence
rigorously and honestly; nothing they output is a recommendation to buy or sell a security.
