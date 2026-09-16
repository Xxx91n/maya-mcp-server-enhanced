# Maya MCP Server

> 让 AI Agent 拥有 Maya 三维空间感知能力的 MCP 服务器

[English](README_en.md) | 中文

## 这是什么

`maya-mcp-server` 是一个 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器，让大语言模型（如 Codex、Claude）能够直接操控 Autodesk Maya，进行三维建模、场景规划和工程级项目落地。

**核心能力：** AI 不再是"闭眼写代码"，而是像有了眼睛一样，能随时感知 Maya 场景的空间状态、材质分布、物体关系，并基于工程规范进行智能审核。

## 能力矩阵

| 能力 | 工具 | 说明 |
|------|------|------|
| 🧊 **空间感知** | `scene_snapshot` `scene_inspect` `scene_measure` | 一次调用获取全场景空间模型，精确距离/重叠/间隙测量 |
| 🎨 **审美分析** | `scene_aesthetics` | 5维专业分析：色彩理论(60-30-10)、空间构成(黄金比例/三分法)、比例尺度(人体工学)、光影质量(三点照明/填充比/阴影质量/照度分布/色温分级/衰减率)、视觉动线 |
| 🎬 **镜头规划** | `camera_create` `camera_orbit` | 8 种行业标准镜头 + 环绕动画 |
| 🛡️ **避灾回退** | `scene_checkpoint` `scene_rollback` | exportAll 内存态快照，回滚重绑原路径 |
| 🧠 **大局观统筹** | scene_plan | 场景组织健康检查、区域平衡分析、布局优化建议、冲突预防、自然语言规划 |
| 📋 **工程审核** | `scene_review` `scene_validate` | 11 维度审核（0-100 分）：空间/重叠/区域/审美5维/约束/孤儿/命名/组件化/冲突/光照质量/场景组织 |
| ⚡ **代码执行** | `execute_code` `write_module` | 在 Maya 中执行任意 Python 代码 |

## 快速开始

### 1. 安装

```bash
# 从 PyPI
pip install maya-mcp-server

# 或从源码
git clone https://github.com/Xxx91n/maya-mcp-server-enhanced.git
cd maya-mcp-server-enhanced
pip install -e .
```

### 2. 配置 Maya 连接

#### 方式一：自动配置（推荐）

启动 MCP 服务器后，AI Agent 会自动调用 `maya_setup_guide` 工具引导连接：

1. 确保 Maya 已启动
2. 在 Codex 中输入任意指令（如"查看 Maya 场景"）
3. 如果未连接，Agent 会自动运行诊断并安装 `userSetup.py`
4. 重启 Maya 后，命令端口自动打开

#### 方式二：手动配置

在 Maya 的脚本编辑器中执行：
```python
import maya.cmds as cmds
cmds.commandPort(name=':7001', sourceType='python')
```

> **提示**: Script Editor 打开方式：Maya 菜单 → Windows → General Editors → Script Editor
> 确保语言选择器显示为 **Python**（不是 MEL）

#### 方式三：永久自动连接

将以下内容保存为 `userSetup.py`，放入 Maya 的 scripts 目录：

| 平台 | 路径 |
|------|------|
| Windows | `%MAYA_APP_DIR%\<version>\scripts\` |
| Linux | `~/maya/<version>/scripts/` |
| macOS | `~/Library/Preferences/Autodesk/maya/<version>/scripts/` |

```python
import maya.cmds as cmds
cmds.evalDeferred('cmds.commandPort(name=":7001", sourceType="python")', lowestPriority=True)
```

#### 故障排查

| 问题 | 解决方案 |
|------|----------|
| `list_sessions` 返回空 | 调用 `maya_setup_guide(action="diagnose")` |
| 端口被占用 | 关闭其他 Maya 实例，或换端口 |
| userSetup.py 不生效 | 确认文件在正确的 scripts 目录，重启 Maya |
| 防火墙拦截 | 确保 localhost:7001 可访问 |

### 3. 配置 MCP 客户端

在 Codex 的 `~/.codex/config.toml` 中添加：

```toml
[mcp_servers.maya_mcp]
command = "python"
args = ["-m", "maya_mcp_server"]
tool_timeout_sec = 120

[mcp_servers.maya_mcp.env]
PYTHONPATH = "/path/to/maya-mcp-server/src"
```

### 4. 开始使用

在 Codex 中直接对话：
> "帮我看看 Maya 场景里有什么，然后在入口处创建一个展示架"

AI 会自动调用 `scene_snapshot()` → 理解场景 → 执行建模 → `scene_review()` 审核结果。

## 工作流：ICEV 循环

每次场景修改都遵循 **ICEV** 工作流：

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ INSPECT  │ ──→ │ COMPUTE  │ ──→ │ EXECUTE  │ ──→ │ VERIFY   │
│ 场景快照  │     │ 计算规划  │     │ 执行修改  │     │ 审核验证  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

1. **INSPECT**：`scene_snapshot()` 获取全场景空间数据
2. **COMPUTE**：基于空间数据计算位置、尺寸、间距
3. **EXECUTE**：`execute_code()` 执行 Maya Python 代码
4. **VERIFY**：`scene_assert()` + `scene_review()` 确认结果

## 工具详解

### 空间感知

```python
# 全场景快照（一次调用，返回所有物体的空间数据）
scene_snapshot(detail="compact", format="cos")

# 深度检查特定物体（含邻居分析）
scene_inspect(target="wall_entrance", include_neighbors=True)

# 精确测量（4 种模式）
scene_measure(obj_a="wall_north", obj_b="counter_A", mode="clearance")

# 验证场景状态
scene_assert(expectations='{"wall": {"exists": true, "position": [0,0,500]}}')
```

### 工程审核

```python
# 9 维度审核（返回 0-100 分）
scene_review()
# 检查：空间完整性、重叠、冲突、区域、命名、组件化、审美、约束、孤儿

# 空间约束验证
scene_validate(rules='[{"type": "min_clearance", "value": 180}]')
```

### 镜头规划

```python
# 创建镜头（支持 8 种行业标准类型）
camera_create(target="product_display", shot_type="medium", azimuth=30, elevation=15)
# 类型：extreme_wide / wide / medium / close / extreme_close / bird_eye / low_angle / over_shoulder

# 环绕动画相机
camera_orbit(center=[0, 100, 0], radius=500, frames=120)
```

### 避灾回退

```python
# 保存检查点（操作前；快照=内存态 exportAll，不含 undo 历史）
scene_checkpoint(name="before_renovation")

# 列出所有检查点
scene_checkpoint_list()

# 回滚（先自动存安全快照，再把场景名重绑回原文件；
# 回滚后请用 scene_snapshot 重建认知）
scene_rollback(filename="cp_before_renovation.ma")
```

## CoS 符号化格式

默认输出使用 **Chain-of-Symbol** 格式，比 JSON 节省 **65% token**：

```
SCENE[164obj, 5zones] UNIT=cm UP=y
shell (23obj) @(-11.8,178.8,145.7)
  GRP_floor[mesh]@(0,0,0) 1121.5x20x1530.5
  pasted__arch_wall[mesh]@(0,0,0) 100x300x10
entrance (6obj) @(157.3,162.6,-111.6)
  GRP_workshopFront[group]@(1162,-17,103) 227.4x200.9x193.3
```

## 配套 Skills

项目提供 4 个 Codex Skills，放在 `~/.codex/skills/` 下：

| Skill | 用途 | 触发场景 |
|-------|------|----------|
| `maya-architect` | 空间布局 + ICEV 工作流 | 用户描述空间需求时 |
| `maya-camera` | 镜头规划 + 运镜 | 用户需要相机/动画时 |
| `maya-aesthetics` | 配色/平衡/焦点分析 | 用户关注视觉效果时 |
| `maya-safety` | 检查点/回滚/约束 | 进行高风险操作时 |

## 架构

```
┌──────────────────────────────────────────┐
│           LLM Agent (Codex)              │
│  scene_snapshot() → 完整空间模型          │
│  scene_review() → 9维度审核评分           │
└──────────┬───────────────────────────────┘
           │ 15 个 MCP 工具
┌──────────▼───────────────────────────────┐
│        MCP Server Layer                   │
│  scene_tools.py  → 工具定义               │
│  scene_cache.py  → TTL 缓存 + 脏检测      │
│  cos_formatter.py → CoS 符号化（省65%）    │
│  security.py     → 输入验证 + 速率限制     │
└──────────┬───────────────────────────────┘
           │ execute_code("import _mcp_scene; ...")
┌──────────▼───────────────────────────────┐
│        Maya 端 (_mcp_scene 模块)           │
│  get_scene_graph() → 层级 + BBox + 变换   │
│  get_spatial_index() → 空间索引 + 邻居     │
│  scene_review() → 9维度审核引擎            │
│  analyze_aesthetics() → 色彩/平衡/焦点     │
└──────────────────────────────────────────┘
```

## 审核维度

`scene_review()` 提供 9 个通用审核维度（适用于任何 Maya 项目）：

| 维度 | 分值 | 检查内容 |
|------|------|----------|
| spatial | 15 | 物体数、相机数、灯光数 |
| overlaps | 15 | BBox 碰撞检测 |
| conflicts | 15 | 空间穿透检测 |
| components | 15 | GRP_ 分组 + 嵌套深度 |
| naming | 10 | Maya 命名规范 |
| zones | 10 | 区域覆盖率 |
| aesthetics | 10 | 色彩和谐 + 空间平衡 + 焦点 |
| constraints | 5 | 安全约束 |
| orphans | 5 | 孤儿/空组检测 |

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python -m pytest tests/ -q

# 安全审计
semgrep scan --config auto src/
```

## 致谢

基于 [chadrik/maya-mcp-server](https://github.com/chadrik/maya-mcp-server) 扩展开发。

## 许可证

MIT
