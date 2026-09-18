# T-10a 最小质量门实施报告（D-033..D-036）

> 日期：2026-09-18 · 执行：修复/开发子 Agent · 基线环境：.venv Py3.13，Windows 11
> 真源：next-round.md rev14 + decision-ledger D-033..D-036 + ADR-0015 + WORKFLOW §4.2
> 分支：`t10a/ci-quality-gates`（stacked on `grill/round10-t10a-spec-docs`）· PR #8

## 交付物核销

### 1. client.py RST 修复（D-034）✅ 独立 commit `zon`，先于 CI 文件
Qt `_send_receive` 捕获链：`IncompleteReadError` 支扩为 `(ConnectionError, asyncio.IncompleteReadError) -> MayaUnavailableError`；typed re-raise 支 `(MayaUnavailableError, MayaExecutionError)` 移至该支之前（账本规定序）。OSError 未整体映射（防吞 EBADF）。
- 证据：`git diff` = 2 行删 3 行增；`pytest tests/test_qt_channel.py -q` -> `40 passed, 2 skipped`（`test_connection_closed_raises_unavailable` 红转绿）。

### 2. tests/ 探测分支（D-035②）→ 两段预算照旧
`ruff check tests --statistics` -> 63 errors，auto-fixable 仅 29（F401×18/I001×9/E401×1/W605×1）= **46% < ~80% 阈值**，不走 fix-forward；预算记两段。

### 3. .github/workflows/ci.yml（D-033/D-035①）✅
- `lint` job（ubuntu-latest 单格）：setup-uv(cache) + setup-python 3.x + `uvx ruff check . --output-format=json` + `python .github/scripts/check_ruff_budget.py` 分段计数 vs 预算文件；>budget fail，<budget 提示同 PR 降预算。
- `test` job：matrix [ubuntu-latest, windows-latest] x ["3.10", "3.x"] = 4 格，fail-fast:false；setup-uv enable-cache + `uv pip install -e ".[dev]" --system` + `python -m pytest -q`。
- `ci` 汇聚 job：needs [lint,test] + if:always()，供分支保护单 context。
- 触发 push(main)+pull_request+workflow_dispatch；concurrency group+cancel-in-progress；permissions:contents:read。

### 4. .github/ruff-baseline.json（D-035①）✅
`{"src":174,"tests":63}` = 修复后实测（src 与基线持平=修复 lint 中性；tests 46% 可修<80% 保留段）。

### 5. .github/workflows/release.yml（D-036①）✅
tag `v*` 触发 → `test`（同 4 格矩阵，needs 前置）→ `build`（uv build + upload-artifact）→ `publish`（environment:pypi、permissions:id-token:write+contents:read、pypi-publish v1.14.2 全 SHA 固定 = PEP740 attestation 默认随 v1.11+）。不建 GitHub Release。

### 6. .github/dependabot.yml（D-036③）✅
github-actions ecosystem / weekly / minor+patch 分组 / open-pull-requests-limit:5。

### 7. README.md+README_en.md（D-036④）✅
CI badge 同轮：`actions/workflows/ci.yml/badge.svg`（新仓库名已一致）。PyPI badge 不加（发布日清单）。

### 8. CONTRIBUTING.md（D-035③）✅
CI 门写明：pytest 须绿（ubuntu+windows）、ruff 预算 ratchet 只降不升（同 PR commit+理由）、mypy 221 为已知状态本地可跑不进 CI。dev 命令行对齐 `ruff check .` 预算语义。

### 9. AGENTS.md（传播矩阵）✅
repo 结构块补 `.github/` 五行（workflows×2/dependabot/baseline/script）；Development Commands 补预算门命令行。

### 10. CHANGELOG.md（传播矩阵）✅
[Unreleased] Added += CI/release/dependabot/预算门一行；Fixed += ConnectionError→MayaUnavailableError 映射一行。

### 11. 发布日/设置清单（D-036②，人工门——全部仅入档未执行）

- [ ] PyPI **pending publisher** 人工预配：repo=`Xxx91n/mcp-for-maya`、workflow=`release.yml`、environment=`pypi`（typo=invalid-pending-publisher 最高频故障；pending publisher 不预留包名——首真实发布即锁名窗口风险，登记债沿用）
- [ ] GitHub Environment `pypi` 配 **required reviewer**（人工门机制化，官方原文推荐）
- [ ] tag 推送 `v*` → 首跑 CI 实测 check 名后 → `gh release create v* --generate-notes`（GitHub Release 人工建，非 CI）
- [ ] 分支保护：`gh api -X PUT repos/Xxx91n/mcp-for-maya/branches/main/protection`，contexts=首跑实测 check 名（候选：`ci` 汇聚 job 单 context，或 `ruff budget gate` + `pytest (ubuntu-latest, 3.10)` 等 5 名）
- [ ] PyPI badge 补：`?cacheSeconds=300` 防 shields/Camo 缓存红标
- [ ] TestPyPI 预演（可选，验证 OIDC 链；OIDC 无 dry-run，只能真发一次验证）

## Action SHA 解析证据（gh api repos/<repo>/commits/<latest-release-tag>，2026-09-18 实测）

| action | tag | sha |
|---|---|---|
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 |
| actions/setup-python | v7.0.0 | 5fda3b95a4ea91299a34e894583c3862153e4b97 |
| astral-sh/setup-uv | v10.1.0 | bec219d24cd3e171d82865faccec33120bb574f4 |
| actions/upload-artifact | v7.0.1 | 043fb46d1a93c77aae656e7c1c64a875d1fc6a0a |
| actions/download-artifact | v8.0.1 | 3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c |
| pypa/gh-action-pypi-publish | v1.14.2 | dc37677b2e1c63e2034f94d8a5b11f265b73ba33 |

## 验收证据（可复跑）

| 验收项 | 命令 | 结果 |
|---|---|---|
| 编译 | `.venv/Scripts/python.exe -m compileall -q src .github/scripts` | COMPILE_OK |
| 打包 | `uv build` | dist/mcp_for_maya-0.1.0-py3-none-any.whl + .tar.gz |
| 进程测活 | uv venv+uv pip install wheel → spawn mcp-for-maya.exe → stdio JSON-RPC initialize/tools-list/ping | serverInfo OK；toolCount=20；ping={} → PROCESS_ALIVE_OK |
| pytest | `.venv/Scripts/python.exe -m pytest tests/ -q` | **547 passed, 6 skipped, 0 failed**（基线 546+6+1fail，WinError64 转绿，无回归） |
| ruff 实测 | `.venv/Scripts/ruff.exe check src/tests --statistics` | src=174（=基线）、tests=63（fixable 29=46%）、repo=237 |
| 预算门 pass | `ruff check . --output-format=json` → `check_ruff_budget.py report baseline` | `src: 174/174 OK / tests: 63/63 OK`，exit 0 |
| 预算门 fail | 同上 vs `{"src":170,"tests":63}` | `src: 174/170 OVER` + `::error::`，exit 1 |
| YAML 有效 | python yaml.safe_load × 3 | YAML_OK |
| 脚本自身 lint | `ruff check .github/scripts/check_ruff_budget.py` | All checks passed |
| 首个 CI run | `gh run list` | run 35327567488 @ PR #8（结果见下文自证节） |

## CI 首跑自证（PR #8, run 35327567488 — 全绿）

`gh run view 35327567488`：6/6 jobs ✓
- ruff budget gate 9s ✓
- pytest (ubuntu-latest, 3.10) 25s ✓ / pytest (ubuntu-latest, 3.x) 27s ✓
- pytest (windows-latest, 3.10) 1m39s ✓ / pytest (windows-latest, 3.x) 1m8s ✓
- ci（汇聚）3s ✓

实测 check 名（分支保护清单用）：`ruff budget gate`、`pytest (ubuntu-latest, 3.10)`、`pytest (ubuntu-latest, 3.x)`、`pytest (windows-latest, 3.10)`、`pytest (windows-latest, 3.x)`、`ci`。
仅良性 annotation：setup-uv cache 预留竞争 warning + ubuntu-latest→26 迁移通知。Windows 格上 D-034 修复使 WinError64 测试在真实 Windows CI 同绿。

## DoD 核销

- [x] 全部文件落地；YAML 语法有效；SHA 注释与实际解析版本一致（gh api 实测表）
- [x] client.py 修复后本地 pytest 全绿（原 WinError64 项转绿）；PR 上 CI lint+4 格 test（首跑自证待回填）
- [x] ruff 预算文件=实测值；本地模拟超预算即 fail 已验证
- [x] fix/ci 分 commit（zon + tmu）；tests-fix 分支未触发（46%<80%）；预算下调规则写明（CONTRIBUTING+脚本提示）
- [x] 发布日/设置清单全项入档（见上 §11）
- [x] 基线不劣化：除既定修复外 pytest/ruff 无新增劣化（547+6+0、174/63/237 全持平）
- [x] but commit 到独立分支 `t10a/ci-quality-gates`；PR #8 已开；合并=用户人工门

## 负向清单自查

mypy 零进入 CI（无 blocking/continue-on-error）✓；无 skipif/注释掩盖（fix-forward 实修）✓；ruff select 规则集未动 ✓；CI 内不写预算文件（脚本只读）✓；不建 lock 文件 ✓；无 macOS 格 ✓；无 lowest-resolution/reviewdog/pre-commit ✓；零外部动作（pending publisher/environment/tag/Release/分支保护/PyPI/secret 全清单交付）✓；release.yml 不建 GitHub Release ✓；version/classifier/import 名/dist 名未动 ✓。

## 阻塞

- `but pr new` 报 forge 识别失败（remote 用自定义 SSH host `github-Xxx91n`，but 未解析为 github.com；OAuth 账号实测有效）→ 走 `but push` + `gh pr create` 兜底，stack 元数据缺失风险已在 PR body 披露 stacking 关系。

## Lessons 候选

1. Windows 上 ruff `--output-format=json` 输出**绝对路径**（Linux 相对路径）——分段脚本必须 `os.path.relpath(cwd)` 归一化，首版直接按 `parts[0]` 取段在本地即翻车（D: 段溢出）。跨平台 CI 脚本必须本地先模拟。
2. `but pr` 对自定义 SSH host alias 的 remote 不识别 forge——`but push` + `gh pr create` 兜底可行，代价是 stack base 元数据缺失。
3. ctx_execute 超长嵌套模板串易在中途损坏（一次五文件批写损坏过一次）——一文件一调用或数组拼行更稳。

## 引用文件

D:/Aworker/maya/maya-mcp-server/src/maya_mcp_server/client.py、D:/Aworker/maya/maya-mcp-server/.github/workflows/ci.yml、release.yml、dependabot.yml、ruff-baseline.json、scripts/check_ruff_budget.py、README.md、README_en.md、CONTRIBUTING.md、AGENTS.md、CHANGELOG.md；真源：.scratch/maya-mcp-grill/decision-ledger.md D-033..D-036、docs/adr/0015-first-ci-release-workflows.md、.scratch/maya-mcp-grill/handoffs/next-round.md rev14。
