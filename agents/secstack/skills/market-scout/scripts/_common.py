"""Shared runtime and output helpers for market-scout scripts."""

import os
import sys
from pathlib import Path

# Provider data can contain non-ASCII company and speaker names.
if sys.platform.startswith("win"):
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

try:
    import truststore

    truststore.inject_into_ssl()
except Exception:
    pass


def log(msg: str) -> None:
    """Write human-readable progress to stderr."""
    print(msg, file=sys.stderr, flush=True)


def emit(path: str | os.PathLike) -> None:
    """Write one absolute artifact path to stdout."""
    print(str(Path(path).resolve()), flush=True)
