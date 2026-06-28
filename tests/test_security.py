"""Tests for security module."""

from __future__ import annotations

import pytest

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


class TestValidateCodeSize:
    """Test code size validation."""

    def test_valid_code(self) -> None:
        """Test that normal code passes validation."""
        validate_code_size("print('hello')")

    def test_empty_code(self) -> None:
        """Test that empty code passes validation."""
        validate_code_size("")

    def test_large_code_raises(self) -> None:
        """Test that code exceeding max size raises error."""
        large_code = "x = 1\n" * 200_000
        with pytest.raises(InputValidationError, match="exceeds maximum"):
            validate_code_size(large_code, max_size=1000)

    def test_custom_max_size(self) -> None:
        """Test custom max size parameter."""
        with pytest.raises(InputValidationError):
            validate_code_size("x" * 101, max_size=100)


class TestValidateModuleName:
    """Test module name validation."""

    def test_valid_simple_name(self) -> None:
        """Test simple valid module name."""
        validate_module_name("mytools")

    def test_valid_dotted_name(self) -> None:
        """Test dotted module name."""
        validate_module_name("mypackage.mymodule")

    def test_valid_deep_dotted_name(self) -> None:
        """Test deeply dotted module name."""
        validate_module_name("a.b.c.d")

    def test_empty_name_raises(self) -> None:
        """Test that empty name raises error."""
        with pytest.raises(InputValidationError, match="cannot be empty"):
            validate_module_name("")

    def test_invalid_name_raises(self) -> None:
        """Test that invalid name raises error."""
        with pytest.raises(InputValidationError, match="Invalid module name"):
            validate_module_name("my-module")

    def test_name_starting_with_digit_raises(self) -> None:
        """Test that name starting with digit raises error."""
        with pytest.raises(InputValidationError, match="Invalid module name"):
            validate_module_name("1module")

    def test_long_name_raises(self) -> None:
        """Test that excessively long name raises error."""
        with pytest.raises(InputValidationError, match="exceeds maximum"):
            validate_module_name("a" * 300)


class TestValidateSessionKey:
    """Test session key validation."""

    def test_none_key(self) -> None:
        """Test that None is valid (auto-select)."""
        assert validate_session_key(None) is None

    def test_valid_key(self) -> None:
        """Test valid session key."""
        assert validate_session_key("127.0.0.1:50000") == "127.0.0.1:50000"

    def test_localhost_key(self) -> None:
        """Test localhost key."""
        assert validate_session_key("localhost:7001") == "localhost:7001"

    def test_invalid_format_raises(self) -> None:
        """Test invalid format raises error."""
        with pytest.raises(InputValidationError, match="Invalid session key"):
            validate_session_key("no-port")

    def test_invalid_port_raises(self) -> None:
        """Test invalid port raises error."""
        with pytest.raises(InputValidationError, match="Invalid port"):
            validate_session_key("host:99999")

    def test_non_string_raises(self) -> None:
        """Test non-string raises error."""
        with pytest.raises(InputValidationError, match="must be a string"):
            validate_session_key(12345)


class TestScanForDangerousPatterns:
    """Test dangerous pattern scanning."""

    def test_safe_code(self) -> None:
        """Test that safe code produces no warnings."""
        warnings = scan_for_dangerous_patterns("import maya.cmds as cmds; cmds.ls()")
        assert len(warnings) == 0

    def test_subprocess_import(self) -> None:
        """Test detection of subprocess import."""
        warnings = scan_for_dangerous_patterns('__import__("subprocess")')
        assert any("subprocess" in w for w in warnings)

    def test_os_system(self) -> None:
        """Test detection of os.system."""
        warnings = scan_for_dangerous_patterns("os.system('ls')")
        assert any("os command" in w for w in warnings)

    def test_eval_usage(self) -> None:
        """Test detection of eval."""
        warnings = scan_for_dangerous_patterns("eval('1+1')")
        assert any("eval" in w for w in warnings)


class TestComputeCodeHash:
    """Test code hashing."""

    def test_deterministic(self) -> None:
        """Test that hash is deterministic."""
        assert compute_code_hash("test") == compute_code_hash("test")

    def test_different_code_different_hash(self) -> None:
        """Test that different code produces different hash."""
        assert compute_code_hash("a") != compute_code_hash("b")

    def test_hash_length(self) -> None:
        """Test hash length."""
        assert len(compute_code_hash("test")) == 32


class TestSanitizeErrorMessage:
    """Test error message sanitization."""

    def test_windows_path(self) -> None:
        """Test Windows path sanitization."""
        msg = "Error at C:\\Users\\admin\\project\\file.py"
        sanitized = sanitize_error_message(msg)
        assert "C:\\Users\\admin" not in sanitized

    def test_unix_path(self) -> None:
        """Test Unix path sanitization."""
        msg = "Error at /home/user/project/file.py"
        sanitized = sanitize_error_message(msg)
        assert "/home/user/" not in sanitized

    def test_no_path(self) -> None:
        """Test message without path."""
        msg = "Some error message"
        assert sanitize_error_message(msg) == msg


class TestRateLimiter:
    """Test rate limiter."""

    def test_allows_within_limit(self) -> None:
        """Test that calls within limit are allowed."""
        limiter = RateLimiter(max_calls=5, window=60.0)
        for _ in range(5):
            assert limiter.check("session1") is True

    def test_blocks_over_limit(self) -> None:
        """Test that calls over limit are blocked."""
        limiter = RateLimiter(max_calls=3, window=60.0)
        for _ in range(3):
            assert limiter.check("session1") is True
        assert limiter.check("session1") is False

    def test_separate_sessions(self) -> None:
        """Test that different sessions have separate limits."""
        limiter = RateLimiter(max_calls=2, window=60.0)
        assert limiter.check("session1") is True
        assert limiter.check("session1") is True
        assert limiter.check("session1") is False
        # Different session should still be allowed
        assert limiter.check("session2") is True

    def test_get_remaining(self) -> None:
        """Test remaining count."""
        limiter = RateLimiter(max_calls=5, window=60.0)
        assert limiter.get_remaining("session1") == 5
        limiter.check("session1")
        assert limiter.get_remaining("session1") == 4
