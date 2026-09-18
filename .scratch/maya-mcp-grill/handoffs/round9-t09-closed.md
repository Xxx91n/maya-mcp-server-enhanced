# Handoff — T-09 关闭（发布卫生实施完成）

> 生成：2026-09-18。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-09 已交付**：LICENSE/pyproject 身份/README 双语/AGENTS/skills×2/CHANGELOG/CONTRIBUTING/docs 同步全落地；六个 roadmap issues #2-#7 已建（#7 pinned），#3 已回填两张 skills 卡与 README。
- **复审返工已核销**：F-1 phantom validator（D-011 决策未实现）从 README 双语+SKILL.md 清除；F-2 issues[] 实形状订正；F-4 SKILL.md 删 pts 列+AGENTS 联动表补 skills/ 行；R-1 报告数字订正（14 节/48/51 行）。
- **改名未执行**——入人工确认门：命令清单见报告 `reports/2026-09-18-t09-implementation.md`（含 git remote set-url、Actions 旧引用检查、PyPI URL 不随重定向提醒、禁旧名重建）。
- **PyPI mcp-for-maya 空闲已实测**：2026-09-18 pypi.org/pypi/mcp-for-maya/json → 404。
- **基线跑平**：pytest 546+6skip+1 既有环境失败（test_qt_channel WinError 64）；ruff src=174/repo=237；mypy=221；compileall+uv build+装包测活（20 工具/annotations 无缺口/ping/拦截）全绿。

## 工作约定（承袭）

- 写文件经 ctx_execute（node.js fs）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- AGENTS.md 现已 LF 归一（原混合行尾）；写文件前先确认目标行尾，replace 模式失配优先查 \r。
- 授权分层不变：agent=文件/分支/issues/PR；人工门=repo 改名、push main、tag、Release、PyPI、secret。
- 六 issues 号段：#2 Poly Haven v1.1 / #3 Skills v1.x / #4 安全模型 v1.x / #5 export+内省 v1.x / #6 资产源 exploratory / #7 真机清单+反馈（pinned）。

## 下一任务：T-10a 最小质量门（GH Actions）

- 内容：.github/workflows CI 跑 pytest + ruff（最小门，发 v1.0 前置；D-021 排序）。
- 注意：CI badge/Actions 引用直接写新仓库名 mcp-for-maya（改名命令已交付用户，大概率先于 T-10a 执行）。
- Linux CI 顺带复核 test_qt_channel WinError 64 的 RST/FIN 语义差（本机环境失败项）。
- 之后：发布 v1.0.0（人工门）→ T-10b 完整质量门 → T-12 Poly Haven（v1.1，issue #2）→ T-06/T-07 内部债。

## 真源与上下文

- 决策账本 .scratch/maya-mcp-grill/decision-ledger.md（D-001..D-032）
- 本轮报告 .scratch/maya-mcp-grill/reports/2026-09-18-t09-implementation.md（全证据+改名命令清单+发布日清单）
- CONTEXT.md（29 术语）；ADR 0001..0014；AGENTS.md 联动规范；docs/threat-model.md §5

## 遗留真机窗口清单（环境限制，未做≠未写）

全部归 issue #7：mayapy Tier2、GUI Tier3 八项、MCP Inspector+双客户端多 block 实测（D-025④）、PySide2 真机、T-05 R-2 headless fallback 真机。

## 登记债（碰到再修，勿认领）

沿用上轮清单：_suggest_layout pair-window 截断未披露；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分语义重设计（D-014d）；test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited；connection_guide 版本扫描复制粘贴三连；ADR-0010 O-2；_probe_port socket 泄漏（O-5）；native _send_receive 丢 code（R-1 微瑕）；visual_module verticalFlip/lookThru 参数序/cmds.refresh 静默待真机；_visual_injected/_injected_sessions 重连跳过重注入；_visual_call/_exec_visual 双胞胎（绞杀者归并时收）；Scene.gui/_ViewWidget/_MAGIC.get 死面。

## suggested skills

- 执行：implement；CI 落地后可 code-review
- 调研：atomcode-research（GH Actions 矩阵/Trusted Publishers 配置如需查证）
- 收尾：handoff、neat-freak；版本控制：gitbutler（but）
