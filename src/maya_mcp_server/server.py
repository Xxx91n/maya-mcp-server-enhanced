"""FastMCP server for Maya integration."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

from maya_mcp_server.client import raise_for_error
from maya_mcp_server.connection_guide import (
    get_agent_connection_instructions,
    get_connection_diagnostics,
    get_fallback_instructions,
    install_user_setup,
    uninstall_user_setup,
)
from maya_mcp_server.scene_tools import mark_dirty, register_scene_tools
from maya_mcp_server.security import (
    InputValidationError,
    RateLimiter,
    SecurityConfig,
    compute_code_hash,
    sanitize_error_message,
    scan_for_dangerous_patterns,
    validate_code_size,
    validate_module_name,
    validate_session_key,
)
from maya_mcp_server.session_manager import SessionManager
from maya_mcp_server.types import ClientType, OutputBuffer, ResultType, SessionInfo


logger = logging.getLogger(__name__)

# Security configuration
_security_config = SecurityConfig()
_rate_limiter = RateLimiter()

# Initialize FastMCP server with instructions for cross-tool workflows
mcp = FastMCP(
    "Maya MCP Server",
    instructions=(
        "This server provides tools to interact with Autodesk Maya 3D sessions.\n\n"
        "## Connection & Setup\n"
        "- maya_setup_guide: Diagnose connection, install userSetup.py, get fallback instructions\n"
        "  Actions: diagnose | install | guide | uninstall\n"
        "  Use when list_sessions returns empty or on first-time setup.\n\n"
        "## Spatial Awareness (ICEV Workflow)\n"
        "1. INSPECT: scene_snapshot() for spatial overview\n"
        "2. COMPUTE: Use spatial data to plan changes\n"
        "3. EXECUTE: execute_code() to apply changes\n"
        "4. VERIFY: scene_assert() to confirm results\n\n"
        "## Scene Tools\n"
        "- scene_snapshot: Full scene spatial overview\n"
        "- scene_inspect: Deep inspection of object/zone\n"
        "- scene_measure: Distance/clearance between objects\n"
        "- scene_assert: Verify scene state\n\n"
        "## Constraint & Safety Tools\n"
        "- scene_validate: Check spatial constraints (clearance, overlap, height)\n"
        "- scene_checkpoint: Save scene checkpoint before risky ops\n"
        "- scene_checkpoint_list: List saved checkpoints\n"
        "- scene_rollback: Rollback to checkpoint\n\n"
        "## Camera & Shot Tools\n"
        "- camera_create: Create camera with shot type (wide/medium/close/etc)\n"
        "- camera_orbit: Create orbiting camera with animation\n\n"
        "## Aesthetic Analysis (5 Professional Dimensions)\n"
        "- scene_aesthetics: Professional-grade analysis with 5 dimensions:\n"
        "  1. Color Theory: 60-30-10 rule, temperature, harmony, saturation, contrast\n"
        "  2. Spatial Composition: golden ratio, rule-of-thirds, visual weight balance\n"
        "  3. Proportion & Scale: human ergonomics, size hierarchy (hero/secondary/tertiary)\n"
        "  4. Lighting Quality: layer composition, color temperature consistency\n"
        "  5. Visual Flow: sight lines, circulation clarity, visual rhythm\n"
        "  Returns: overall score (0-100), grade (S/A/B/C/D/F), improvement suggestions\n"
        "- scene_review: Comprehensive audit after operations (score 0-100)\n"
        "  Checks: spatial, overlaps, zones, aesthetics, constraints, orphans, naming,\n"
        "  components, conflicts, lighting, organization\n\n"
        "## Scene Planning\n"
        "- scene_plan: Holistic scene planning with organization validation,\n"
        "  layout optimization, conflict prevention\n\n"
        "## General Tools\n"
        "- list_sessions: Discover active Maya sessions\n"
        "  (if empty, call maya_setup_guide for connection help)\n"
        "- write_module: Define reusable Python functions\n"
        "- execute_code: Run Python code in Maya\n\n"
        "Best practices:\n"
        "- Call scene_snapshot() before modifications\n"
        "- Use scene_checkpoint() before risky operations\n"
        "- Use scene_validate() to check constraints after changes\n"
        "- Cache auto-invalidates after execute_code/write_module"
    ),
)

# Register scene tools on the MCP instance
register_scene_tools(mcp)

# Global session manager - initialized when server starts
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get the global session manager."""
    if _session_manager is None:
        raise RuntimeError("Session manager not initialized. Server not started.")
    return _session_manager


def _check_rate_limit(session_key: str | None) -> None:
    """Check rate limit for a session. Raises if exceeded."""
    if not _security_config.rate_limit_enabled:
        return
    key = session_key or "_default"
    if not _rate_limiter.check(key):
        raise InputValidationError(
            f"Rate limit exceeded for session. "
            f"Max {_security_config.rate_limit_max_calls} calls per "
            f"{_security_config.rate_limit_window}s window."
        )


# MCP Tools


@mcp.tool
async def list_sessions() -> list[SessionInfo]:
    """
    List all active Maya sessions.

    Returns a list of session information including:
    - session_key: Session key used to interact with tools and resources
    - host: Session host address
    - port: Session port number
    - pid: Maya process ID
    - user: Logged-in user
    - maya_version: Maya version string
    - scene_name: Current scene filename
    - scene_path: Full path to current scene

    Note: To detect new or removed sessions, clients should call this tool
    periodically (e.g., every 10-30 seconds) and compare results. The SessionManager
    automatically scans for new Maya sessions in the background.

    If this returns an empty list, call maya_setup_guide() for connection help.
    """
    manager = get_session_manager()
    sessions = await manager.list_sessions()
    if not sessions:
        logger.info(
            "No Maya sessions found. Call maya_setup_guide() for connection help."
        )
    return sessions


@mcp.tool
async def maya_setup_guide(
    action: str = "diagnose",
    port: int = 7001,
    target_version: str | None = None,
) -> dict[str, Any]:
    """
    Maya connection setup guide and diagnostics.

    Use this tool when list_sessions returns empty or when setting up
    Maya MCP for the first time. Provides platform-aware diagnostics,
    auto-installation of userSetup.py, and step-by-step fallback instructions.

    Args:
        action: What to do:
            - "diagnose": Run connection diagnostics and return status
            - "install": Auto-install userSetup.py to Maya scripts dirs
            - "guide": Get full step-by-step connection guide
            - "uninstall": Remove installed userSetup.py
        port: Maya command port number (default: 7001)
        target_version: Specific Maya version (e.g., "2024").
            If None, targets all detected versions.

    Returns:
        Dict with diagnostics, installation results, or guide text

    Typical workflow:
        1. Call maya_setup_guide(action="diagnose") to check status
        2. If port not open, call maya_setup_guide(action="install")
        3. Restart Maya, then call list_sessions() again
        4. If still failing, follow the guide from action="guide"
    """
    if action == "diagnose":
        return get_connection_diagnostics(port)
    elif action == "install":
        return install_user_setup(port=port, target_version=target_version)
    elif action == "guide":
        return {
            "guide": get_fallback_instructions(port),
            "diagnostics": get_connection_diagnostics(port),
            "agent_instructions": get_agent_connection_instructions(port),
        }
    elif action == "uninstall":
        return uninstall_user_setup(port=port, target_version=target_version)
    else:
        raise InputValidationError(
            f"Invalid action '{action}': must be diagnose, install, guide, or uninstall"
        )


@mcp.tool
async def write_module(
    name: str,
    code: str,
    overwrite: bool = False,
    session_key: str | None = None,
) -> str:
    """
    Create a virtual Python module in a Maya session.

    Args:
        name: Module name. Can be a dotted path (e.g., 'mypackage.utils')
              in which case parent packages are created automatically.
        code: Python source code for the module.
        overwrite: If True, replace existing module. If False, raise error
                   if module already exists.
        session_key: Session key (optional if only one session exists)

    Returns:
        Success message

    Example:
        write_module("mytools", '''
        import maya.cmds as cmds

        def create_cube(name="cube1"):
            return cmds.polyCube(name=name)[0]
        ''')

        # Then use it:
        execute_code("import mytools; mytools.create_cube('myCube')")
    """
    # Input validation
    validate_module_name(name)
    validate_code_size(code)
    validate_session_key(session_key)

    # Audit logging
    code_hash = compute_code_hash(code)
    logger.info(f"write_module: name={name}, hash={code_hash}, overwrite={overwrite}")

    # Check for dangerous patterns
    if (
        _security_config.enable_dangerous_pattern_warning
        or _security_config.block_dangerous_patterns
    ):
        warnings = scan_for_dangerous_patterns(code)
        if warnings:
            if _security_config.block_dangerous_patterns:
                raise InputValidationError(
                    f"Module '{name}' blocked: contains dangerous patterns: {', '.join(warnings)}"
                )
            logger.warning(f"write_module '{name}' contains: {', '.join(warnings)}")

    manager = get_session_manager()
    client = await manager.get_client(session_key)

    result = await client.write_module(name, code, overwrite)

    # Mark scene cache dirty after module write
    mark_dirty(session_key)

    return result


@mcp.tool
async def execute_code(
    code: str,
    result_type: str = "NONE",
    session_key: str | None = None,
) -> Any:
    """
    Execute Python code in a Maya session.

    Args:
        code: Python code to execute.
        result_type: How to handle the result:
            - "NONE": Execute statements, don't capture result
            - "JSON": Evaluate expression, JSON encode result
            - "RAW": Evaluate expression, return string representation
        session_key: Session key (optional if only one session exists)

    Returns:
        Captured result (None if result_type is NONE)

    Note: stdout and stderr are captured and exposed via the
    maya://sessions/{session_key}/output MCP Resource.

    Example:
        # Execute statements
        execute_code("import maya.cmds as cmds; cmds.polyCube()")

        # Get JSON result
        execute_code("cmds.ls(type='mesh')", result_type="JSON")
    """
    # Input validation
    validate_code_size(code)
    validate_session_key(session_key)

    # Validate result_type
    try:
        rt = ResultType(result_type)
    except ValueError:
        raise InputValidationError(
            f"Invalid result_type '{result_type}': must be NONE, JSON, or RAW"
        )

    # Rate limiting
    _check_rate_limit(session_key)

    # Audit logging
    code_hash = compute_code_hash(code)
    logger.info(
        f"execute_code: hash={code_hash}, result_type={result_type}, "
        f"session={session_key or 'auto'}"
    )

    # Check for dangerous patterns
    if (
        _security_config.enable_dangerous_pattern_warning
        or _security_config.block_dangerous_patterns
    ):
        warnings = scan_for_dangerous_patterns(code)
        if warnings:
            if _security_config.block_dangerous_patterns:
                raise InputValidationError(
                    f"Code blocked: contains dangerous patterns: {', '.join(warnings)}"
                )
            logger.warning(f"execute_code [{code_hash}]: {', '.join(warnings)}")

    manager = get_session_manager()
    client = await manager.get_client(session_key)

    try:
        result = await client.execute_code(code, rt)
    except Exception as e:
        # Sanitize error messages to avoid leaking internal paths
        raise type(e)(sanitize_error_message(str(e))) from e

    # Fetch any buffered output and store it in the client
    try:
        output = await client.get_buffered_output()
        client.append_output(output.stdout, output.stderr)
    except Exception as e:
        logger.debug(f"Failed to get buffered output: {e}")

    # Mark scene cache dirty after code execution
    mark_dirty(session_key)

    # Surface Maya-side execution errors instead of silently dropping them
    raise_for_error(result)

    return result.result


@mcp.tool
async def add_session(host: str = "127.0.0.1", port: int = 7002) -> SessionInfo:
    """
    Manually add a Maya session at a specific host and port.

    Use this when auto-discovery doesn't find your Maya session,
    or to connect to a Maya instance on a specific port.

    Args:
        host: The session host (default: "127.0.0.1")
        port: The session port number (default: 7002)

    Returns:
        Session information for the added session

    Before using this, ensure Maya has a Python command port open.
    In Maya's Script Editor (Python), run:
        import maya.cmds as cmds
        cmds.commandPort(name=':7002', sourceType='python')
    """
    # Validate port range
    if not (1 < port < 65536):
        raise InputValidationError(f"Invalid port {port}: must be 1-65535")

    # Block non-localhost connections by default
    if host not in ("127.0.0.1", "localhost", "::1"):
        if not _security_config.allow_remote_connections:
            raise InputValidationError(
                f"Remote connection to {host} blocked for security. "
                "Set SecurityConfig.allow_remote_connections=True to enable."
            )
        logger.warning(f"Adding non-localhost session: {host}:{port}")

    manager = get_session_manager()
    client = await manager.add_session(host, port)
    return await client.session_info()


# MCP Resources


@mcp.resource("maya://sessions/{session_key}/info")
async def session_info(session_key: str) -> SessionInfo:
    """
    Get information about a Maya session.

    Args:
        session_key: Session key

    Returns:
        SessionInfo with session details (pid, user, maya_version, scene)
    """
    validate_session_key(session_key)
    manager = get_session_manager()
    client = await manager.get_client(session_key)
    return await client.session_info()


@mcp.resource("maya://sessions/{session_key}/output")
async def session_output(session_key: str, clear: bool = True) -> OutputBuffer:
    """
    Get captured stdout/stderr output from a Maya session.

    Args:
        clear: If True (default), clear the buffer after reading.
               If False, keep the buffer contents.
        session_key: Session key

    Returns:
        OutputBuffer with stdout and stderr fields containing captured output
        since the last call (or since stream capture was installed).

    This provides access to stdout/stderr that was captured during
    execute_code calls. For real-time streaming, subscribe to the
    MCP Resources instead.
    """
    validate_session_key(session_key)
    manager = get_session_manager()
    client = await manager.get_client(session_key)
    return client.get_accumulated_output(clear=clear)


async def initialize_session_manager(
    scan_interval: float = 10.0,
    client_type: str = "qt",
) -> SessionManager:
    """
    Initialize the global session manager.

    Args:
        scan_interval: Seconds between background scans
        client_type: Type of client to use ("native" or "qt")

    Returns:
        The initialized SessionManager
    """
    global _session_manager

    _session_manager = SessionManager(
        scan_interval=scan_interval,
        client_type=ClientType(client_type),
    )
    await _session_manager.start()

    return _session_manager


async def shutdown_session_manager() -> None:
    """Shutdown the global session manager."""
    global _session_manager

    if _session_manager is not None:
        await _session_manager.stop()
        _session_manager = None
