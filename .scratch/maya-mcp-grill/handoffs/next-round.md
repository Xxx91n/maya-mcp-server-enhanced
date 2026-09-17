# Handoff — maya-mcp-grill 下一轮任务书（rev8）

> 生成时间：2026-09-17（T-05 完成交棒）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-05 实施完成，审计返修一轮，待复审**：首轮审计(audit-t05)裁定打回返工——F-1 headless 回退死代码+僵尸会话(两层失效)、F-2 ruff repo +1 失实、F-3 Qt 路径域 code 丢失；三项已全修(双端防御：helper 事件循环检测 qt_unavailable_headless + client liveness gate ping≤5s；raise_on_error=False 契约钉；域 code 编入异常文本)。O-1/O-3/O-4/O-6 顺手核销，O-2/O-5 已入登记债。分支 fix/t05-qt-channel(kyn=feat+kpt=docs+返修 commit)。报告 reports/2026-09-17-t05-implementation.md（含返修附录）。
- **基线（勿劣化）**：pytest **517+3skip**；ruff src=174/repo=237；mypy=221；compileall+wheel+stdio(18工具四hint ping audit JSONL)全绿。
- **锐评复核（round6 实物复验）**：rui.txt 全条目有归属无孤儿；T-04 核销项实证为真（marker-block :45/confirm :392/真 token bucket/pipeline 收口/helper 诚实注释 :182）。
- **round6 决策**：D-020（对标三档能力矩阵，①被 D-021 修订）→ D-021（任务重排 C 版）→ D-022（Codex Skills 处置 C 微调版）。落地 ADR-0012。

## 真源与上下文（先读这些）

- 决策账本：.scratch/maya-mcp-grill/decision-ledger.md（D-001..D-022；D-020 revised→D-021，余皆 current）
- 术语表 CONTEXT.md；ADR docs/adr/0001..0012（0012=对标定位+发布排序）
- 规则文件 AGENTS.md（联动表含 pipeline/connection_guide 行）
- 审计 smoke 脚本：.scratch/maya-mcp-grill/audit/{stdio-smoke,stdio-ratelimit,probe,probe-repair}.mjs
- 全部历史：.scratch/maya-mcp-grill/{handoffs,reports,audit}/

## 工作约定（承袭）

- 写文件一律经 ctx_execute（node.js fs / python fs）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- 账本纪律：新决策先入 D-xxx；测试纪律：每修复带回归（base 可复现 RED）；预算只降不升。
- 文档纪律：README/AGENTS/threat-model 不超前于代码、同 commit 同步、字字为真（threat-model §5 矩阵须与 pipeline.TOOL_ANNOTATIONS 逐行一致）。
- 错误契约 D-019；审计不变式：每个 tools/call 必落 audit.jsonl 一行；管线 try 外不得有可能抛出的代码。

## 任务序（D-021 定案，替代旧序）

```
T-05 Qt 连接层重写
T-08 视觉闭环           ← 提前：对标最大短板+传播演示点
T-09 发布卫生           ← T-11 版本声明文档级并入
T-10a 最小质量门        ← GH Actions 跑 pytest+ruff
─── 发布 v1.0 ───
T-10b 完整质量门        ← pre-commit+mypy ratchet，T-06/T-07 动工前置
T-12 Poly Haven         ← v1.1 首弹（挤首发活口见 ADR-0012）
T-06 审美引擎单源化     ← 内部债，在 T-10b 护栏下做
T-07 注册表+绞杀拆分    ← 内部债
```

## 下一任务：T-08 视觉闭环（D-002/D-003a/D-020②/D-021）

- 两工具拆分已定：scene_viewport_snapshot（高频便宜）+ scene_render_preview（低分辨按需）
- T-05 已交付分帧红利：base64 视口图走 16MiB 帧通道无 temp-file 负担；headless 会话无视口→显式能力错误（D-019 契约：内定时选域侧语义，未决项 #1 届时核销）
- 传播级一等公民：发布演示素材依此产出
- 注意 seam：截图能力挂在 client.framed_channel 上区分 GUI/headless；Maya 侧用 MGlobal.activeView + OGS 或 cmds.getAttr 屏幕捕获路径，先调研最小实现

## 其后任务速览

- **T-09**（D-001c/D-003c/D-010/D-020④⑤/D-022）：LICENSE(MIT+上游 notice)、pyproject 身份/URLs、仓库改名 mcp-for-maya、README 逐项核实（18工具/11维/分值表/65%/pip 指向/Skills 幻影按 D-022 话术/LOGLEVEL/scripts/）、能力矩阵对比叙事、telemetry 信任卖点明示、T-11 版本声明并入、roadmap issue 开 skills+v1.x 项
- **T-10a**（D-009/D-021）：GH Actions pytest+ruff 最小门；**T-10b**：pre-commit+mypy ratchet+覆盖率
- **T-12**（D-003b/D-020/D-021）：Poly Haven 薄集成挂 scene_plan zone+bbox 推荐，v1.1
- **T-06**（D-006/D-014a）：审美单源化+伪引用清算（McCamy/mired/Aesthetic3D/arXiv/Narrative/Tripo3D 实证仍在）
- **T-07**（D-004/D-011/D-014c）：验证器注册表+绞杀拆分

## 竞品与对标情报（D-020⑤，ADR-0012）

- mcp-for-blender（28.8k★）：5 资产源/viewport 截图/对象 CRUD/export/API 内省/safe_mode opt-in/telemetry 默认开（我们不跟）
- dcc-mcp-maya（55★/535commits/活跃）：Maya 侧直接竞品，29 skill 包+Codex 插件市场+progressive skills 打法——skills 是 README 第一卖点
- 官方入局信号：Blender 官方 MCP+Claude connector、Autodesk APS（2026-04）——护城河窗口期有限

## 登记债（碰到再修，勿认领）

- _suggest_layout pair-window 截断未披露；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分语义重设计（D-014d）
- test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited RuntimeWarning；connection_guide 版本扫描复制粘贴三连
- ADR-0010 后果项“版本感知响应规范化”未实现（audit-t05 O-2）；_probe_port 的 MayaConnectionError 分支 socket 泄漏（O-5，基线既有）

## 未决 spec 项（内定归属，非阻塞）

- #1 headless 视觉工具能力错误契约→T-08 内定（D-019 模式可循）；#3 拆分边界→T-07 绞杀者内定；#5 CoS 版本化→T-09；#6 版本号/发布节奏→T-09

## suggested skills

- 执行：implement, tdd, research/atomcode-research（T-08 视觉闭环：Maya viewport 捕获路径需调研）
- 评审：code-review（每任务完成后双轴审计，同 T-03/T-04 先例）
- 调研：research / atomcode-research（dcc-mcp-maya 竞品深挖可选）
- 收尾：handoff（再交接）、neat-freak
- 版本控制：gitbutler（but）
