# Contributing

## Development setup

```bash
pip install -e ".[dev]"            # or: uv pip install -e ".[dev]"
python -m pytest tests/ -q         # stub-layer suite (contract tests vs the maya.cmds stub)
ruff check src tests               # lint — error budget is frozen, ratchet only goes down
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
- Baseline gates: pytest green (the maya-stub tier), ruff and mypy error counts must not increase.

## Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) v2.1. Be respectful, assume good faith, keep discussion technical.
