"""Unified security pipeline (D-018 / ADR-0005).

One FastMCP middleware funnels every tool call through:
    input validation -> rate limit -> pattern scan -> dispatch -> audit.

TOOL_ANNOTATIONS is the single source for each tool's four MCP hints;
the same map drives the read/write rate-limit bucket classification.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

import mcp.types as mt
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

from maya_mcp_server.security import (
    AuditLogger,
    PatternBlockedError,
    PipelineError,
    RateLimiter,
    RateLimitExceededError,
    SecurityConfig,
    build_audit_event,
    scan_tool_params,
    validate_code_size,
    validate_session_key,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool annotations \u2014 the single matrix (D-018). All 18 tools, all four hints.
# readOnlyHint also drives the read/write rate-limit bucket.
# ---------------------------------------------------------------------------

_READ = mt.ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True,
    openWorldHint=False,
)
_WRITE_SAFE = mt.ToolAnnotations(
    readOnlyHint=False, destructiveHint=False, idempotentHint=False,
    openWorldHint=False,
)
_WRITE_DESTRUCTIVE = mt.ToolAnnotations(
    readOnlyHint=False, destructiveHint=True, idempotentHint=False,
    openWorldHint=False,
)

TOOL_ANNOTATIONS: dict[str, mt.ToolAnnotations] = {
    # read-only tools (9)
    "list_sessions": _READ,
    "scene_snapshot": _READ,
    "scene_inspect": _READ,
    "scene_measure": _READ,
    "scene_assert": _READ,
    "scene_validate": _READ,
    "scene_checkpoint_list": _READ,
    "scene_aesthetics": _READ,
    "scene_review": _READ,
    # mutation-class tools: scene/filesystem effects, not destructive (7)
    "scene_checkpoint": _WRITE_SAFE,
    "scene_rollback": _WRITE_SAFE,
    "scene_plan": _WRITE_SAFE,
    "camera_create": _WRITE_SAFE,
    "camera_orbit": _WRITE_SAFE,
    "add_session": _WRITE_SAFE,
    # dangerous tools: arbitrary code execution / startup-file writes (2+1)
    "execute_code": _WRITE_DESTRUCTIVE,
    "write_module": _WRITE_DESTRUCTIVE,
    "maya_setup_guide": _WRITE_DESTRUCTIVE,
}


def tool_annotations(name: str) -> mt.ToolAnnotations:
    """Annotations for a tool; unknown tools default to write-class."""
    return TOOL_ANNOTATIONS.get(name, _WRITE_SAFE)


# ---------------------------------------------------------------------------
# Pipeline middleware
# ---------------------------------------------------------------------------


class SecurityPipeline(Middleware):
    """The single choke point every MCP tool call passes through.

    Rejections (validation/rate-limit/pattern block) raise PipelineError
    -> MCP isError with a [code] prefix (D-019 host layer). Every call \u2014
    success, error, or rejected \u2014 is recorded to the audit JSONL.
    """

    def __init__(
        self,
        config: SecurityConfig | None = None,
        audit: AuditLogger | None = None,
    ) -> None:
        self.config = config or SecurityConfig()
        if audit is not None:
            self.audit: AuditLogger | None = audit
        elif self.config.audit_enabled:
            path = (
                Path(self.config.audit_log_path)
                if self.config.audit_log_path
                else None
            )
            self.audit = AuditLogger(path)
        else:
            self.audit = None
        self._read_limiter = RateLimiter(
            window=self.config.rate_limit_window,
            max_calls=self.config.rate_limit_read_max_calls,
        )
        self._write_limiter = RateLimiter(
            window=self.config.rate_limit_window,
            max_calls=self.config.rate_limit_write_max_calls,
        )

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, Any],
    ) -> Any:
        tool_name = getattr(context.message, "name", "<unknown>")
        args = getattr(context.message, "arguments", None) or {}
        if not isinstance(args, dict):
            args = {}
        session_id = _resolve_session_id(context, args)
        started = time.monotonic()
        outcome = "success"
        warnings: list[dict[str, str]] = []
        try:
            # 1. host-side validation (tool-semantic checks stay in tool bodies)
            if "session_key" in args:
                validate_session_key(args.get("session_key"))
            code_val = args.get("code")
            if isinstance(code_val, str):
                validate_code_size(code_val, self.config.max_code_size)

            # 2. rate limit \u2014 split read/write token buckets, per session
            if self.config.rate_limit_enabled:
                kind = (
                    "read" if tool_annotations(tool_name).readOnlyHint else "write"
                )
                limiter = (
                    self._read_limiter if kind == "read" else self._write_limiter
                )
                if not limiter.check(session_id):
                    wait = limiter.retry_after(session_id)
                    raise RateLimitExceededError(
                        f"{kind}-class rate limit exceeded for session "
                        f"{session_id}; retry in {wait:.1f}s",
                        suggestion="slow down and retry after the bucket refills",
                    )

            # 3. pattern scan \u2014 warn by default; only precise rules block
            if (
                self.config.enable_dangerous_pattern_warning
                or self.config.block_dangerous_patterns
            ):
                warnings, blocked = scan_tool_params(
                    tool_name, args, set(self.config.pattern_exclusions)
                )
                if blocked and not self.config.block_dangerous_patterns:
                    warnings = warnings + blocked
                    blocked = []
                if blocked:
                    hit = blocked[0]
                    raise PatternBlockedError(
                        f"{tool_name}.{hit['param']} blocked by "
                        f"{hit['rule_id']}: {hit['message']}",
                        suggestion=(
                            "rephrase the input without the blocked pattern, "
                            "or tune via a rule_id x tool x param exclusion"
                        ),
                    )

            # 4. dispatch
            result = await call_next(context)
            if _result_is_error(result):
                outcome = "error"
            return result
        except PipelineError:
            outcome = "rejected"
            raise
        except Exception:
            outcome = "error"
            raise
        finally:
            if self.audit is not None:
                duration_ms = (time.monotonic() - started) * 1000.0
                self.audit.record(
                    build_audit_event(
                        session_id=session_id,
                        tool_name=tool_name,
                        params=args,
                        outcome=outcome,
                        duration_ms=duration_ms,
                        warnings=warnings,
                    )
                )


def _resolve_session_id(
    context: MiddlewareContext[Any], args: dict[str, Any]
) -> str:
    """Rate-limit/audit session key: session_key arg, else MCP session id."""
    sk = args.get("session_key")
    if isinstance(sk, str) and sk:
        return sk
    fctx = getattr(context, "fastmcp_context", None)
    sid = getattr(fctx, "session_id", None) if fctx is not None else None
    if isinstance(sid, str) and sid:
        return sid
    return "_default"


def _result_is_error(result: Any) -> bool:
    """Detect domain-level errors inside a successful tool result.

    The two-layer contract (D-019) returns domain failures as
    {"error": {...}} payloads rather than exceptions; for audit purposes
    they count as outcome="error".
    """
    if getattr(result, "isError", False):
        return True
    sc = getattr(result, "structured_content", None)
    if sc is None:
        sc = getattr(result, "structuredContent", None)
    if isinstance(sc, dict) and "error" in sc:
        return True
    content = getattr(result, "content", None)
    items = content if isinstance(content, list) else [content]
    for item in items or []:
        text = getattr(item, "text", None)
        if not isinstance(text, str):
            if isinstance(item, str):
                text = item
            else:
                continue
        try:
            payload = json.loads(text)
        except (ValueError, TypeError):
            continue
        if isinstance(payload, dict) and "error" in payload:
            return True
    return False
