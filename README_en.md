# Maya MCP Server

> MCP server giving AI agents spatial awareness for Autodesk Maya

English | [中文](README.md)

## What Is This

`maya-mcp-server` is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that enables LLMs (Codex, Claude, etc.) to directly control Autodesk Maya for 3D modeling, scene planning, and engineering-grade project delivery.

**Key capability:** The AI can "see" the Maya scene — spatial state, material distribution, object relationships — and perform intelligent auditing based on engineering standards.

## Capability Matrix

| Capability | Tools | Description |
|------------|-------|-------------|
| 🧊 **Spatial Awareness** | `scene_snapshot` `scene_inspect` `scene_measure` | One-call full scene spatial model, precise distance/overlap/gap measurement |
| 🎨 **Aesthetic Analysis** | `scene_aesthetics` | 5-dimension professional analysis: Color Theory (60-30-10), Spatial Composition (golden ratio/rule of thirds), Proportion & Scale (human ergonomics), Lighting Quality (3-point setup, fill ratio, shadow quality, illuminance distribution, color temperature grading, decay rate), Visual Flow |
| 🎬 **Camera Planning** | `camera_create` `camera_orbit` | 8 industry-standard shot types + orbit animation |
| 🛡️ **Disaster Recovery** | `scene_checkpoint` `scene_rollback` | Pre-operation snapshots, auto-rollback on failure |
| 🧠 **Scene Planning** | scene_plan | Holistic organization health, zone balance, layout optimization, conflict prevention, NL planning |
| 📋 **Engineering Audit** | `scene_review` `scene_validate` | 11-dimension audit (0-100 score): spatial/overlaps/zones/5D-aesthetics/constraints/orphans/naming/componentization/conflicts/lighting/organization |
| ⚡ **Code Execution** | `execute_code` `write_module` | Execute arbitrary Python code in Maya |

## Quick Start

### 1. Install

```bash
pip install maya-mcp-server

# Or from source
git clone https://github.com/Xxx91n/maya-mcp-server-enhanced.git
cd maya-mcp-server-enhanced
pip install -e .
```

### 2. Configure Maya

Execute in Maya's Script Editor:
```python
import maya.cmds as cmds
cmds.commandPort(name=':7001', sourceType='python')
```

### 3. Configure MCP Client

Add to Codex `~/.codex/config.toml`:

```toml
[mcp_servers.maya_mcp]
command = "python"
args = ["-m", "maya_mcp_server"]
tool_timeout_sec = 120

[mcp_servers.maya_mcp.env]
PYTHONPATH = "/path/to/maya-mcp-server/src"
```

### 4. Start Using

Talk to Codex naturally:
> "Look at what's in my Maya scene, then create a display shelf at the entrance"

The AI automatically calls `scene_snapshot()` → understands the scene → models → `scene_review()` audits.

## Workflow: ICEV Cycle

Every scene modification follows **ICEV**:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ INSPECT  │ ──→ │ COMPUTE  │ ──→ │ EXECUTE  │ ──→ │ VERIFY   │
│ snapshot │     │ calculate │     │ apply    │     │ audit    │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

## Tools Reference

### Spatial Awareness

```python
scene_snapshot(detail="compact", format="cos")  # Full scene overview
scene_inspect(target="wall_entrance")            # Deep object inspection
scene_measure(obj_a="wall", obj_b="shelf", mode="clearance")  # Precise distance
scene_assert(expectations='{"wall": {"exists": true}}')  # Verify state
```

### Engineering Audit

```python
scene_review()  # 9-dimension audit, returns 0-100 score
scene_validate(rules='[{"type": "min_clearance", "value": 180}]')
```

### Camera Planning

```python
camera_create(target="display", shot_type="medium", azimuth=30, elevation=15)
camera_orbit(center=[0, 100, 0], radius=500, frames=120)
```

### Disaster Recovery

```python
scene_checkpoint(name="before_change")
scene_checkpoint_list()
scene_rollback(filename="cp_20260629_120000_before_change.ma")
```

## CoS Format

Default output uses **Chain-of-Symbol** notation, saving **65% tokens** vs JSON:

```
SCENE[164obj, 5zones] UNIT=cm UP=y
shell (23obj) @(-11.8,178.8,145.7)
  GRP_floor[mesh]@(0,0,0) 1121.5x20x1530.5
```

## Codex Skills

4 companion skills in `~/.codex/skills/`:

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `maya-architect` | Spatial layout + ICEV workflow | User describes spatial needs |
| `maya-camera` | Camera planning + animation | User needs cameras/motion |
| `maya-aesthetics` | Color/balance/focus analysis | User cares about visuals |
| `maya-safety` | Checkpoints/rollback/constraints | High-risk operations |

## Architecture

```
┌──────────────────────────────────────────┐
│           LLM Agent (Codex)              │
│  scene_snapshot() → complete spatial model│
│  scene_review() → 9-dimension audit score│
└──────────┬───────────────────────────────┘
           │ 15 MCP tools
┌──────────▼───────────────────────────────┐
│        MCP Server Layer                   │
│  scene_tools.py  → tool definitions       │
│  scene_cache.py  → TTL cache + dirty flag │
│  cos_formatter.py → CoS notation (-65%)   │
│  security.py     → validation + rate limit│
└──────────┬───────────────────────────────┘
           │ execute_code("import _mcp_scene; ...")
┌──────────▼───────────────────────────────┐
│        Maya Side (_mcp_scene module)      │
│  get_scene_graph() → hierarchy + BBox     │
│  get_spatial_index() → spatial index      │
│  scene_review() → 9-dimension audit       │
│  analyze_aesthetics() → color/balance     │
└──────────────────────────────────────────┘
```

## Audit Dimensions

`scene_review()` provides 9 universal audit dimensions:

| Dimension | Score | Checks |
|-----------|-------|--------|
| spatial | 15 | Object/camera/light counts |
| overlaps | 15 | BBox collision detection |
| conflicts | 15 | Penetration detection |
| components | 15 | GRP_ grouping + nesting depth |
| naming | 10 | Maya naming conventions |
| zones | 10 | Zone coverage |
| aesthetics | 10 | Color harmony + balance + focal points |
| constraints | 5 | Safety constraints |
| orphans | 5 | Orphan/empty group detection |

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
semgrep scan --config auto src/
```

## Credits

Based on [chadrik/maya-mcp-server](https://github.com/chadrik/maya-mcp-server) with spatial awareness, camera planning, aesthetic analysis, and scene auditing extensions.

## License

MIT
