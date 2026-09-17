# Handoff — maya-mcp-grill 下一轮任务书（rev6）

> 生成时间：2026-09-17（T-04 实现+返修+复审通过）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-04 通过**：统一安全管线 + 威胁模型 + connection_guide 收口 + D-019 双层错误契约。
  分支 fix/t04-security-pipeline = ovz(61f81af) + qtv(ae0db34) + ulw(56f565a 返修)。
  审计链：reports/2026-09-17-audit-t04.md（打回 4+6）→ 返修 → reports/2026-09-17-audit-t04-closure.md（通过）。
- **新基线（勿劣化）**：pytest 457+3skip；ruff src=174 / repo=237；mypy=221；compileall+wheel+stdio(18工具四hint)+audit JSONL 全绿。
- 审计 smoke 脚本留档：.scratch/maya-mcp-grill/audit/{stdio-smoke,stdio-ratelimit,probe,probe-repair}.mjs（node 直跑，可复用）。

## 真源与上下文（先读这些）

- 决策账本：.scratch/maya-mcp-grill/decision-ledger.md（D-001..D-019 全 current）
- 术语表 CONTEXT.md；ADR docs/adr/0001..0011
- 规则文件 AGENTS.md（联动表已含 pipeline/connection_guide 行）
- 全部历史：.scratch/maya-mcp-grill/{handoffs,reports,audit}/

## 工作约定（承袭）

- 写文件一律经 ctx_execute（node.js fs / python fs）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- 账本纪律：新决策先入 D-xxx；测试纪律：每修复带回归（base 可复现 RED）；预算只降不升。
- 文档纪律：README/AGENTS/threat-model 不超前于代码、同 commit 同步、字字为真（threat-model §5 矩阵须与 pipeline.TOOL_ANNOTATIONS 逐行一致）。
- 错误契约 D-019：宿主失败=coded 异常→isError+[code]；Maya 域={error:{code,message,suggestion?}}；新增错误形态同此。
- 审计不变式：每个 tools/call 必落 audit.jsonl 一行（success/error/rejected）——管线 try 外不得有可能抛出的代码。

## 下一任务：T-05 Qt 连接层重写（D-013/D-014，ADR-0010）

- readyRead 事件驱动 + 逐连接命令队列 + 长度前缀分帧（8-16MiB 帧上限）+ typed error + 指数退避(0.5/1/2s) + localhost-only 强制 + 健康探针 + _failed_ports 去重
- 修 add_session 丢弃 bootstrap 返回值 bug；GUI 会话移除 temp-file 注入；native 降为 bootstrap/headless 最小通道并文档化
- 顺带清单：StreamWriter 5MB 上限接线、client.py write_module 死响应、__main__ 调试脚本移出库代码、add_session 默认端口 7002→7001 对齐文档
- 注意：client.py/session_manager.py 现在抛 PipelineError 子类（D-019），重写时保持 code 语义不丢

## 登记债（碰到再修，勿认领）

- _suggest_layout pair-window 截断未披露；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分语义重设计（D-014d）
- test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited RuntimeWarning；server.py port 校验 1<port vs 文案 1-65535 vs security.py 0<port 不一致

## suggested skills

- 执行：implement, tdd, diagnosing-bugs
- 评审：code-review（T-05 完成后同法双轴）
- 调研：research / atomcode-research（Qt 通道设计取证）
- 收尾：handoff（再交接）、neat-freak
- 版本控制：gitbutler（but）
