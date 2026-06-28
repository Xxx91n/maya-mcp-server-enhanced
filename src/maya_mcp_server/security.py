"""Security utilities for maya-mcp-server.

Provides input validation, rate limiting, and security checks
for MCP tool inputs before they reach Maya execution.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)

# Maximum code size (1MB) to prevent memory exhaustion
MAX_CODE_SIZE = 1_048_576

# Maximum module name length
MAX_MODULE_NAME_LENGTH = 256

# Dangerous patterns that should be flagged (not blocked, as exec is core functionality)
DANGEROUS_PATTERNS = [
    (r"__import__\s*\(\s*['\"]subprocess['\"]", "subprocess import detected"),
    (r"__import__\s*\(\s*['\"]os['\"]", "os module import via __import__"),
    (r"os\.(system|popen|exec|spawn)", "os command execution"),
    (r"subprocess\.(run|call|Popen|check_output|check_call)", "subprocess execution"),
    (r"eval\s*\(", "eval() usage"),
    (r"exec\s*\(", "exec() usage"),
    (r"__builtins__", "builtins access"),
    (r"open\s*\(.+['\"]w['\"]", "file write operation"),
    (r"shutil\.(rmtree|move|copy)", "filesystem operations"),
]

# Module name validation pattern (Python identifier with dots)
MODULE_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$")

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60.0  # seconds
RATE_LIMIT_MAX_CALLS = 100  # max calls per window per session


@dataclass
class SecurityConfig:
    """Security configuration for the MCP server."""

    max_code_size: int = MAX_CODE_SIZE
    max_module_name_length: int = MAX_MODULE_NAME_LENGTH
    enable_dangerous_pattern_warning: bool = True
    block_dangerous_patterns: bool = False
    allow_remote_connections: bool = False
    rate_limit_enabled: bool = True
    rate_limit_window: float = RATE_LIMIT_WINDOW
    rate_limit_max_calls: int = RATE_LIMIT_MAX_CALLS


@dataclass
class RateLimiter:
    """Token bucket rate limiter per session."""

    window: float = RATE_LIMIT_WINDOW
    max_calls: int = RATE_LIMIT_MAX_CALLS
    _calls: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def check(self, session_key: str) -> bool:
        """Check if a call is allowed for the given session.

        Returns:
            True if allowed, False if rate limited
        """
        now = time.monotonic()
        calls = self._calls[session_key]

        # Remove old calls outside the window
        cutoff = now - self.window
        self._calls[session_key] = [t for t in calls if t > cutoff]

        if len(self._calls[session_key]) >= self.max_calls:
            logger.warning(
                f"Rate limit exceeded for session {session_key}: "
                f"{len(self._calls[session_key])} calls in {self.window}s"
            )
            return False

        self._calls[session_key].append(now)
        return True

    def get_remaining(self, session_key: str) -> int:
        """Get remaining calls in the current window."""
        now = time.monotonic()
        cutoff = now - self.window
        active = sum(1 for t in self._calls[session_key] if t > cutoff)
        return max(0, self.max_calls - active)


class InputValidationError(Exception):
    """Raised when input validation fails."""

    pass


def validate_code_size(code: str, max_size: int = MAX_CODE_SIZE) -> None:
    """Validate that code does not exceed maximum size.

    Args:
        code: Python code string to validate
        max_size: Maximum allowed size in bytes

    Raises:
        InputValidationError: If code exceeds max size
    """
    size = len(code.encode("utf-8"))
    if size > max_size:
        raise InputValidationError(
            f"Code size ({size:,} bytes) exceeds maximum allowed ({max_size:,} bytes)"
        )


def validate_module_name(name: str) -> None:
    """Validate module name format and length.

    Args:
        name: Module name to validate

    Raises:
        InputValidationError: If name is invalid
    """
    if not name:
        raise InputValidationError("Module name cannot be empty")

    if len(name) > MAX_MODULE_NAME_LENGTH:
        raise InputValidationError(
            f"Module name length ({len(name)}) exceeds maximum ({MAX_MODULE_NAME_LENGTH})"
        )

    if not MODULE_NAME_PATTERN.match(name):
        raise InputValidationError(
            f"Invalid module name '{name}': must be a valid Python dotted identifier "
            f"(e.g., 'mypackage.mymodule')"
        )


def validate_session_key(session_key: str | None) -> str | None:
    """Validate session key format.

    Args:
        session_key: Session key to validate (host:port format)

    Returns:
        Validated session key or None

    Raises:
        InputValidationError: If format is invalid
    """
    if session_key is None:
        return None

    if not isinstance(session_key, str):
        raise InputValidationError("Session key must be a string")

    # Validate format: host:port
    parts = session_key.rsplit(":", 1)
    if len(parts) != 2:
        raise InputValidationError(
            f"Invalid session key format '{session_key}': expected 'host:port'"
        )

    host, port_str = parts
    try:
        port = int(port_str)
        if not (0 < port < 65536):
            raise ValueError
    except ValueError:
        raise InputValidationError(
            f"Invalid port in session key '{session_key}': must be 1-65535"
        )

    return session_key


def scan_for_dangerous_patterns(code: str) -> list[str]:
    """Scan code for potentially dangerous patterns.

    This does NOT block execution - it generates warnings for logging/auditing.

    Args:
        code: Python code to scan

    Returns:
        List of warning messages for detected patterns
    """
    warnings = []
    for pattern, message in DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            warnings.append(message)
    return warnings


def compute_code_hash(code: str) -> str:
    """Compute SHA-256 hash of code for audit logging.

    Args:
        code: Python code to hash

    Returns:
        Hex digest of SHA-256 hash
    """
    return hashlib.sha256(code.encode("utf-8")).hexdigest()[:32]


def sanitize_error_message(message: str) -> str:
    """Sanitize error messages to avoid leaking internal paths.

    Args:
        message: Original error message

    Returns:
        Sanitized error message
    """
    # Remove absolute paths that might leak user information
    import re
    # Match Windows paths
    sanitized = re.sub(r'[A-Z]:\\(?:[^\\]+\\)+', '...\\\\', message)
    # Match Unix paths
    sanitized = re.sub(r'/home/[^/]+/', '/.../', sanitized)
    sanitized = re.sub(r'/Users/[^/]+/', '/.../', sanitized)
    return sanitized
