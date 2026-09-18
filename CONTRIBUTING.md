# Contributing

## Development setup

```bash
pip install -e ".[dev]"            # or: uv pip install -e ".[dev]"
python -m pytest tests/ -q         # stub-layer suite (contract tests vs the maya.cmds stub)
ruff check .                        # lint — frozen budget gate (.github/ruff-baseline.json), ratchet only goes down
mypy src                           # typecheck — strict for new files
python -m maya_mcp_server -vv      # run with DEBUG logs (-v=INFO, -vv=DEBUG)
```

House rules:

- Every fix ships with a regression test on the maya stub layer.
- Real-Maya tests are a separate local manual tier (`pytest -m mayapy`, see docs/testing.md) — never mixed with the stub tier.
- If your change makes a doc line stale, fix that line in the same commit (propagation matrix in AGENTS.md).

## Pull requests

- One branch per change; keep diffs small and reviewable.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (feat / fix / docs / refactor / test / chore).
- CI gates (`.github/workflows/ci.yml`): `pytest` must be green on ubuntu + windows; the ruff budget
  (`.github/ruff-baseline.json`) is ratchet-only-down — above budget fails, and a lower count may be
  budgeted down in the same PR commit with the reason stated. `mypy` (221 known errors) runs locally
  but is not a CI gate yet (full quality gate is a later round).

## Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) v2.1. Be respectful, assume good faith, keep discussion technical.
