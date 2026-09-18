# T-09 发布卫生实施报告（D-028..D-032）

> 日期：2026-09-18 · 执行：修复/开发子 Agent · 基线环境：.venv Py3.13，Windows 11
> 真源：next-round.md rev13 + decision-ledger D-028..D-032 + ADR-0014

## 交付物核销

### 1. LICENSE（D-030②）✅
MIT 全文 + 双行版权（上游 notice 法律义务保留）。
- 证据：`head -5 LICENSE` → `MIT License / Copyright (c) 2026 Chad Dombrova / Copyright (c) 2026 Xxx91n`；1096 bytes、LF、无 BOM。

### 2. pyproject.toml 身份字段（D-029/D-032①）✅
`git diff pyproject.toml` 净变更=4 处：`name="mcp-for-maya"`；description 对齐新叙事；`[project.scripts]` 双入口 `mcp-for-maya`+`maya-mcp-server` 同指 `maya_mcp_server.__main__:main`；urls 三条→`github.com/Xxx91n/mcp-for-maya`。version=0.1.0 与 classifier 3-Alpha **未动**（diff 中无对应行）。

### 3. README.md + README_en.md（D-030①）✅
结构重排 + 全量修错，逐项：
- (a) “与 blender-mcp 对比”诚实三档节（我方独有 ICEV/CoS/checkpoint/注册表/11 项审核/带元数据 playblast vs 它方资产生态/CRUD/AI-gen vs 共有 MCP 面/截图/exec/socket）。
- (b) 审核维度统一 11 项，分值表按 maya_scene_module 实测 max_score：spatial10/overlaps10/conflicts10/zones5/naming5/components10/orphans5/aesthetics15/lighting10/organization10/constraints5（源：maya_scene_module.py:2772-3267）。
- (c) 65% 如实归因：“该格式论文报告在其演示场景上较 JSON 节省约 65% token（arXiv:2305.10276，-65.8%）——论文测量值而非本项目基准测试”。
- (d) 安装改 `pip install mcp-for-maya` + `uvx mcp-for-maya`；[!NOTE] 三层命名（dist/import/script）一行说明。
- (e) Skills 幻影删除→真实 `skills/` 两卡 + Experimental 声明 + issue #3 指向。
- (f) clone URL→`github.com/Xxx91n/mcp-for-maya`。
- (g) 信任段：zero telemetry, no phone-home + 本地单用户 + 安全网（校验/限流 100/20 每 60s/pattern warn-only/JSONL 审计）如实描述，无 sandbox/secure 字样。
- (h) 版本策略节：semver + 0.x→4-Beta（feature-complete+外部测试）→1.0.0+5-Production/Stable 晋升条件 + 里程碑驱动不承诺周期。
- 证据：`grep -c '^## ' README.md`=14 节无重复；11 维度表行数=11；`grep '9 维\|maya-mcp-server-enhanced\|pip install maya-mcp-server'` 两文件均零命中。

### 4. AGENTS.md（D-030①）✅
- `LOGLEVEL=DEBUG python -m maya_mcp_server` → `python -m maya_mcp_server -vv`（-v=INFO/-vv=DEBUG，对齐 __main__.py argparse）。
- `python scripts/secrets.py` / `python scripts/dependency.py` 幻影两行删除；保留真实存在的 semgrep 行。
- 审核维度表 9 行错值 → 11 行代码实值（同 README）。
- CoS 行 ~65% → 论文归因表述。
- 证据：`git diff AGENTS.md` 净变更 26 行，仅上述区域；`grep LOGLEVEL\|scripts/ AGENTS.md` 零命中。
- 附带修复：文件原有混合行尾（上段 LF/下段 CRLF）已归一 LF，与 .gitattributes eol=lf 一致。

### 5. skills/（D-031①）✅
`skills/icev-workflow/SKILL.md`（48 行）+ `skills/scene-review-playbook/SKILL.md`（51 行，复审后）：
- frontmatter：name 小写连字符==目录名；description≤1024（实测 347/343 字符）；`compatibility: "Tested on Claude Code only; requires mcp-for-maya MCP server"`。
- 正文含 "Experimental. Evaluated on Claude Code only; untested on Codex/Gemini CLI/Cursor. Tracked in issue #3."。
- 纯流程卡、单文件、远小于 500 行，无需 references/。

### 6. CHANGELOG.md（D-032②）✅
Keep a Changelog 1.1.0 头 + semver 声明 + [Unreleased] 段（Added/Changed/Fixed/Removed），内容为 fork 全量增量（可对源核销）。

### 7. CONTRIBUTING.md（D-032②）✅
最小三节：dev setup（pip/uv -e ".[dev]"+pytest+ruff+mypy+-vv）、PR 流程（conventional commits + 基线门）、行为准则引用（Contributor Covenant v2.1 外链，不建 CODE_OF_CONDUCT 文件）。

### 8. SECURITY.md / threat-model.md / docs（传播矩阵）✅
仅同步改名所致 stale：SECURITY.md 产品名→mcp-for-maya；threat-model.md 标题→mcp-for-maya。ADR 历史件不改写；testing.md 本地路径属本机事实保留。

### 9. GitHub 侧（D-028③/D-031②/D-032③）✅（issues）/ 待用户（改名）
- 六 roadmap issues 已建：
  - #2 [Roadmap v1.1] Poly Haven thin-slice（含 asset 类型/缓存/无网降级 AC）
  - #3 [Roadmap v1.x] Skills program（含跨模型评测计划）← skills 卡 #N 指向
  - #4 [Roadmap v1.x] Security & permission model（safe_mode 子任务）
  - #5 [Roadmap v1.x] export_scene + 场景图内省
  - #6 [Exploratory] asset sources beyond Poly Haven
  - #7 真机验证清单 + v1.0 feedback/triage（已 pin）
- #N 已回填：skills 两卡正文 Tracked in issue #3；README 技能节+路线图节引用 #2/#3/#4/#5/#6/#7。

## 改名命令清单（人工确认门交付）

```bash
# 1) 改名（高副作用一次性公开行为，由用户执行）
gh repo rename mcp-for-maya --repo Xxx91n/maya-mcp-server-enhanced
# 2) 本地 remote 跟随
git remote set-url origin git@github-Xxx91n:Xxx91n/mcp-for-maya.git
# 3) 改名后检查 Actions 对旧 owner/repo@ref 的引用（Actions 引用不随重定向）；本仓库尚无 .github/，T-10a 落地时直接写新名
# 4) 绝不在旧名 maya-mcp-server-enhanced 下重建仓库（重定向链会断）
```
已按新名写就的文件：README.md / README_en.md（clone URL+issue 引用）、pyproject.toml（Homepage/Repository/Issues）。
⚠️ PyPI 元数据 URL **不随 GitHub 重定向**——首次发布前确认 pyproject urls 已指新名（本轮已写好）。

## 发布日清单（入档）

- [x] PyPI `mcp-for-maya` 空闲确认：2026-09-18 `GET https://pypi.org/pypi/mcp-for-maya/json` → 404（空闲）
- [x] 手动 pytest+build：546 passed+6 skip+1 既有环境失败；`uv build` → mcp_for_maya-0.1.0 wheel+sdist
- [ ] Trusted Publishers 发真实 0.1.0（或按 D-021 留 v1.0.0）——人工门
- [ ] tag/release——人工门

## 验收证据（可复跑）

| 验收项 | 命令 | 结果 |
|---|---|---|
| 编译 | `.venv/Scripts/python.exe -m compileall -q src` | COMPILE_OK |
| 打包 | `uv build` | dist/mcp_for_maya-0.1.0-py3-none-any.whl + .tar.gz |
| 包内容 | zipfile 读 wheel | 21 个 maya_mcp_server/ 文件；entry_points 双 script；METADATA Name=mcp-for-maya，urls 新仓库，License-Expression MIT + LICENSE 入包 |
| 安装测活 | `uv venv`+`uv pip install dist/...whl` → `mcp-for-maya.exe --help` | argparse CLI 正常（-v/-vv/--client-type/--scan-interval） |
| 进程测活 | node stdio smoke（initialize→tools/list→ping→tools/call） | serverInfo OK；**toolCount=20**；hintGaps=[]；ping={}；os.system 载荷被 [blocked_pattern] 拦截 |
| pytest | `.venv/Scripts/python.exe -m pytest tests/ -q` | 546 passed, 6 skipped, 1 failed（test_qt_channel WinError 64，归 T-10a 的既有环境项）= 基线 |
| ruff src | `ruff check src` | 174 errors = 基线 |
| ruff repo | `ruff check .` | 237 errors = 基线 |
| mypy | `python -m mypy src`（系统 Python 2.1.0） | 221 errors = 基线 |

## DoD 核销

- [x] 1-8 文件全落地且与代码实测一致（README 每个数字已对源：20 工具=5 server+13 scene+2 visual；11 checks+分值=maya_scene_module max_score；5 审美维=analyze_aesthetics weights）
- [x] 六 issues 已建、#N 已回填 skills 卡与 README
- [x] 改名命令清单已交付用户（含 PyPI URL 不随重定向提醒）
- [x] 基线不劣化：pytest/ruff/mypy 跑平（docs-only，src/ 零改动——`git status` 无 src/ 变更）
- [x] 发布日清单入档（见上）
- [ ] but commit 到新分支（本报告提交时一并完成）

## 负向清单自查

不发 PyPI（零发布动作）✓；不改 import 名（src/maya_mcp_server/ 未动）✓；不动 version/classifier（0.1.0+3-Alpha）✓；不建 CODE_OF_CONDUCT/Dockerfile ✓；不做 typed-skill 重路线 ✓；README 无 sandbox/secure 描述安全网 ✓；telemetry 写“零遥测”非“默认关” ✓。

## 遗留（未做≠未写，环境限制）

1. mayapy Tier2 / GUI Tier3 八项（无本机 Maya）→ 已入 issue #7 清单。
2. MCP Inspector+Claude Code+Codex 多 block 实测（D-025④）→ issue #7。
3. PySide2 真机兼容、T-05 R-2 headless fallback 真机 → issue #7。
4. test_qt_channel WinError 64（RST/FIN 语义差）→ T-10a Linux CI 复核。

## 复审返工（F-1..F-4 + R-1 核销）

- **F-1（实质）**：phantom validator 注册机制——src/ 实测无 register/check_error（D-011 决策未实现且原文“非发布卖点”）。已从 README 双语对比档移除（替换为真实 scene_plan 规划），SKILL.md “Custom validators” 节删除，改为如实声明 “designed (ADR-0008) but not yet implemented”。
- **F-2**：issues[] 实为 {severity,check,msg}（计数/建议文案），对象名在 checks[].details/examples（采样列表）。SKILL.md 已按实形状改写。
- **F-3（判断项，保留）**：README_en 与中文版平行同步的 Option C/平台表/Troubleshooting/环境要求属 spec “README_en 平行同步”授权范围，内容均对源核实，保留并在此披露。
- **F-4**：SKILL.md 删除 max pts 列（第四份分值副本逃逸传播矩阵），并已在 AGENTS.md 联动表新增 skills/ 卡同步行。
- **R-1**：报告数字订正——README h2 实测 14（非 15）、skills 卡 wc -l 实测 48/51（split 计数差 1 误报为 49/52）。

## 变更文件

D:\Aworker\maya\maya-mcp-server\LICENSE（新）、D:\Aworker\maya\maya-mcp-server\CHANGELOG.md（新）、D:\Aworker\maya\maya-mcp-server\CONTRIBUTING.md（新）、D:\Aworker\maya\maya-mcp-server\skills\icev-workflow\SKILL.md（新）、D:\Aworker\maya\maya-mcp-server\skills\scene-review-playbook\SKILL.md（新）、D:\Aworker\maya\maya-mcp-server\pyproject.toml、D:\Aworker\maya\maya-mcp-server\README.md、D:\Aworker\maya\maya-mcp-server\README_en.md、D:\Aworker\maya\maya-mcp-server\AGENTS.md、D:\Aworker\maya\maya-mcp-server\SECURITY.md、D:\Aworker\maya\maya-mcp-server\docs\threat-model.md
