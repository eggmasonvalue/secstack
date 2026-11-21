---
name: run-workflow
description: >-
  Write and run Python workflow scripts with run_workflow using type_name="worker"
  for bounded multi-ticker fan-out, peer extraction, bulk transcript sweeps, and
  independent memo verification.
disable-slash-command: true
---

# Dynamic Workflows (`run_workflow`)

A workflow is a Python script executed by `run_workflow` to coordinate isolated bare workers (`type_name="worker"`). Use it for horizontal multi-ticker sweeps, peer-comp extraction, bulk transcript scans, and independent red-team citation audits. Keep single-company thesis synthesis in the primary context.

## Critical Rules for `secstack`

1. **Always pass `type_name="worker"`**: Built-in `"self"` is unavailable on custom agents (`subagent "self" not found`). Every `agent(...)` call must pass `type_name="worker"`.
2. **Brief workers explicitly**: `worker` runs bare (`excludeDefaultComponents: true`, `inheritMcp: false`). Include in every worker prompt:
   - Absolute research workspace path (`WORKSPACES[0]`) and absolute `<skills-root>` path.
   - Exact `SKILL.md` path(s) to read (e.g., `<skills-root>/sec-edgar-skill/SKILL.md`).
   - Required provenance fields so handoffs stay lossless (figures, units, periods, SEC accession or URL, cached file path, verbatim quote, explicit errors/gaps).
3. **Cap EDGAR concurrency (`<= 4`) and isolate per-ticker failures**: SEC EDGAR enforces a 10 req/s per-IP rate limit, and `parallel(...)` cancels all siblings if one worker fails. Wrap EDGAR fan-outs with `asyncio.Semaphore(4)` and `asyncio.gather(..., return_exceptions=True)` so one bad or delisted ticker does not abort the sweep.

## Invocation & Primitives

Pass inline Python via `Script` (or a file via `ScriptPath`) with a short `Description` and optional JSON `Args` (exposed as `args`). Top-level `await` and `async def` are supported; `WORKSPACES` (tuple, primary first), `CONVERSATION_ID`, `STEP_INDEX`, and `args` are injected.

| Primitive | Behavior |
| :--- | :--- |
| `phase(name)` | Starts a named UI phase grouping logs and worker cards. |
| `log(*args)` | Appends a line to workflow logs and tool result `Logs:`. |
| `agent(prompt=None, schema=None, role=None, type_name="worker", workspace="inherit", model=None)` | Defines a lazy worker. `await agent(...)` runs once and returns the parsed `finish` value matching `schema`. `w = agent(...)` then `await w(prompt, schema)` runs sequential turns retaining conversation state (`del w` ends it). |
| `parallel(items, fn)` | Runs `fn(item)` concurrently in item order; cancels siblings if any item raises. |
| `pipeline(items, fn)` | Runs `fn(item)` sequentially in item order. |
| `await trajectory(last=None, types=None, tools=None, min_index=None, max_index=None)` | Reads earlier parent steps before `run_workflow` started. |

Key `agent(...)` arguments:

- `type_name`: `"worker"` (required).
- `schema` *(required)*: JSON Schema dict/string enforced via the child's `finish` tool.
- `model`: `"inherit"` (default; keep for financial judgment), `"flash"` / `"flash_lite"` (only for purely mechanical extraction), or `"pro"`.
- `role`: Short UI card title (e.g., `f"{ticker}: 280E tax extraction"`).

## Patterns

### Bounded Multi-Ticker Fan-Out (EDGAR Rate-Safe + Failure-Isolated)

```python
import asyncio
import json

SKILLS_ROOT = args["skills_root"]
WS = WORKSPACES[0]
TICKERS = args["tickers"]

SCHEMA = {
    "type": "object",
    "properties": {
        "ticker": {"type": "string"},
        "status": {"type": "string", "enum": ["ok", "partial", "error"]},
        "rows": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fiscal_year": {"type": "string"},
                    "metric_value": {"type": ["number", "null"]},
                    "units": {"type": "string"},
                    "accession": {"type": "string"},
                    "cached_path": {"type": "string"},
                    "verbatim_quote": {"type": "string"},
                },
                "required": ["fiscal_year", "metric_value", "units", "accession", "cached_path"],
            },
        },
        "caveats": {"type": "string"},
    },
    "required": ["ticker", "status", "rows", "caveats"],
}

sem = asyncio.Semaphore(4)

async def extract_one(ticker: str):
    async with sem:
        return await agent(
            f"""Workspace: {WS}
Skills root: {SKILLS_ROOT}
Read {SKILLS_ROOT}/sec-edgar-skill/SKILL.md first.
For {ticker}, pull the last 3 fiscal years of the requested disclosure from its latest 10-K/20-F.
Return exact figures, SEC accession, absolute cached file path, verbatim footnote excerpt, and caveats.""",
            schema=SCHEMA,
            type_name="worker",
            role=f"{ticker}: filing extraction",
        )

phase("Extract cohort")
raw = await asyncio.gather(*(extract_one(t) for t in TICKERS), return_exceptions=True)
results = [
    {"ticker": t, "status": "error", "rows": [], "caveats": str(r)} if isinstance(r, Exception) else r
    for t, r in zip(TICKERS, raw)
]
print(json.dumps(results, indent=2))
```

### Stateful Anomaly Follow-Up Within a Workflow

```python
w = agent(
    f"Workspace: {WORKSPACES[0]}. Skills root: {args['skills_root']}. Read sec-edgar-skill/SKILL.md first.",
    type_name="worker",
    role=f"{ticker}: deep footnote check",
)
first = await w(
    f"Extract 3-year cash taxes and 280E tax provisions from {ticker}'s latest 10-K. Flag any IRS refund claims.",
    schema=FIRST_SCHEMA,
)
if first.get("has_irs_claim"):
    followup = await w(
        "Inspect the contingencies and subsequent-events footnotes in the same filing for IRS claim amounts and uncertain tax benefits.",
        schema=FOLLOWUP_SCHEMA,
    )
del w
```
