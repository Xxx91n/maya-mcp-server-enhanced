"""Tests for connection_guide module."""

from __future__ import annotations

import platform
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from maya_mcp_server.connection_guide import (
    DEFAULT_COMMAND_PORT,
    MayaInstallInfo,
    _get_platform,
    find_maya_installations,
    generate_user_setup_content,
    get_agent_connection_instructions,
    get_connection_diagnostics,
    get_fallback_instructions,
    install_user_setup,
    uninstall_user_setup,
)


class TestPlatformDetection:
    """Test platform detection functions."""

    def test_get_platform_returns_string(self):
        result = _get_platform()
        assert isinstance(result, str)
        assert result in ("windows", "linux", "macos", platform.system().lower())

    @patch("maya_mcp_server.connection_guide.platform")
    def test_get_platform_windows(self, mock_platform):
        mock_platform.system.return_value = "Windows"
        assert _get_platform() == "windows"

    @patch("maya_mcp_server.connection_guide.platform")
    def test_get_platform_linux(self, mock_platform):
        mock_platform.system.return_value = "Linux"
        assert _get_platform() == "linux"

    @patch("maya_mcp_server.connection_guide.platform")
    def test_get_platform_macos(self, mock_platform):
        mock_platform.system.return_value = "Darwin"
        assert _get_platform() == "macos"


class TestUserSetupGeneration:
    """Test userSetup.py content generation."""

    def test_generates_valid_python(self):
        content = generate_user_setup_content(7001)
        assert "import maya.cmds as cmds" in content
        assert "7001" in content
        assert "_open_command_port" in content
        assert "commandPort" in content

    def test_custom_port(self):
        content = generate_user_setup_content(9999)
        assert "9999" in content
        assert "7001" not in content

    def test_default_port(self):
        content = generate_user_setup_content()
        assert "7001" in content

    def test_contains_eval_deferred(self):
        content = generate_user_setup_content()
        assert "evalDeferred" in content

    def test_contains_fallback(self):
        content = generate_user_setup_content()
        assert "Script Editor" in content or "_open_command_port" in content


class TestFallbackInstructions:
    """Test human-readable fallback instructions."""

    def test_contains_key_sections(self):
        instructions = get_fallback_instructions(7001)
        assert "Script Editor" in instructions
        assert "Python" in instructions
        assert "commandPort" in instructions
        assert "7001" in instructions

    def test_contains_troubleshooting(self):
        instructions = get_fallback_instructions(7001)
        assert "Troubleshooting" in instructions or "排查" in instructions

    def test_custom_port(self):
        instructions = get_fallback_instructions(8888)
        assert "8888" in instructions


class TestConnectionDiagnostics:
    """Test connection diagnostics."""

    def test_returns_dict_structure(self):
        diag = get_connection_diagnostics(7001)
        assert isinstance(diag, dict)
        assert "platform" in diag
        assert "port" in diag
        assert "maya_running" in diag
        assert "port_open" in diag
        assert "issues" in diag
        assert "suggestions" in diag
        assert "user_setup_found" in diag

    def test_port_value(self):
        diag = get_connection_diagnostics(9999)
        assert diag["port"] == 9999


class TestAgentInstructions:
    """Test agent-facing connection instructions."""

    def test_contains_diagnostics(self):
        instructions = get_agent_connection_instructions(7001)
        assert "7001" in instructions
        assert "Maya" in instructions

    def test_contains_platform_info(self):
        instructions = get_agent_connection_instructions(7001)
        current = _get_platform()
        assert current in instructions


class TestInstallUninstall:
    """Test install and uninstall userSetup.py."""

    def test_install_dry_run(self):
        result = install_user_setup(port=7001, dry_run=True)
        assert isinstance(result, dict)
        assert "success" in result

    def test_install_no_maya_found(self, tmp_path):
        with patch("maya_mcp_server.connection_guide.find_maya_installations", return_value=[]):
            result = install_user_setup(port=7001)
            assert result["success"] is False
            assert "error" in result

    def test_install_creates_file(self, tmp_path):
        scripts_dir = tmp_path / "2024" / "scripts"
        scripts_dir.mkdir(parents=True)
        fake_install = MayaInstallInfo(
            version="2024",
            scripts_dir=scripts_dir,
            user_setup_path=scripts_dir / "userSetup.py",
            platform="windows",
            maya_app_dir=str(tmp_path),
            is_valid=True,
            notes=["test"],
        )
        with patch("maya_mcp_server.connection_guide.find_maya_installations", return_value=[fake_install]):
            result = install_user_setup(port=7001)
            assert result["success"] is True
            assert (scripts_dir / "userSetup.py").exists()
            content = (scripts_dir / "userSetup.py").read_text()
            assert "7001" in content

    def test_install_backup_existing(self, tmp_path):
        scripts_dir = tmp_path / "2024" / "scripts"
        scripts_dir.mkdir(parents=True)
        existing = scripts_dir / "userSetup.py"
        existing.write_text("# old content", encoding="utf-8")
        fake_install = MayaInstallInfo(
            version="2024",
            scripts_dir=scripts_dir,
            user_setup_path=existing,
            platform="windows",
            maya_app_dir=str(tmp_path),
            is_valid=True,
            notes=["test"],
        )
        with patch("maya_mcp_server.connection_guide.find_maya_installations", return_value=[fake_install]):
            result = install_user_setup(port=7001)
            assert result["success"] is True
            assert (scripts_dir / "userSetup.py.bak").exists()
            assert (scripts_dir / "userSetup.py.bak").read_text() == "# old content"

    def test_uninstall_no_files(self, tmp_path):
        scripts_dir = tmp_path / "2024" / "scripts"
        scripts_dir.mkdir(parents=True)
        fake_install = MayaInstallInfo(
            version="2024",
            scripts_dir=scripts_dir,
            user_setup_path=scripts_dir / "userSetup.py",
            platform="windows",
            maya_app_dir=str(tmp_path),
            is_valid=True,
            notes=["test"],
        )
        with patch("maya_mcp_server.connection_guide.find_maya_installations", return_value=[fake_install]):
            result = uninstall_user_setup(port=7001)
            assert result["results"][0]["action"] == "not_found"

    def test_uninstall_removes_file(self, tmp_path):
        scripts_dir = tmp_path / "2024" / "scripts"
        scripts_dir.mkdir(parents=True)
        target = scripts_dir / "userSetup.py"
        target.write_text("# to remove", encoding="utf-8")
        fake_install = MayaInstallInfo(
            version="2024",
            scripts_dir=scripts_dir,
            user_setup_path=target,
            platform="windows",
            maya_app_dir=str(tmp_path),
            is_valid=True,
            notes=["test"],
        )
        with patch("maya_mcp_server.connection_guide.find_maya_installations", return_value=[fake_install]):
            result = uninstall_user_setup(port=7001)
            assert result["success"] is True
            assert not target.exists()


class TestFindMayaInstallations:
    """Test Maya installation detection."""

    @patch("maya_mcp_server.connection_guide._get_platform", return_value="linux")
    @patch("maya_mcp_server.connection_guide.Path")
    def test_linux_finds_home_maya(self, mock_path_cls, mock_platform, tmp_path):
        scripts_dir = tmp_path / "maya" / "2024" / "scripts"
        scripts_dir.mkdir(parents=True)
        # Patch Path.home() to return tmp_path
        with patch.object(Path, "home", return_value=tmp_path):
            # Need to use real Path for the function to work
            from maya_mcp_server.connection_guide import _find_maya_versions_linux
            results = _find_maya_versions_linux()
            # At least one should be found
            assert len(results) >= 1
