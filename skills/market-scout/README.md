# Market Scout

Public market context and earnings-call transcript retrieval for US-listed stocks via
[`yfinance`](https://github.com/ranaroussi/yfinance) and Yahoo Finance. The skill returns source
material; it does not decide whether a security is attractive.

Part of the [SecStack skills](../README.md) collection.

## Setup

The SecStack bootstrap installs this skill's dependencies into the profile environment. For
standalone use:

```bash
uv sync --project "<skill-dir>"
```

Activate the resulting environment or prefix script commands with
`uv run --project "<skill-dir>"`.

Transcript retrieval also uses the Pi-managed `agent-browser` binary. Install its browser runtime
once from an active SecStack profile:

```bash
agent-browser install
```

## Examples

Keep the research workspace as the current directory and invoke the installed scripts by their
resolved paths so generated transcript cache stays with the research:

```bash
python "<skill-dir>/scripts/fetch_market_data.py" --ticker AAPL --peers
python "<skill-dir>/scripts/fetch_transcripts.py" --ticker AAPL --list
python "<skill-dir>/scripts/fetch_transcripts.py" --ticker AAPL --latest 1
```

See [SKILL.md](SKILL.md) for routing, output contracts, and runtime discovery beyond the bundled
report fields. Yahoo data is best-effort and can be stale or incomplete for thinly covered names;
verify load-bearing facts against an issuer or regulatory source.
