# Handoff — T-09 关闭（复审通过）→ 下一任务 T-10a

> 生成：2026-09-18 · 审计 LOOP2 PASS。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-09 已交付并过审**：LICENSE/pyproject 身份/README 双语/AGENTS/skills×2/CHANGELOG/CONTRIBUTING/docs 同步全落地（commit 3cfeccd @ t09/release-hygiene）；六 roadmap issues #2-#7 已建（#7 pinned），#3 回填 skills 卡与 README。
- **复审返工已核销**：F-1 phantom validator（D-011 决策未实现）清除并替换为真实 scene_plan；F-2 issues[] 实形状；F-4 SKILL 卡出矩阵 pts 列+AGENTS 联动补行；R-1 报告数字订正。审计件：reports/2026-09-18-audit-t09.md（打回）+ 2026-09-18-audit-t09-closure.md（通过）。
- **基线复核（勿劣化；规范环境=.venv Py3.13）**：pytest 546+6skip+1 既有环境失败（test_qt_channel WinError 64）；ruff src=174/repo=237；mypy=221；compileall+uv build+新 venv 装包测活+stdio smoke 全绿。
- **改名未执行**——入人工确认门：命令清单见 reports/2026-09-18-t09-implementation.md（gh repo rename + remote set-url + Actions 旧引用检查 + PyPI URL 不随重定向提醒 + 禁旧名重建）。PyPI mcp-for-maya 空闲已实测（404）。

## 工作约定（承袭）

- 写文件经 ctx_execute（node.js fs）；版本控制一律 but（禁 git 写命令）；每轮独立分支；评审件由评审方自提（本轮修复窗代提为例外）。
- 授权分层不变：agent=文件/分支/issues/PR；人工门=repo 改名、push main、tag、Release、PyPI、secret。
- 报告验收数字一律以当次命令实测为准（连续两轮证据数字失实，R-1 已订正）。

## 下一任务：T-10a 最小质量门（GH Actions）

- 内容：.github/workflows CI 跑 pytest + ruff（最小门，发 v1.0 前置；D-021 排序）。
- CI badge/Actions 引用直接写新仓库名 mcp-for-maya（改名命令已交付用户，大概率先于 T-10a 执行）。
- Linux CI 顺带复核 test_qt_channel WinError 64 的 RST/FIN 语义差（本机 Windows 环境失败项）。
- 其后：发布 v1.0.0（人工门）→ T-10b 完整质量门 → T-12 Poly Haven（v1.1，issue #2）→ T-06/T-07 内部债。

## grill 方向指示

- T-10a spec 待开：CI 矩阵（OS/Python 版本）、ruff/mypy 门阈（沿用冻结 error budget 还是收口）、badge 落位、Trusted Publishers 发布工作流是否同轮（D-032② 发布日清单联动）。

## 真源与上下文

- 决策账本 .scratch/maya-mcp-grill/decision-ledger.md（D-001..D-032）；CONTEXT.md；ADR 0001..0014；AGENTS.md 联动规范（本轮新增 skills/ 行）；docs/threat-model.md §5。
- 本轮报告 .scratch/maya-mcp-grill/reports/2026-09-18-t09-implementation.md（含返工核销节+改名命令清单+发布日清单）。

## 遗留真机窗口清单（环境限制，未做≠未写）

全部归 issue #7：mayapy Tier2、GUI Tier3 八项、MCP Inspector+双客户端多 block 实测（D-025④）、PySide2 真机、T-05 R-2 headless fallback 真机。

## 登记债（碰到再修，勿认领）

- **新增**：D-011/ADR-0008 validator 注册表=已决策未实现（src/ 无 register/check_error；SKILL.md 已如实标注）——挂 T-06/T-07 或显式撤回决策。
- 沿用：_suggest_layout pair-window 截断未披露；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分语义重设计（D-014d）；test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited；connection_guide 版本扫描复制粘贴三连；ADR-0010 O-2；_probe_port socket 泄漏（O-5）；native _send_receive 丢 code（R-1 微瑕）；visual_module verticalFlip/lookThru 参数序/cmds.refresh 静默待真机；_visual_injected/_injected_sessions 重连跳过重注入；_visual_call/_exec_visual 双胞胎（绞杀者归并时收）；Scene.gui/_ViewWidget/_MAGIC.get 死面。

## suggested skills

- 执行：implement；CI 落地后可 code-review
- 调研：atomcode-research（GH Actions 矩阵/Trusted Publishers 配置如需查证）
- 收尾：handoff、neat-freak；版本控制：gitbutler（but）
