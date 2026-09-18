---
name: icev-workflow
description: "Enforce the Inspect-Compute-Execute-Verify loop for every Maya scene modification via the mcp-for-maya MCP server. Use whenever a task will create, move, rename, delete, or otherwise mutate scene objects — prevents blind edits by requiring scene_snapshot before changes and scene_assert/scene_review (plus visual tools on GUI sessions) after them."
compatibility: "Tested on Claude Code only; requires mcp-for-maya MCP server"
---

# ICEV Workflow

> **Experimental.** Evaluated on Claude Code only; untested on Codex/Gemini CLI/Cursor. Tracked in issue #3.

ICEV = Inspect → Compute → Execute → Verify. Every scene mutation goes through all four phases, in order, every time. Skipping Inspect produces blind edits; skipping Verify produces unverified claims — both are the failure modes this workflow exists to prevent.

## When to use

- Any request that modifies the scene: create, move/rotate/scale, rename, reparent, delete, or change materials, lights, cameras.
- Read-only questions ("what is in the scene?") need only Inspect — answer straight from `scene_snapshot`.

## The loop

### 1. INSPECT

Call `scene_snapshot()`; add `scene_inspect(target)` for deep detail on one object or zone. Build the spatial model — names, types, positions, bounding boxes, hierarchy — BEFORE deciding anything.

### 2. COMPUTE

Plan changes against the snapshot data: positions, sizes, clearances, naming. Apply the production naming convention: `GRP_` groups, `GEO_` geometry, `MAT_` materials, `CAM_` cameras, `LGT_` lights, `LOC_` locators — never default Maya names. If the scene may have changed since the last snapshot, re-snapshot instead of trusting stale coordinates.

### 3. EXECUTE

Apply changes with `execute_code` — batch related edits into one call. Before risky or destructive operations, take `scene_checkpoint(name)` first so a rollback path exists.

### 4. VERIFY

- `scene_assert(expectations=...)` — verify the objects/properties you intended to change.
- `scene_review()` — full audit when the change is structural (new groups, relayout, many objects).
- GUI sessions only: `scene_viewport_snapshot()` (what the artist sees) or `scene_render_preview()` (clean single frame) for visual confirmation. On headless sessions these return a `gui_session_required` error — do not retry them there.

## Failure handling

- VERIFY fails → re-INSPECT the affected region, fix, re-verify. Never report success before a verify pass confirms it.
- EXECUTE fails mid-change → `scene_rollback(filename)` to the last checkpoint, then `scene_snapshot()` to rebuild context — snapshots carry no undo history.
- After any rollback, always re-snapshot; never assume the post-rollback state.

## Standing rules

- Never report "done" on a mutating task without a verify step in the same turn.
- Batch related changes into one `execute_code` call; run `scene_review` after a unit of work, not between micro-edits.
- The pipeline (validation, rate limits, pattern scan) is a safety net for accidents — treat its rejections as stop signals, not obstacles to route around.
