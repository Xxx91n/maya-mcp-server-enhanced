# maya-mcp-server

MCP server for interacting with Autodesk Maya sessions with **spatial awareness**, **camera planning**, **aesthetic analysis**, and **scene auditing**.

## Features

### Core
- **Multi-session support**: Manage multiple Maya sessions from a single MCP server
- **Full Python expressiveness**: Execute arbitrary Python code in Maya
- **Streaming output**: Capture stdout/stderr via MCP resources
- **Simple setup**: No Maya modules to install — uses command port bootstrapping
- **Easy installation**: `uvx maya-mcp-server`

### Spatial Awareness (NEW)
- **`scene_snapshot`**: Full scene spatial overview with CoS notation (65% token savings)
- **`scene_inspect`**: Deep inspection of objects/zones with neighbor analysis
- **`scene_measure`**: Precise distance measurement (center/surface/clearance/bbox)
- **`scene_assert`**: Verify scene state matches expectations

### Scene Auditing (NEW)
- **`scene_review`**: Universal 9-dimension audit (0-100 score)
  - Spatial integrity, overlap detection, spatial conflicts, zone coverage
  - Naming conventions, componentization, aesthetics, constraints, orphans

### Camera & Animation (NEW)
- **`camera_create`**: Create cameras with industry-standard shot types (wide/medium/close/bird_eye/etc.)
- **`camera_orbit`**: Create orbiting cameras with keyframe animation

### Safety & Recovery (NEW)
- **`scene_checkpoint`**: Save scene checkpoints before risky operations
- **`scene_checkpoint_list`**: List all saved checkpoints
- **`scene_rollback`**: Rollback to any checkpoint (auto-backup before rollback)
- **`scene_validate`**: Validate spatial constraints (min_clearance/max_objects/no_overlap)

### Aesthetic Analysis (NEW)
- **`scene_aesthetics`**: Color harmony, spatial balance, focal point analysis

## Installation

```bash
# Using uvx (recommended)
uvx maya-mcp-server

# Or pip install
pip install maya-mcp-server
```

## Configuration

Add to your MCP client config (e.g., Codex `~/.codex/config.toml`):

```toml
[mcp_servers.maya_mcp]
command = "python"
args = ["-m", "maya_mcp_server"]
tool_timeout_sec = 120

[mcp_servers.maya_mcp.env]
PYTHONPATH = "/path/to/maya-mcp-server/src"
```

## Usage

### ICEV Workflow (Recommended)

Every scene modification follows the **ICEV** cycle:

1. **INSPECT**: `scene_snapshot()` → understand current state
2. **COMPUTE**: Use spatial data to calculate changes
3. **EXECUTE**: `execute_code()` → apply changes
4. **VERIFY**: `scene_assert()` + `scene_review()` → confirm results

### Example: Create and Verify

```
# 1. Get scene overview
scene_snapshot(detail="compact", format="cos")

# 2. Create objects
execute_code("import maya.cmds as cmds; cmds.polyCube(name='wall', w=300, h=200, d=10)")

# 3. Verify result
scene_assert(expectations='{"wall": {"exists": true}}')

# 4. Full audit
scene_review()
```

### Example: Camera Planning

```
# Create a wide establishing shot
camera_create(target="store_entrance", shot_type="wide", azimuth=30, elevation=15)

# Create orbiting camera for product showcase
camera_orbit(center=[0, 100, 0], radius=500, frames=120, name="product_orbit")
```

### Example: Safety Workflow

```
# Before risky operation
scene_checkpoint(name="before_renovation")

# Make changes...

# Verify
scene_review()
# If issues found:
scene_rollback(filename="cp_20260628_120000_before_renovation.ma")
```

## MCP Tools Reference

| Tool | Description |
|------|-------------|
| `list_sessions` | List active Maya sessions |
| `write_module` | Create virtual Python modules in Maya |
| `execute_code` | Execute Python code in Maya |
| `scene_snapshot` | Full scene spatial overview |
| `scene_inspect` | Deep inspection of object/zone |
| `scene_measure` | Distance measurement (4 modes) |
| `scene_assert` | Verify scene state |
| `scene_review` | Universal 9-dimension audit |
| `scene_validate` | Spatial constraint validation |
| `scene_checkpoint` | Save scene checkpoint |
| `scene_checkpoint_list` | List checkpoints |
| `scene_rollback` | Rollback to checkpoint |
| `camera_create` | Create camera with shot type |
| `camera_orbit` | Create orbiting camera |
| `scene_aesthetics` | Aesthetic analysis |

## Architecture

```
┌─────────────────────────────────────────────┐
│              LLM Agent (Codex)               │
│                                              │
│  scene_snapshot() → complete spatial model   │
│  scene_review() → 9-dimension audit score    │
│  camera_create() → industry-standard shots   │
└──────────┬───────────────────────────────────┘
           │ MCP Tools (15 tools)
┌──────────▼───────────────────────────────────┐
│         MCP Server Layer                      │
│                                               │
│  scene_tools.py → 15 MCP tool definitions     │
│  scene_cache.py → TTL + dirty detection       │
│  cos_formatter.py → CoS notation (65% saving) │
│  security.py → input validation + rate limit  │
└──────────┬───────────────────────────────────┘
           │ execute_code("import _mcp_scene; ...")
┌──────────▼───────────────────────────────────┐
│         Maya Side (_mcp_scene module)          │
│                                               │
│  get_scene_graph() → BBox + Transform + tree  │
│  get_zone_map() → functional zone grouping    │
│  get_spatial_index() → neighbor relationships │
│  measure() → precise distance measurement     │
│  scene_review() → 9-dimension audit           │
│  analyze_aesthetics() → color/balance/focal   │
└───────────────────────────────────────────────┘
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -q

# Run with debug logging
LOGLEVEL=DEBUG python -m maya_mcp_server
```

## Credits

Based on [chadrik/maya-mcp-server](https://github.com/chadrik/maya-mcp-server) with spatial awareness, camera planning, aesthetic analysis, and scene auditing extensions.

## License

MIT
