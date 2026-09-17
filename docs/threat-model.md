# Threat Model \u2014 maya-mcp-server

> Status: current (D-008/D-017/D-018/D-019, 2026-09-17). Source of truth
> for what this project's safety machinery does and does not claim.

## 1. Explicit threat model

**Trusted party**: the MCP client/agent (Codex, Claude, \u2026) and the local
user who runs this server.

**Risk addressed**: confused-deputy \u2014 an agent that receives injected or
misunderstood instructions and drives this server's capabilities toward
outcomes the user did not intend. Also plain accidents: runaway loops,
bad filenames, oversized payloads.

**Risk explicitly NOT addressed**: a malicious client. Any MCP client can
send arbitrary tool calls; nothing here can or does try to contain a
hostile one. If the client is the attacker, the game is already over \u2014
the controls below are a safety net for accidents and confused deputies,
not a boundary.

## 2. Boundary declaration

The following are **not** security boundaries:

- The regex pattern scan. It catches obvious accidents; it is trivially
  bypassable and we say so. Detection, not containment.
- Input validation. It rejects malformed inputs, not malicious intent.
- Rate limiting. It slows accidents, not adversaries.
- The audit log. It records what happened; it prevents nothing.
- The `userSetup.py` marker block. It protects *your* file from
  being overwritten; it does not protect Maya from the block.
- Anything Maya-side (`maya_mcp_helper.py`, `_mcp_scene`).
  Code reaching Maya runs with Maya's full privileges \u2014 __builtins__ is
  fully present in the exec namespace by design.

We deliberately avoid the words "sandbox" and "secure" for these
mechanisms. A future opt-in AST allowlist (`safe_mode`, roadmap
P2) would still be a hallucination-slowing net, not a jail \u2014
language-level confinement of Python inside Maya is a known-won't-fix
problem.

## 3. Defense inventory (the actual safety net)

| Layer | What it does | Where |
|-------|--------------|-------|
| Input validation | size caps, session-key format, module-name rules | security.py |
| Rate limiting | per-session token buckets: ~20 writes/60s, ~100 reads/60s | security.py |
| Pattern scan | exact-match blocks (`..` traversal in filenames, `os.system`/`subprocess`/`eval(` in code); everything else warn-only into audit | security.py |
| Audit log | append-only JSONL, every tool call recorded incl. rejections | security.py |
| Error contract | host failures raise coded exceptions (isError); Maya-domain failures return `{error:{code,message,suggestion?}}` | pipeline.py, maya_scene_module.py |
| Checkpoint/rollback | exportAll memory snapshots, auto safety snapshot before rollback, S2 rebind | maya_scene_module.py |
| userSetup.py merge | marker-block upsert, confirm-gated, .bak backup, symmetric uninstall | connection_guide.py |
| Tool annotations | readOnlyHint/destructiveHint/idempotentHint/openWorldHint on all 18 tools | pipeline.py |

All 18 tools pass through one FastMCP middleware pipeline:
validate \u2192 rate-limit \u2192 pattern-scan \u2192 dispatch \u2192 audit.

## 4. Port and network exposure

- The MCP server speaks stdio/SSE to its client; the Maya channel is a
  localhost TCP command port (default `:7001`, sourceType=python).
- The command port binds localhost only; `allow_remote_connections`
  defaults to False and there is no remote path today.
- Anyone who can reach the command port can run Python inside Maya \u2014
  that is Maya's own model, not something this server adds or can remove.
  Keep it localhost; do not port-forward it.

## 5. Tool annotations (MCP hints)

Every tool carries four hints as cooperation signals (the server-side
pipeline enforces regardless):

- destructive: `execute_code`, `write_module`,
  `maya_setup_guide` (install/uninstall), `camera_create`,
  `camera_orbit`, `scene_checkpoint`
- destructive=false but non-idempotent: `scene_rollback`
  (recovery semantics; marking destructive would spook confirm UX)
- readOnly+idempotent: all `scene_*` read tools, `list_sessions`
- openWorld=false everywhere: no tool reaches the open network

See `pipeline.TOOL_ANNOTATIONS` for the full matrix.

## 6. Audit log schema and replay

One JSON object per line (JSONL), at
`platformdirs.user_log_dir("mcp-for-maya")/audit.jsonl`:

```json
{"event_id":"uuid","timestamp":"ISO8601Z","session_id":"host:port",
 "tool_name":"execute_code","input_summary":"code=\"print\u2026\"(12B sha:ab12)",
 "outcome":"success|error|rejected","duration_ms":1.2,
 "warnings":[{"rule_id":"\u2026","match":"\u2026"}]}
```

- File mode 0600, size-based rotation (audit.jsonl.N), write failures
  never block tool execution; dual-written to the app logger.
- `input_summary` is an allowlist preview (\u2264200 chars): param
  names, short values, size+sha for large strings; credential-shaped
  param names (token/secret/password/api_key) are redacted.
- `outcome=rejected` is always recorded \u2014 probing is the first
  signal of a confused deputy.

Replay:

```bash
jq -c 'select(.tool_name=="execute_code")' audit.jsonl
jq -c 'select(.outcome=="rejected")' audit.jsonl
jq -c 'select(.session_id=="127.0.0.1:7001")' audit.jsonl
```

## 7. Vulnerability reporting

See [SECURITY.md](../SECURITY.md).

## 8. What would change this model

- Multi-user or remote access \u2192 the model breaks; don't do it without a
  redesign.
- `safe_mode` AST allowlist (roadmap P2, opt-in, default off,
  responses carry a `mode` field, docs say "safety net, not a
  boundary").
