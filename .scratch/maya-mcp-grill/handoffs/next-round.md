# Handoff — maya-mcp-grill 下一轮任务书（rev15）

> 生成时间：2026-09-18（T-10a 实施完成，PR #8 待人工合并）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-10a 已交付**：分支 `t10a/ci-quality-gates`（stacked on `grill/round10-t10a-spec-docs`），commit `zon`=D-034 client.py 修复、`tmu`=CI 全套（D-033/D-035/D-036）。PR #8 已开：**合并=人工门**。
- **首个 CI run 自证全绿**（run 35327567488）：lint `ruff budget gate` 9s + test 4 格（ubuntu/windows × 3.10/3.x）全过 + 汇聚 `ci`。实测 check 名：`ruff budget gate` / `pytest (<os>, <ver>)` ×4 / `ci`——分支保护 contexts 用。
- **基线复核（勿劣化；.venv Py3.13 Windows）**：pytest **547+6skip+0fail**（原 WinError64 项红转绿）；ruff src=174/tests=63/repo=237 全持平；mypy=221（不进 CI 任何形态）；compileall+uv build+干净 venv 装 wheel stdio 握手=PROCESS_ALIVE_OK。
- **探测分支结果**：tests/ auto-fixable=29/63=46% < ~80% → 两段预算照旧 `{"src":174,"tests":63}`；tests-fix commit 未触发。
- **本地预算门双向验证**：真报告 exit 0；压预算 src:170 exit 1 + `::error::`。

## 真源与上下文（先读这些）

- 决策账本 .scratch/maya-mcp-grill/decision-ledger.md（D-001..D-036）
- ADR docs/adr/0001..0015（0015=CI/发布工作流形态，本轮已落地）
- T-10a 实施报告 .scratch/maya-mcp-grill/reports/2026-09-18-t10a-implementation.md（含发布日/设置清单全项）
- AGENTS.md 联动规范；CONTEXT.md；docs/testing.md 分层（mayapy 档永不入 CI）

## 工作约定（承袭）

- 写文件经 ctx_execute（node.js fs，**绝对路径**）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- **新坑**：`but pr` 不识别自定义 SSH host（`github-Xxx91n`）→ `but push <branch>` + `gh pr create` 兜底（PR body 披露 stacking）。
- **新坑**：Windows 上 ruff JSON 报告输出绝对路径——分段统计脚本必须 relpath(cwd) 归一化。
- 授权分层：agent=文件/分支/issues/PR；人工门=push main、tag、Release、PyPI、pending publisher、environment reviewer、分支保护、secret。
- 验收数字一律以当次命令实测为准。

## 下一任务：发布 v1.0.0（人工门序列）→ T-10b 完整质量门

### 先决：合并 PR #8（人工门），或按口味先合 `grill/round10-t10a-spec-docs`

### 发布日清单（全项入档于 T-10a 报告 §11，摘要）
1. PyPI pending publisher 人工预配：repo=`Xxx91n/mcp-for-maya`、workflow=`release.yml`、environment=`pypi`
2. GitHub Environment `pypi` 配 required reviewer
3. 版本晋升决策（D-032①）：0.1.0 锁名发布 or 直升 1.0.0+5-Production/Stable（需同 commit 升 classifier）
4. tag 推送 `v*` → release.yml 自动 test→build→publish → `gh release create v* --generate-notes`
5. 分支保护：`gh api -X PUT repos/Xxx91n/mcp-for-maya/branches/main/protection`，contexts=实测 check 名（见上，推荐汇聚 `ci` 单 context 或全部 6 名）
6. PyPI badge 补 README 双语（`?cacheSeconds=300`）；TestPyPI 预演可选

### T-10b 完整质量门（发布后可动）
pre-commit + mypy-baseline 第一天落地（sync 入 VCS+blocking，221 存量冻结）+ ruff per-rule 预算升级（litellm ruff-strict-budget.json 先例）+ coverage + macOS 格候选 + ruff 原生 baseline（#1149）落地即迁移。

### 其后
T-12 Poly Haven（v1.1，issue #2）→ T-06/T-07 内部债。

## 登记债（碰到再修，勿认领）

- **新增**：`uvx ruff` 浮动版本 vs 冻结预算的工具漂移风险（无 lock 的既定取舍；若漂移致误红，PR 降预算或修真实问题）；`but pr` SSH-alias forge 识别缺陷；OSError errno 白名单（ENET*/ENOTCONN→unavailable）后续增强；ruff 原生 baseline（#1149）迁移；pending publisher 锁名窗口风险。
- 沿用：D-011/ADR-0008 validator 注册表已决策未实现；_suggest_layout pair-window 截断；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分（D-014d）；test_security.py:389 I001；AsyncMock never-awaited；connection_guide 版本扫描三连；ADR-0010 O-2；_probe_port socket 泄漏；native _send_receive 丢 code；visual_module 真机项；_visual_injected 重连；_visual_call/_exec_visual 双胞胎；Scene.gui/_ViewWidget/_MAGIC.get 死面。

## 遗留真机窗口清单（归 issue #7）

mayapy Tier2、GUI Tier3 八项、MCP Inspector+双客户端多 block 实测、PySide2 真机、T-05 R-2 headless fallback 真机。

## suggested skills

- 合并后发布序列：人工门执行（清单已备）；T-10b 用 implement；收尾 handoff、neat-freak；版本控制 gitbutler（but）
- 调研：atomcode-research（mypy-baseline 形态/pre-commit 选型如开 T-10b）
