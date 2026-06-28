# AGENTS.md — Maya MCP Server

## Project Overview

This is an MCP (Model Context Protocol) server for Autodesk Maya. It enables LLM agents to interact with Maya sessions through structured tools for spatial awareness, camera planning, aesthetic analysis, and scene auditing.

## Repository Structure

```
src/maya_mcp_server/
├── server.py              # FastMCP server entry point, tool registration
├── client.py              # Maya connection client (native + Qt)
├── session_manager.py     # Multi-session management
├── maya_mcp_helper.py     # Maya-side helper (executed inside Maya)
├── maya_bootstrap.py      # Maya bootstrap code (create_module)
├── scene_tools.py         # 15 MCP scene tool definitions
├── scene_cache.py         # TTL + dirty-detection cache
├── cos_formatter.py       # Chain-of-Symbol notation formatter
├── maya_scene_module.py   # Maya-side module (injected via write_module)
├── spatial_types.py       # Data type definitions
├── security.py            # Input validation, rate limiting, pattern scanning
├── types.py               # Core types (ResultType, ClientType, SessionInfo)
├── bootstrap.py           # Server bootstrap
├── utils.py               # Utility functions
└── __main__.py            # Entry point

tests/
├── test_client.py
├── test_cos_formatter.py
├── test_prepare_code.py
├── test_scene_cache.py
├── test_scene_tools.py
├── test_security.py
└── test_session_manager.py
```

## Key Architecture Decisions

1. **No Maya client modification** — everything works through existing `execute_code` + `write_module` channels
2. **Maya-side module injection** — `_mcp_scene` is injected once via `write_module` on first scene tool call
3. **Large module handling** — modules >15K chars use temp-file injection to avoid command port buffer issues
4. **Response alignment** — `execute_code` handles both `str` and `dict` results to prevent `json.loads` errors
5. **CoS notation** — Chain-of-Symbol format saves ~65% tokens vs raw JSON

## ICEV Workflow

Every scene modification must follow:
1. **INSPECT**: `scene_snapshot()` — understand current state
2. **COMPUTE**: Use spatial data to calculate changes
3. **EXECUTE**: `execute_code()` — apply changes
4. **VERIFY**: `scene_assert()` + `scene_review()` — confirm results

## scene_review Dimensions (Universal)

The audit tool is generic — works for ANY Maya project:

| Dimension | Score | What it checks |
|-----------|-------|----------------|
| spatial | 15 | Object count, cameras, lights |
| overlaps | 15 | BBox collision (excludes parent-child) |
| conflicts | 15 | Penetration detection (excludes env objects like SUN) |
| zones | 10 | Naming-rule zone coverage |
| naming | 10 | Maya production naming convention |
| components | 15 | GRP_ grouping + nesting depth ≤ 4 |
| aesthetics | 10 | Color harmony + spatial balance + focal points |
| constraints | 5 | Max objects, custom rules |
| orphans | 5 | Empty groups, default names |

## Maya Naming Convention

- `GRP_` for groups, `GEO_` for geometry, `MAT_` for materials
- `CAM_` for cameras, `LGT_` for lights, `LOC_` for locators
- NEVER use default Maya names (pCube1, group1, etc.)

## Development Commands

```bash
# Run tests
python -m pytest tests/ -q

# Run with debug logging
LOGLEVEL=DEBUG python -m maya_mcp_server

# Security audit
semgrep scan --config auto src/
python scripts/secrets.py --path src
python scripts/dependency.py --path src
```

## Known Quirks

- Maya command port produces stale responses when large modules (>10K chars) are written. Fixed via temp-file injection for `_mcp_scene`.
- `execute_code` with `result_type="JSON"` may receive `dict` directly (not `str`). The client handles both.
- Stream capture auto-installs on first `get_client()` call.
- `import X; X.func()` pattern can fail with `prepare_code_for_result_capture`. Pre-import with `execute_code("import X", NONE)` then use expression-only calls.
