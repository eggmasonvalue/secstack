# SECstack

SECstack is a bottom-up equity research harness for US-listed companies built on SEC filings. It
bundles five composable research skills from a single source of truth and ships as both:

- an **Antigravity CLI plugin** (`secstack` bare custom main agent with zero bleed into coding
  sessions and bounded `run_workflow` fan-out), and
- an isolated **[Pi](https://pi.dev/) profile** (`~/.pi/secstack-agent`, with selected Pi
  extensions, themes, and Pi-managed `agent-browser`).

## Antigravity CLI

SECstack packages an isolated `secstack` main agent (`excludeDefaultComponents: true`,
`inheritMcp: false`) with its skills co-located under `agents/secstack/skills/`. Because the
plugin exposes no top-level `skills/` directory, coding agents (`Default`, `clean`, `bare`) never
load SECstack's research skills or instructions.

### Antigravity prerequisites

- [Antigravity CLI (`agy`)](https://antigravity.google/)
- Python 3.11 or newer and [uv](https://docs.astral.sh/uv/) on `PATH`
- [`agent-browser`](https://www.npmjs.com/package/agent-browser) on `PATH` plus its one-time
  browser install (`agent-browser install`) for `market` earnings-call transcripts
- `EDGAR_IDENTITY` exported in your shell for SEC-facing requests (see
  [One-time runtime setup](#one-time-runtime-setup))

### Antigravity install & launch

Install directly from GitHub (or from a local checkout):

```bash
agy plugin install https://github.com/eggmasonvalue/secstack
```

Verify installation and start a session:

```bash
agy agents
agy --agent secstack
```

You can also switch to `secstack` interactively inside any `agy` session via `/agents`.

No shell launcher or manual `uv sync` is required: the `secstack` agent invokes dependency-backed
skill scripts via `uv run --project` using an external cache environment
(`${XDG_CACHE_HOME:-$HOME/.cache}/secstack/<skill>`), keeping the installed plugin directory clean
across updates and writing `./sec-cache/`, `./screen-cache/`, and `./transcript-cache/` in
your research workspace.

### Workflows in Antigravity

The `secstack` agent includes `run_workflow` with a private bare `worker.md` for horizontal
fan-out—multi-ticker thematic sweeps, shortlist triage after `screen`, peer-comp extraction,
bulk transcript scans, and independent red-team citation audits—capped at `<= 4` concurrent EDGAR
workers. Single-company thesis synthesis, normalization, valuation judgment, and
`diligence` → `pitch-like-lou` rendering stay in the primary context.

## Pi profile

The normal Pi profile is not modified. SECstack uses:

```text
~/.pi/secstack-agent
```

### Pi install

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

The bootstrap is safe to rerun. It configures `allowScripts` for `agent-browser` in the
profile's npm root (`~/.pi/secstack-agent/npm/package.json`), installs the unpinned top-level
Pi package sources, merges only SECstack-managed package entries, shell-path configuration,
and `quietStartup` preference into the SECstack profile's `settings.json` and creates a
profile-local Python environment. It links the profile's `SYSTEM.md` to the installed SECstack
package, so `pi update --extensions` updates the research-agent identity and prompt envelope.
It does not install coding-task guidance or link global `AGENTS.md` or `APPEND_SYSTEM.md` files
into the profile.

It does not overwrite the profile's `auth.json`, `models.json`, provider settings,
model selections, UI preferences, sessions, or unrelated settings.

### Pi launch & update

The bootstrap offers to add a `secpi` Bash function to `~/.bashrc`. After opening a
new Bash shell (or running `source ~/.bashrc`), use:

```bash
secpi
```

The launcher activates the SECstack virtual environment, exposes the Pi-managed npm
binaries, and starts Pi with the isolated profile. It accepts normal Pi arguments:

```bash
secpi --mode json -p "Summarize the current research workflow."
```

Without the launcher, start the profile directly:

```bash
PI_CODING_AGENT_DIR="$HOME/.pi/secstack-agent" pi
```

Update every Pi-managed package in the SECstack profile with the launcher:

```bash
secpi update --extensions
```

If the launcher is not installed or loaded in the current shell, use the profile
prefix directly:

```bash
PI_CODING_AGENT_DIR="$HOME/.pi/secstack-agent" pi update --extensions
```

After updating, use `/reload` inside Pi to load the new resources without restarting the
machine.

Python dependencies are installed or refreshed with `uv` when the bootstrap is rerun. They
are not part of Pi's `pi update --extensions` lifecycle.

### Included Pi packages

The SECstack Pi profile manages these as separate top-level Pi packages:

- `git:github.com/eggmasonvalue/secstack` — this repository's five skills, research-agent
  prompt envelope, and responsive SECstack startup header
- `git:github.com/eggmasonvalue/pi-setup` — selected extensions and themes only
- `git:github.com/eggmasonvalue/pi-system-prompt-viewer` — `/system-context` overlay
- `git:github.com/trefeon/pi-freeflow` — free model provider proxy and relay
- `npm:agent-browser`

The selected `pi-setup` resources are `btw`, `notify`, `session-context`, `tavily-web`,
`vibe-spinner`, and the `midnight-pastel`, `pastel-dark`, and `pastel-light` themes. Its
coding-oriented skills, including `repo-nav` and `bootstrap-docs`, are excluded.

Each independently managed source remains a top-level profile package so
`pi update --extensions` can update it independently. Third-party resources are not copied
into this repository or bundled as nested dependencies. In Pi, research runs in the primary
context; the profile does not install or invoke sub-agents.

## One-time runtime setup

`market` transcript fetching uses `agent-browser`. Its browser/runtime installation is a
one-time step (on Antigravity, install `agent-browser` globally on `PATH` first; on Pi, the
bootstrap installs it as a Pi-managed npm package):

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

## Skills

The five research skills are documented in
[`agents/secstack/skills/README.md`](agents/secstack/skills/README.md). The production flow is:

```text
screen → diligence → edgar / market → pitch-like-lou
```

## Development

The repository layout and data flow are documented in [`context/MAP.md`](context/MAP.md).
Project conventions are in [`context/CONVENTIONS.md`](context/CONVENTIONS.md). Run the
following checks before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
npx markdownlint-cli2 "**/*.md"
agy plugin validate .
```

## Scope

These skills produce research, not investment advice. They are tools for doing diligence
rigorously and honestly; nothing they output is a recommendation to buy or sell a security.
