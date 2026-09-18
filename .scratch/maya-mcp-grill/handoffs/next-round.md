# Handoff — maya-mcp-grill 下一轮任务书（rev14）

> 生成时间：2026-09-18（T-10a grill 定稿 D-033..D-036）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-09 已关闭**（3cfeccd+audit closure 73fc2bd，复审 PASS）；**repo 已由用户改名** maya-mcp-server-enhanced→Xxx91n/mcp-for-maya，本地 remote 双 URL 已跟随（ls-remote 可达 HEAD=73fc2bd）；六 roadmap issues #2-#7 已建（#7 pinned）。
- **T-10a spec 四问闭合**：D-033 CI 矩阵 / D-034 RST 修复 / D-035 预算门+mypy 排除 / D-036 release.yml+dependabot+badge+分支保护清单。
- **基线复核（勿劣化；规范环境=.venv Py3.13 Windows）**：pytest 546+6skip+1 fail（test_qt_channel WinError 64=本轮修复对象）；ruff src=174/repo=237；mypy=221；无 .github/、无 lock 文件。
- **远端事实**：Xxx91n/mcp-for-maya 已存在（gh 实测）；PyPI mcp-for-maya 空闲（2026-09-18 实测 404）。

## 真源与上下文（先读这些）

- 决策账本 .scratch/maya-mcp-grill/decision-ledger.md（D-001..D-036）
- ADR docs/adr/0001..0015（0015=首个 CI/发布工作流形态）；CONTEXT.md 28 术语（新增“冻结预算”）
- AGENTS.md 联动规范；docs/threat-model.md §5；docs/testing.md 分层（mayapy 档永不入 CI）
- T-09 实施报告 .scratch/maya-mcp-grill/reports/2026-09-18-t09-implementation.md（发布日清单母版）

## 工作约定（承袭）

- 写文件经 ctx_execute（node.js fs，**用绝对路径**——沙箱 cwd 非仓库根）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- 授权分层：agent=文件/分支/issues/PR；人工门=push main、tag、Release、PyPI、pending publisher、environment reviewer、分支保护、secret。
- 文档传播矩阵：本 commit 只修因 CI/修复而 stale 的行；其余既有错误列清单交后续任务。
- 验收数字一律以当次命令实测为准（连续两轮证据数字失实的前科）。

## 下一任务：T-10a 最小质量门实施（D-033..D-036）

### 交付物清单

1. **client.py RST 修复**（D-034）：Qt `_send_receive` 捕获链 IncompleteReadError 支扩为 `(ConnectionError, asyncio.IncompleteReadError)→MayaUnavailableError`；typed re-raise 支（MayaUnavailableError/MayaExecutionError）保持在前；回归证=既有测试 test_connection_closed_raises_unavailable 由红转绿。**独立 commit，先于 CI 文件**（先修后门）。
2. **tests/ 探测分支**（D-035②）：先 `ruff check tests/ --statistics`——auto-fixable ≥~80% 则 `ruff check tests/ --fix` 同 PR 清零（独立 commit），预算只记 src；否则两段预算照旧。
3. **.github/workflows/ci.yml**（D-033/D-035①）：lint job（ubuntu-latest 单格——ruff check . --output-format=json 分段计数 vs 预算文件，>budget fail、≤通过+提示“可同 PR 降预算”）+test job（matrix [ubuntu-latest,windows-latest]×["3.10","3.x"]、fail-fast:false、actions/setup-python+astral-sh/setup-uv enable-cache+uv pip install -e ".[dev]" --system+pytest -q）；触发 push(main)+pull_request+workflow_dispatch；concurrency group+cancel-in-progress；permissions:contents:read；外部 action 全 SHA 固定+# vX.Y.Z 注释。可选实现层自由：汇聚 job（needs matrix）供分支保护单 context。
4. **.github/ruff-baseline.json**（D-035①）：{"src":N,"tests":M}——值=修复后实测（probe 结果决定 tests 段是否归 0/省略）。
5. **.github/workflows/release.yml**（D-036①）：tag v*→test（needs，矩阵重跑）→build（uv build+artifact）→publish（environment:pypi、permissions:id-token:write+contents:read、pypa/gh-action-pypi-publish SHA 固定、PEP740 attestation 随 v1.11+）；不建 GitHub Release。
6. **.github/dependabot.yml**（D-036③）：github-actions ecosystem、weekly、minor+patch 分组、open-pull-requests-limit:5。
7. **README.md+README_en.md**（D-036④）：CI badge 同轮（workflows/ci.yml 状态章，新名已一致）；PyPI badge 不加（发布日清单）。
8. **CONTRIBUTING.md**（D-035③/传播矩阵）：CI 门写明——pytest 须绿、ruff 预算可降不可升、mypy 221 为已知状态本地可跑不进 CI；PR 节补“预算下调随 PR 同 commit+理由”。
9. **AGENTS.md**（传播矩阵）：repo 结构块补 .github/workflows 一行；Development Commands 如有 stale 对齐预算门语义。
10. **CHANGELOG.md**（传播矩阵）：[Unreleased] Added=CI/release/dependabot/预算门；Fixed=ConnectionError→unavailable 映射。
11. **发布日/设置清单更新**（D-036②，入 T-10a 报告）：pending publisher 精确字段（repo=Xxx91n/mcp-for-maya、workflow=release.yml、environment=pypi）+environment required reviewer 人工配+tag 推送+gh release create v* --generate-notes+分支保护 gh api -X PUT .../branches/main/protection（contexts=首跑后实测 check 名）+PyPI badge 补（?cacheSeconds=300）+TestPyPI 预演可选。

### DoD

- [ ] 全部文件落地；YAML 语法有效；SHA 注释与实际解析版本一致
- [ ] client.py 修复后本地 pytest 全绿（含原 WinError64 项转绿）；PR 上 CI lint+4 格 test 全绿（首个 CI run 自证）
- [ ] ruff 预算文件=实测值；本地模拟超预算即 fail 已验证
- [ ] fix/ci/tests-fix 分 commit；预算下调规则写明（PR 同 commit+理由）
- [ ] 发布日/设置清单全项入档
- [ ] 基线不劣化：除既定修复外 pytest/ruff 无新增劣化
- [ ] but commit 到独立分支；PR 已开；合并=用户人工门

### 负向清单

- mypy 不进 CI 任何形态（blocking/continue-on-error 均禁）；不 skipif/注释掩盖任何既有失败；不降 ruff select 规则集过门
- CI 内不写预算文件；不建 lock 文件；不加 macOS 格；不做 lowest-resolution job；不做 reviewdog/diff-lint；不做 pre-commit（T-10b）
- 不执行任何外部动作：pending publisher/environment/tag/Release/分支保护/PyPI/secret 全清单交付
- release.yml 不建 GitHub Release；不动 version/classifier/import 名/dist 名

## 其后任务速览

- **发布 v1.0.0**（人工门，清单已备）→ **T-10b** 完整质量门（pre-commit+mypy-baseline 第一天落地+per-rule 预算升级+coverage+macOS 候选）→ **T-12** Poly Haven（v1.1，issue #2）→ **T-06/T-07** 内部债。

## 登记债（碰到再修，勿认领）

- **新增**：OSError errno 白名单（ENET*/ENOTCONN→unavailable）后续增强；ruff 原生 baseline（#1149）落地即迁移；pending publisher 不预留名→首真实发布即锁名窗口风险
- 沿用：D-011/ADR-0008 validator 注册表已决策未实现（挂 T-06/T-07 或显式撤回）；_suggest_layout pair-window 截断；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分（D-014d）；test_security.py:389 I001；AsyncMock never-awaited；connection_guide 版本扫描三连；ADR-0010 O-2；_probe_port socket 泄漏；native _send_receive 丢 code；visual_module 真机项；_visual_injected 重连；_visual_call/_exec_visual 双胞胎；Scene.gui/_ViewWidget/_MAGIC.get 死面

## 遗留真机窗口清单（归 issue #7）

mayapy Tier2、GUI Tier3 八项、MCP Inspector+双客户端多 block 实测、PySide2 真机、T-05 R-2 headless fallback 真机。

## suggested skills

- 执行：implement；CI/修复落地后 code-review
- 调研：atomcode-research（action SHA 解析/workflow 语法如需查证）
- 收尾：handoff、neat-freak；版本控制：gitbutler（but）
