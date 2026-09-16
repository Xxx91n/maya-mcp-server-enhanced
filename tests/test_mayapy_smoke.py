"""Real-Maya smoke tests — mayapy tier only.

Run inside a real Maya interpreter:

    set PYTHONPATH=<repo>\src;<repo>\tests
    mayapy -m pytest tests/ -m mayapy

Under vanilla python (or the stub) these skip — they exist so docs/testing.md
describes a real tier, not a hypothetical one.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mayapy


@pytest.fixture
def real_maya():
    cmds = pytest.importorskip("maya.cmds", reason="requires real Maya (mayapy)")
    f = getattr(cmds, "__file__", "") or ""
    if "maya_stub" in f or "tests" in f.replace("\\", "/"):
        pytest.skip("maya stub is installed — mayapy tier needs a real interpreter")
    return cmds


def test_scene_graph_runs_in_real_maya(real_maya):
    import maya_mcp_server.maya_scene_module as m

    real_maya.polyCube(name="GEO_probe")
    res = m.get_scene_graph("compact")
    assert "stats" in res
    assert res["stats"]["total"] >= 1


def test_measure_roundtrip_in_real_maya(real_maya):
    import maya_mcp_server.maya_scene_module as m

    a = real_maya.polyCube(name="GEO_a")[0]
    b = real_maya.polyCube(name="GEO_b")[0]
    real_maya.move(100, 0, 0, b)
    res = m.measure(a, b, "center")
    assert res["distance"] == pytest.approx(100, abs=0.01)
