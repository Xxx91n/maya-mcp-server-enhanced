# Handoff — maya-mcp-grill 下一轮任务书（rev7）

> 生成时间：2026-09-17（round6 grill 定稿：blender-mcp 对标 + 任务重排）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-04 通过**：统一安全管线 + 威胁模型 + connection_guide 收口 + D-019 双层错误契约。分支 fix/t04-security-pipeline（61f81af+ae0db34+56f565a），审计链 reports/2026-09-17-audit-t04.md → 返修 → audit-t04-closure.md（通过）。
- **基线（勿劣化）**：pytest 457+3skip（本轮复验一致）；ruff src=174/repo=237；mypy=221；compileall+wheel+stdio(18工具四hint)+audit JSONL 全绿。
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

## 下一任务：T-05 Qt 连接层重写（D-013/D-014c，ADR-0010）

- readyRead 事件驱动 + 逐连接命令队列 + 长度前缀分帧（8-16MiB 帧上限）+ typed error + 指数退避(0.5/1/2s) + localhost-only 强制 + 健康探针 + _failed_ports 去重
- 修 add_session 丢弃 bootstrap 返回值 bug（session_manager.py:323 实证仍在）；GUI 会话移除 temp-file 注入；native 降为 bootstrap/headless 最小通道并文档化
- 顺带清单：StreamWriter 5MB 上限接线（helper :35 仍孤儿）、client.py write_module 死响应、__main__ 调试脚本×2 移出库代码（client.py:867/session_manager.py:374）、add_session 默认端口 7002→7001 对齐文档（server.py:337）
- 注意：client.py/session_manager.py 现在抛 PipelineError 子类（D-019），重写时保持 code 语义不丢

## T-08 预热 spec（视觉闭环，D-002/D-003a/D-020②/D-021）

- 两工具拆分已定：scene_viewport_snapshot（高频便宜）+ scene_render_preview（低分辨按需）
- 对 T-05 仅软依赖：base64+尺寸限幅可在现有传输先行，分帧红利后收；分帧不进 DoD（blender-mcp 同款实证）
- headless 会话无视口→显式能力错误（按 D-019 契约：宿主侧 coded 异常 isError / 域侧 {error:{code,message,suggestion}}——内定时选域侧语义，未决项 #1 届时核销）
- 传播级一等公民：发布演示素材依此产出

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
- test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited RuntimeWarning；server.py port 校验 1<port vs 文案 1-65535 vs security.py 0<port 不一致；connection_guide 版本扫描复制粘贴三连

## 未决 spec 项（内定归属，非阻塞）

- #1 headless 视觉工具能力错误契约→T-08 内定（D-019 模式可循）；#3 拆分边界→T-07 绞杀者内定；#5 CoS 版本化→T-09；#6 版本号/发布节奏→T-09

## suggested skills

- 执行：implement, tdd, diagnosing-bugs（T-05 连接层重写）
- 评审：code-review（每任务完成后双轴审计，同 T-03/T-04 先例）
- 调研：research / atomcode-research（dcc-mcp-maya 竞品深挖可选）
- 收尾：handoff（再交接）、neat-freak
- 版本控制：gitbutler（but）
