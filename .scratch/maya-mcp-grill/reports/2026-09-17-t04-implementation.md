# T-04 Implementation Report \u2014 Unified Security Pipeline + Marker-Block userSetup.py

Date: 2026-09-17
Branch scope: D-008, D-014(b), D-017, D-018, D-019

## Summary

All 18 MCP tools now pass through a single FastMCP middleware
(security.py primitives + pipeline.py orchestrator): validate ->
rate-limit (read/write token buckets) -> pattern scan -> dispatch ->
audit JSONL. userSetup.py install/uninstall now follows D-017 A'
marker-block semantics. Maya-domain errors migrated to
{error:{code,message,suggestion?}}; host failures raise coded
exceptions that surface as isError + [code] text.

## Evidence

### 1. Tests
- `python -m pytest tests/ -q` -> `443 passed, 3 skipped`
  (baseline 370+3skip; +73 new: pipeline 32, connection_guide 35 incl.
  marker-block cases, security +6, checkpoint D-019 shape class).

### 2. Quality budgets (must not rise)
- `python -m ruff check src/ --output-format concise` -> `Found 175` (baseline 185)
- `python -m ruff check . --output-format concise` -> `Found 238` (baseline 244)
- `python -m mypy src/` -> `Found 221 errors in 3 files` (baseline 223)

### 3. Compile / package / smoke
- `python -m compileall -q src/` -> clean
- `pip wheel . --no-deps -w dist/` -> maya_mcp_server-0.1.0-py3-none-any.whl
- stdio MCP smoke (node script, tools/list): `tool count: 18; tools
  missing annotations: []; tools missing a hint: []` \u2014 all 18 tools
  expose readOnlyHint/destructiveHint/idempotentHint/openWorldHint.
- stdio tools/call: `execute_code {code:'os.system("x")'}` ->
  isError=true, text `[blocked_pattern] execute_code.code blocked by
  code-os-system: os command execution (suggestion: ...)`.

### 4. Audit JSONL lands + replays
- File: `%LOCALAPPDATA%/mcp-for-maya/mcp-for-maya/Logs/audit.jsonl`
  (platformdirs user_log_dir("mcp-for-maya")).
- Real stdio run produced lines like:
  `{"event_id":"\u2026","timestamp":"2026-09-17T02:59:08.965Z","session_id":"\u2026",
  "tool_name":"execute_code","input_summary":"code=\"os.system(\"x\")\"",
  "outcome":"rejected","warnings":[{"rule_id":"warn-os-exec",\u2026}]}`
- tests/test_pipeline.py::TestAuditJsonlContract pins: every line is a
  valid JSON object with the full schema, replay-by-tool filtering,
  rotation preserves JSONL, write failure never raises, input_summary
  is allowlist preview (\u2264200 chars, sha256 for large strings,
  credential-shaped names redacted).

### 5. D-017 userSetup.py marker block
- `python -m pytest tests/test_connection_guide.py -q` -> 35 passed.
- Semantics: missing file -> created (block only); existing no-marker
  -> needs_confirm + proposed_block, writes only on confirm=True;
  existing marker -> in-place replace (already_current idempotent);
  unparseable/unterminated -> refused with fallback; every write
  preceded by <file>.bak.<timestamp> and the path is reported;
  uninstall strips only the region; only-block file reports
  file_now_empty unless remove_empty_file=True.
- generate_user_setup_content(port) == _marker_block(port) == the text
  shown in fallback instructions (byte-identical).

### 6. D-019 error contract
- maya_scene_module: all error returns are {error:{code,message,
  suggestion?}} \u2014 pinned codes: invalid_name, checkpoint_exists,
  path_not_directory, dir_not_writable, untitled_scene,
  workspace_unavailable, snapshot_write_failed, snapshot_missing,
  preserve_failed, invalid_filename, path_escapes_dir, snapshot_lost,
  auto_snapshot_failed, open_failed, rebind_failed, object_not_found,
  check_failed, unknown_shot_type, target_not_found.
- TestDomainErrorShape in test_checkpoint_rollback.py asserts the shape
  on live calls; checkpoint metadata (existing/preserved_as/
  original_file_status/scene_rebound_to) preserved at top level.
- Host side: PipelineError subclasses (invalid_input, rate_limited,
  blocked_pattern, maya_unavailable, maya_execution) raise with
  [code] prefixes -> MCP isError. MayaConnectionError/MayaExecutionError
  now subclass PipelineError.

### 7. Threat-model documentation (8 items)
- docs/threat-model.md: explicit threat model, boundary declaration
  (regex scan/validation/rate-limit/audit/marker block/Maya-side exec
  are NOT boundaries), defense inventory, port & network exposure,
  annotations matrix, audit schema + jq replay, reporting pointer,
  roadmap delta.
- SECURITY.md: private reporting channel, in/out-of-scope list.
- README.md / README_en.md: warning box \u2014 "safety net for accidents
  and injected instructions \u2014 not a boundary against a malicious
  client". No 'sandbox'/'secure' misuse anywhere (only meta-references
  in ADR-0005/threat-model saying we avoid them).

### 8. Honesty fixes (rui.txt \u4E09\u5904 + helper)
- Real TokenBucket replaces the mislabeled sliding window; comment
  corrected.
- sanitize_error_message Windows regex now covers full paths
  ([A-Za-z]:[\\/][^\\s"']+).
- import re at module top (no in-function import).
- maya_mcp_helper.py: "controlled namespace for security" comment
  replaced with explicit not-a-boundary note (__builtins__ present).
- connection_guide: _get_platform deduped to utils.get_platform;
  three platform scanners collapsed into one root-driven loop; false
  "\u5DF2\u751F\u6210" copy removed; hardcoded Administrator path removed.

## Known limits

- Audit input_summary still records a \u226440-char head of code values \u2014
  intentional forensics (spec: \u8131\u654F\u6458\u8981\u975E\u7EAF\u54C8\u5E0C); credential-shaped
  param names are redacted, but a secret embedded inside code text is
  not detected (documented in threat-model \u00A72/\u00A76).
- mypy/ruff legacy debt untouched (E701/E501 in maya_scene_module,
  aesthetic_engine) \u2014 budgets only decreased, per ratchet rule.
- safe_mode AST allowlist remains roadmap P2, unimplemented, and is
  documented as such.
