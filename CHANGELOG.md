# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Scene-intelligence layer on top of the upstream connection stack: 13 scene tools (snapshot / inspect / measure / assert / validate / checkpoint / rollback / checkpoint_list / camera_create / camera_orbit / aesthetics / review / plan) plus 2 GUI-only visual tools (scene_viewport_snapshot, scene_render_preview) — 20 MCP tools total.
- ICEV (Inspect-Compute-Execute-Verify) workflow enforced in server instructions; two experimental agent process cards under `skills/` (icev-workflow, scene-review-playbook).
- Unified pipeline across all tools: argument validation, per-session token-bucket rate limits, warn-only pattern scan, independent JSONL audit log.
- Transactional safety: exportAll in-memory checkpoints with whitelisted filenames, automatic safety snapshot before rollback, explicit scene rebind.
- Qt framed working channel (length-prefixed frames, up to 16 MiB) with a minimal native commandPort fallback for headless sessions.
- `maya_setup_guide` (diagnose / install / guide / uninstall) with idempotent marker-block merge into userSetup.py and timestamped backups.
- Project docs: CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, docs/threat-model.md, docs/adr/*, docs/testing.md, dual README (中文 + English).

### Changed

- Distribution renamed to `mcp-for-maya` (import package stays `maya_mcp_server`); console scripts are now `mcp-for-maya` plus `maya-mcp-server` as a compatibility alias; project URLs point to Xxx91n/mcp-for-maya.
- README rewritten: honest three-tier blender-mcp comparison, code-sourced numbers (20 tools, 11 audit checks with real weights, CoS figure attributed to its paper), a real `skills/` section, zero-telemetry statement, and a versioning policy.
- Two-layer error contract: host-side failures surface via MCP isError with a code prefix; Maya-side results return `{error:{code,message,suggestion}}`.

### Fixed

- JSON-serialized argument passing across scene tools (closes the string-interpolation injection surface in scene_validate / scene_measure / scene_assert).
- scene_checkpoint now snapshots in-memory state via exportAll instead of copying the last saved file; rollback whitelists basenames and rebinds the scene path explicitly.
- World-bbox math unified on the 8-corner transform for rotated objects.
- scene_review check list, weights, and sampling limits aligned to the implementation.
- Aesthetic engine single-sourced (standalone module injected into Maya, replacing the divergent dual implementation).
- add_session now uses the post-bootstrap dedicated-port client; Qt channel rewritten to event-driven reads with per-connection queues.

### Removed

- Phantom references: LOGLEVEL env var, scripts/secrets.py, scripts/dependency.py, and the "4 Codex Skills" README promise (replaced by the real `skills/` cards).
