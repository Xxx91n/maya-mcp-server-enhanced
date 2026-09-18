"""Compare a ruff JSON report against the frozen error budget.

Usage: check_ruff_budget.py <ruff-report.json> <ruff-baseline.json>

Budget semantics (frozen budget, ratchet-only-down):
- each top-level segment (src/, tests/, anything else) has a frozen count;
- count > budget  -> fail (new lint debt);
- count <= budget -> pass; a lower count may be budgeted down in the same
  PR commit with the reason stated in the commit message.
The CI never writes the budget file.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def segment_of(filename: str) -> str:
    """Top-level directory of a path made relative to the repo root (cwd)."""
    name = filename
    if os.path.isabs(name):
        name = os.path.relpath(name, Path.cwd())
    parts = name.replace(chr(92), "/").split("/")
    if len(parts) <= 1 or parts[0] in ("", ".", ".."):
        return "other"
    return parts[0]


def main() -> int:
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    budget = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

    counts: dict[str, int] = {}
    for diag in report:
        seg = segment_of(diag.get("filename", ""))
        counts[seg] = counts.get(seg, 0) + 1

    failed = False
    for seg in sorted(set(counts) | set(budget)):
        count = counts.get(seg, 0)
        cap = budget.get(seg, 0)
        status = "OK" if count <= cap else "OVER"
        hint = ""
        if count < cap:
            hint = " (below budget - may be lowered in the same PR commit)"
        print(f"{seg}: {count}/{cap} {status}{hint}")
        if count > cap:
            failed = True
            print(f"::error::ruff budget exceeded for {seg}/: {count} > {cap}")

    if failed:
        print(
            "Frozen budget is ratchet-only-down: fix the new errors, or"
            " lower the budget file in the same PR with the reason stated."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
