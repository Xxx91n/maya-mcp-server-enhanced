# Handoff — T-10a 审计通过（PASS）→ 下一任务：PR #8 合并（人工门）→ T-10b

> 生成：2026-09-18 · 审计子 Agent · 结论以决策账本为唯一真源

## 本轮验收事实（审计实测，非计划）

- **T-10a 审计 PASS**：分支 `t10a/ci-quality-gates`（stacked on `grill/round10-t10a-spec-docs`），commit `zon`=eaa232e（D-034 client.py 修复）+`tmu`=b82e11f（CI 全套 D-033/D-035/D-036）。PR #8 OPEN→main，6/6 checks 绿（run 35327567488）。**合并=人工门**。
- **硬验收复跑全绿**（.venv Py3.13 Windows）：compileall OK；uv build whl+sdist；新 venv 装 wheel 后 mcp-for-maya.exe stdio 握手 serverInfo/toolCount=20/ping={}；pytest **547+6skip+0fail**；ruff src=174/tests=63/repo=237 全持平；预算门双向验证 exit 0/exit 1+::error::；YAML×3 OK；check_ruff_budget.py lint 净。
- **mypy=221 本地不可复验**（.venv 未装 mypy）——沿用文档化基线，T-10b mypy-baseline 落地时会重新实测。
- **审计报告**：.scratch/maya-mcp-grill/reports/2026-09-18-audit-t10a.md（声明→证据→结论全表）。

## 呈报未追认项（轻微，不阻断）

- 报告幻影引用 `WORKFLOW §4.2`（全仓库不存在）；diff 行数 "2删3增" 实为 3/3。连续第三轮证据小失实——后续实施窗口须继续执行"验收数字一律当次实测"。

## 新登记债（碰到再修，勿认领）

- `|| true` 吞 ruff 崩溃退出码（异常路径经 json traceback 失败，仍 fail 更脏）；ci↔release test 矩阵 ~20 行重复（第三处收 workflow_call）；Qt 已映射 ConnectionError 族而 native _send_receive 未对等（与"native 丢 code"旧债同族）；unavailable 消息丢 {e}、budget 脚本 argv 未防护、Qt _send_receive 缺 Raises docstring。
- 沿用：`uvx ruff` 浮动 vs 冻结预算（已登记，审计复核风险属实）；but pr SSH-alias forge 缺陷；OSError errno 白名单；ruff 原生 baseline(#1149)；pending publisher 锁名窗口；及 next-round.md rev15 全部沿用债。

## 下一任务（顺序）

1. **PR #8 合并 = 人工门**（用户执行）。
2. 发布 v* 序列 = 人工门清单（实施报告 §11 全项：pending publisher→environment reviewer→版本晋升决策→tag+release.yml→gh release create→分支保护 contexts=实测 check 名→PyPI badge）。
3. **T-10b 完整质量门 spec**（grill 方向）：mypy-baseline 形态（sync 入 VCS+blocking）/pre-commit 选型/ruff per-rule 预算（litellm 先例）/coverage/macOS 格/ruff 原生 baseline 迁移；顺带可 grill：`|| true` 收窄、Qt/native 映射对等、`uvx ruff` 固定化。
4. 其后 T-12 Poly Haven（v1.1，issue #2）→ T-06/T-07 内部债。

## 工作约定（承袭）

- 写文件经 ctx_execute（node.js fs，绝对路径）；版本控制一律 but（禁 git 写命令）；每轮独立分支；评审件由评审方自提（本轮审计件已自提 `audit/t10a-closure`）。
- 授权分层：agent=文件/分支/issues/PR；人工门=合并 main、tag、Release、PyPI、pending publisher、environment reviewer、分支保护、secret。
- 已知坑：but pr 不识别 github-Xxx91n SSH alias→but push+gh pr create 兜底；Windows ruff JSON 输出绝对路径需 relpath 归一化；冷 venv 首跑测活探针需 >20s 超时。

## 真源

- .scratch/maya-mcp-grill/decision-ledger.md（D-001..D-036）
- docs/adr/0001..0015
- .scratch/maya-mcp-grill/reports/2026-09-18-audit-t10a.md + 2026-09-18-t10a-implementation.md
- .scratch/maya-mcp-grill/handoffs/next-round.md rev15（实施侧交接，含发布日清单摘要）

## suggested skills

- T-10b 规格化：grill → to-spec → to-tickets → implement
- 调研：atomcode-research（mypy-baseline 形态/pre-commit 选型）
- 版本控制：gitbutler（but）；收尾：handoff、code-review
