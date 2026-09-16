"""Pytest fixtures for maya-mcp-server tests."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


# tests/ dir is on sys.path under pytest prepend import mode; be explicit
# so maya_stub also resolves when tests are imported as a package.
sys.path.insert(0, str(Path(__file__).parent))

import maya_stub  # noqa: E402


@pytest.fixture
def mock_port() -> int:
    """Return a port for the mock server."""
    return 17002


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def maya_env():
    """Install the maya stub and import maya_scene_module bound to it.

    Yields a namespace: .scene (stub Scene builder), .module (the
    maya_scene_module under test), .cmds (stub maya.cmds).
    """
    scene = maya_stub.install()
    module = maya_stub.load_scene_module()
    env = SimpleNamespace(
        scene=scene,
        module=module,
        cmds=sys.modules["maya.cmds"],
        om2=sys.modules["maya.api.OpenMaya"],
    )
    yield env
    maya_stub.uninstall()
    sys.modules.pop("maya_mcp_server.maya_scene_module", None)
