# T-09 复审通过报告（closure）— D-028..D-032

> 日期：2026-09-18 · 执行：审计子 Agent（第二 LOOP）· 对象：amend 后 commit 3cfeccd（branch t09/release-hygiene，fixed point 08f99e0）+ 评审件 commit 1319ab6
> 前轮：2026-09-18-audit-t09.md 打回返工（F-1 实质 + F-2/F-4 次要 + F-3 判断 + R-1 证据失实）
> 结论：**PASS** — F-1..F-4 + R-1 全部实物核销为真；同一套硬验收复跑全绿；无新增缺陷。

## 一、返工核销（逐项实物复核）

| 项 | 修复声明 | 审计证据 | 结论 |
|---|---|---|---|
| F-1 | README 双语 phantom→scene_plan；SKILL.md 删节改诚实声明 | git diff 2cf406d→3cfeccd：README:24 双语 "自注册 validator"→"scene_plan（zone 语义+布局建议）"（scene_plan 为 20 工具实测存在、zone 语义属实）；SKILL.md Custom validators 节删除，改注 "designed (ADR-0008) but not yet implemented — there is no register API to call today"；shipped docs 全 grep register(name/check_error/自注册 零命中 | ✅ |
| F-2 | issues[] 实形状写入卡片 | SKILL.md:34 现为 "severity, check, and a msg summary (counts + advice). Per-object detail lives under checks[] — e.g. checks.overlaps.details names the colliding pairs (sampled list)"；对 maya_scene_module.py:2839-2845 实物：details=overlap_pairs[:5] 为 {a,b} 对象名对——属实 | ✅ |
| F-3 | README_en 平行节保留并披露理由 | 实施报告新增「复审返工」节披露保留理由（spec“README_en 平行同步”授权）；审计接受该判断——属结构重排自由度内 | ✅（判断项关闭） |
| F-4 | SKILL.md 删 max pts 列+AGENTS.md 联动表补行 | SKILL.md 表改 2 列（check/what it looks at）+“does not duplicate weights, see README/AGENTS.md”指引；AGENTS.md:170 新增联动行 maya_scene_module.py(scene_review check names/semantics)→skills/scene-review-playbook/SKILL.md | ✅ |
| R-1 | 报告数字订正 | 实施报告：'^## '=14（实测复核=14）、skills 48/51（wc -l 复核=48/51）；订正原因（split 差 1）已写明 | ✅ |

## 二、同一套硬验收复跑（返工后，全绿）

| 验收项 | 实测 |
|---|---|
| compileall | COMPILE_OK |
| uv build | mcp_for_maya-0.1.0 whl+sdist |
| wheel 内容 | 21 pkg py、双 entry→同 main、Name=mcp-for-maya、urls 新仓、MIT+LICENSE |
| 新 venv 装包测活 | mcp-for-maya==0.1.0 装入；--help/-vv 正常 |
| stdio smoke（对已装 wheel） | serverInfo "Maya MCP Server"、20 工具、annotations 无缺口、ping={}、os.system→[blocked_pattern]、BOGUS→[invalid_input] |
| pytest | 546 passed + 6 skipped + 1 failed（test_qt_channel WinError 64，同基线） |
| ruff src / repo / mypy | 174 / 237 / 221 — 与基线持平（docs-only 零波动） |

## 三、补充观察（非缺陷）

- amend 净 delta=6 文件 36+/26-，范围恰为返工清单，无夹带。
- 评审件（diff-t09-review.patch + 2026-09-18-audit-t09.md）由修复窗口代为独立 commit（1319ab6，verbatim 未动评审内容）——仓库 .scratch 入 git 为既定惯例，内容与审计员落盘一致，登记为事实不追责；后续轮次评审件建议由评审方自提。
- 登记债新增建议：**D-011/ADR-0008 validator 注册表=已决策未实现**（decision-vs-code gap，非本轮引入）——SKILL.md 已如实标注，建议挂账至 T-06/T-07 内部债统一处置（或显式撤回决策）。

## 四、结论

T-09 发布卫生实施（D-028..D-032）**审计通过**：交付物与代码实测一致，负向清单全守，授权分层未越，基线不劣化。剩余人工门：repo 改名（命令清单已交付）、PyPI 首发、tag/release。
