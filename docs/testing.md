# Testing Tiers

Two test tiers exist. They are deliberately separate.

## Tier 1 — stub tests (CI-safe, no Maya needed)

```bash
python -m pytest tests/ -q
```

`tests/maya_stub/` provides semantic fakes for `maya.cmds` and
`maya.api.OpenMaya`: a real DAG scene graph, row-major matrix math,
and correct 8-corner world-bbox transforms. The `maya_env` fixture
(conftest.py) installs the stub into `sys.modules` and imports
`maya_scene_module` bound to it.

The stub is NOT a Maya replacement — it models only the cmds/OpenMaya
surface the scene module uses. Its math is self-verified in
`test_maya_stub.py`; if the stub lies, product tests lie, so keep
`math3d.py` honest (row-vector convention, translation in M[12..14]).

## Tier 2 — real Maya via mayapy (manual, local-only, NEVER in CI)

Run the scene module inside a real Maya interpreter to catch stub drift
and real API behavior differences:

```bash
# Point mayapy at the repo so maya_mcp_server + tests import cleanly
set PYTHONPATH=D:\Aworker\maya\maya-mcp-server\src;D:\Aworker\maya\maya-mcp-server\tests
"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" -m pytest tests/ -q -m mayapy
```

Tests marked `@pytest.mark.mayapy` exercise real `maya.cmds`/
`maya.api.OpenMaya` against `maya_scene_module` — they are skipped
unless the `mayapy` marker is explicitly selected. They are the
reference tier: if a stub test and a mayapy test disagree, the stub is
wrong.

For a quick smoke test of the module inside Maya's Script Editor:

```python
import sys; sys.path.insert(0, r"D:\Aworker\maya\maya-mcp-server\src")
import maya_mcp_server.maya_scene_module as _mcp_scene
_mcp_scene.get_scene_graph()
```

## Tier 3 — visual loop, real Maya GUI (manual checklist)

The stub layer is a contract layer — it deliberately never asserts
pixels. The following checks require a real Maya GUI session and are
run by hand (D-027). In Maya's Script Editor:

```python
import sys; sys.path.insert(0, r"D:\Aworker\maya\maya-mcp-server\src")
import maya_mcp_server.visual_module as _mcp_visual
```

- [ ] `viewport_snapshot()` — image orientation is correct (the
      `verticalFlip()` call is validated here; if output is upside
      down, remove the flip).
- [ ] `viewport_snapshot()` — VP2/kFloat path on Maya 2025+ produces a
      non-black image (official patch).
- [ ] `viewport_snapshot()` — captured content actually matches the
      active viewport (HUD/selection visible).
- [ ] `render_preview()` — playblast artifact is produced and decoded;
      `width/height` in metadata match reality.
- [ ] `render_preview(camera="CAM_x")` — panel camera is restored to
      the prior camera after the call (lookThru restore).
- [ ] `render_preview()` — current time is unchanged after the call
      (undo bug #21 restore).
- [ ] `render_preview()` — the `exists` pre-check on the target
      camera behaves correctly against real `cmds.objExists`
      (stub mirrors it; real-Maya acceptance verified here).
- [ ] Batch/mayapy run — `pytest -m mayapy` covers the
      `gui_session_required` gate on a real interpreter.
