# Handoff — maya-mcp-grill 下一轮任务书（rev12）

> 生成时间：2026-09-17（T-08 审计通过并合入 main d0f6f77）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-08 已关闭**：两轮审计——audit-t08.md 打回（F-1 联动规范漏改 test_security.py + capture_invalid 零覆盖；F-2 skip 数失实）→ 返修 amend 归位 → audit-t08-closure.md 通过。全部 5 commit 已 land 到 origin/main（d0f6f77），fix/audit/grill 三分支已删。
- **基线复核（勿劣化；规范环境=.venv Py3.13）**：pytest 546+6skip+1 既有环境失败（见下）；ruff src=174/repo=237（持平）；mypy=221（持平，新增 2 文件 0 error）；compileall+uv build wheel+stdio 全绿。
- **既有环境失败（非 T-08 回归，勿认领修复）**：test_qt_channel.py::TestQtClientWire::test_connection_closed_raises_unavailable —— 裸 asyncio 复现 WinError 64（Windows RST vs POSIX FIN 语义差异）。建议 T-10a CI（Linux）复核。
- **计数对账**：旧基线 520 collected；现 **553 collected = 旧 520 + 新 33**（29 视觉契约 + 3 security 钉 + 1 mayapy batch-gate）。ignore-visual 变体实测 517+6skip+1fail。skip 构成=4 mayapy+2 PySide6；注意系统 python3.11 装 PySide6 会得 4-skip 假象。
- **R-1 残余（核销状态）**：本文件对账式已订正；report:41 "514 passed" 陈旧格留待下次 docs 触手订正为 517（属 dated artifact，审计窗口不改他人报告）。

## 真源与上下文（先读这些）

- 决策账本：.scratch/maya-mcp-grill/decision-ledger.md（D-001..D-027）
- 术语表 CONTEXT.md；ADR docs/adr/0001..0013（0013=视觉闭环架构）
- AGENTS.md（结构+联动表已含 visual_* 行；security.py 行含 test_security.py 联动义务——T-08 F-1 教训）
- 审计链：reports/2026-09-17-audit-t08.md + 2026-09-17-audit-t08-closure.md；闭环记录 handoffs/round8-t08-closed.md
- 审计 smoke：.scratch/maya-mcp-grill/audit/{stdio-smoke,stdio-ratelimit,probe,probe-repair}.mjs

## 工作约定（承袭）

- 写文件一律经 ctx_execute（node.js fs 或 heredoc）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- 新决策先入 D-xxx；测试纪律：修复带回归；预算只降不升。
- 文档传播矩阵：只修本次变更致 stale 的行，其余错数落清单交后续任务。
- D-019 双层错误契约；审计不变式；管线 try 外零可抛代码。
- **T-08 审计教训**：改 security.py 必同步 test_security.py（联动规范硬义务）；报告验收数字必须当轮实测，不得沿用旧跑。

## 遗留真机窗口清单（环境限制，未做≠未写）

1. **mayapy Tier2**：本机无 Maya 安装。真机跑 `pytest -m mayapy`——含 test_visual_module_batch_gate_in_real_maya（batch 闸真机可跑）。
2. **GUI Tier3 手动 checklist**（docs/testing.md 八项）：verticalFlip 方向核验（若反则删该调用）、VP2 kFloat 实画面、HUD/选区可见、playblast 产物尺寸、lookThru 恢复、currentTime 恢复、batch 闸、exists-flag 真机接受度。
3. **MCP Inspector + Claude Code + Codex 多 block 渲染**（D-025④ DoD 项）：无客户端环境未实测；返回结构按 FastMCP 2.14.2 列表透传构造。
4. **PySide2 真机兼容**：QIODevice.OpenModeFlag 已 getattr 兜底；Maya≤2024 PySide2 路径未真机验证。
5. T-05 R-2 旧账：headless bootstrap→native 落会话真机未实测（同窗口顺手补验）。

## 下一任务：T-09 发布卫生（D-001c/D-003c/D-010/D-020④⑤/D-022）

### 交付物
- LICENSE（MIT+上游 chadrik notice 保留）、pyproject 身份/URLs/license 字段、仓库改名 mcp-for-maya 配套
- **README/README_en 逐项核实清单**（T-08 已核销 tool count 20 项，余）：
  - 9 维 vs 11 维审核口径不一致（能力矩阵写 11、维度表写 9）
  - CoS 65% 省 token 数字未核实证
  - PyPI 名/pip install 指向未发布包 + 仓库 URL Xxx91n/maya-mcp-server-enhanced 幻影
  - 4 个 Codex Skills 幻影（D-022：删或实建）
  - LOGLEVEL 写法、scripts/secrets.py、scripts/dependency.py 幻影路径
  - AGENTS.md 审核维度表同 9/11 口径
- 能力矩阵竞品对比叙事、telemetry 信任卖点、roadmap issue 落 GitHub
- T-11 版本声明文档级并入（版本号策略+release 节奏写进 README/CONTRIBUTING）

### 其后任务速览
- **T-10a**：GH Actions pytest+ruff 最小门；**T-10b**：pre-commit+mypy ratchet+覆盖率（T-06/T-07 前置护栏）
- **T-12**：Poly Haven 薄集成（v1.1）
- **T-06/T-07**：内部债（审美单源化/注册表绞杀）

## 登记债（碰到再修，勿认领）

- _suggest_layout pair-window 截断未披露；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分语义重设计（D-014d）
- test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited；connection_guide 版本扫描复制粘贴三连
- ADR-0010 O-2；_probe_port socket 泄漏（O-5）；native _send_receive 丢 code（R-1 微瑕）
- visual_module verticalFlip 为 GL bottom-up 约定的防御默认——Tier3 真机若画面倒置删之；lookThru(panel,camera) 参数序按官方 synopsis [editorName][object]，若真机不兼容换 modelEditor -e -camera
- **T-08 审计新登**：_visual_injected/_injected_sessions 会话重连跳过重注入（同款 parity 缺陷，归并时同修）；_visual_call/_exec_visual 与 scene_tools 同形双胞胎（绞杀者归并时收）；Scene.gui/_ViewWidget/_MAGIC.get 死面；cmds.refresh 异常静默可能回旧帧。

## suggested skills

- 执行：implement, tdd；评审：code-review；调研：atomcode-research（T-09 LICENSE/PyPI 名核实可联网查证）
- 收尾：handoff, neat-freak；版本控制：gitbutler（but）
