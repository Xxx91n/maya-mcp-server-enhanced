# Handoff — maya-mcp-grill 下一轮任务书（rev13）

> 生成时间：2026-09-18（T-09 grill 定稿 D-028..D-032）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-08 已关闭并合入 main**（d0f6f77）；T-09 spec 五问闭合：D-028 范围边界 / D-029 三层命名 / D-030 README+LICENSE+telemetry / D-031 skills+issues / D-032 版本+文档骨架+授权门。
- **基线复核（勿劣化；规范环境=.venv Py3.13）**：pytest 546+6skip+1 既有环境失败（test_qt_channel WinError 64 RST/FIN 语义差，归 T-10a Linux CI 复核）；ruff src=174/repo=237；mypy=221；compileall+wheel+stdio 全绿。
- **T-09 不写源码**——它是文档/身份/仓库设置任务；唯一 pyproject 改动=身份字段（name/scripts/urls/description/classifier 保持 3-Alpha、version 保持 0.1.0）。

## 真源与上下文（先读这些）

- 决策账本：.scratch/maya-mcp-grill/decision-ledger.md（D-001..D-032）
- 术语表 CONTEXT.md（27 术语）；ADR docs/adr/0001..0014（0014=发布身份与卫生策略）
- AGENTS.md 联动规范；docs/threat-model.md §5 工具矩阵
- rui.txt（.codex_tmp/）——dated artifact，仍开着的 P2 项=T-09 清扫对象
- 锐评复核基线：上一轮会话已对 rui.txt 全条目实物核销（见 git log ad571ca 前各 T 提交）

## 工作约定（承袭）

- 写文件经 ctx_execute（node.js fs）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- 新决策先入 D-xxx；文档传播矩阵：本任务（T-09）是授权清扫方——全部 stale 行归本任务，不再“留后续”。
- **授权分层（D-032③）**：agent 自主=文件/分支/issues/PR；人工确认门=repo 改名、push main、tag、Release、PyPI、secret。
- README 撰写遵循 skills/git/readme/create-readme（GFM+GitHub admonition、克制 emoji、不含 LICENSE/CONTRIBUTING/CHANGELOG 节）。

## 下一任务：T-09 发布卫生实施（D-028..D-032）

### 交付物清单

1. **LICENSE**（D-030②）：MIT 全文+双行版权 `Copyright (c) 2026 Chad Dombrova`（上游 notice 保留=法律义务）+ `Copyright (c) 2026 Xxx91n`。
2. **pyproject.toml**（D-029/D-032①）：`name="mcp-for-maya"`；`[project.scripts]` 双入口 `mcp-for-maya`+`maya-mcp-server` 同指 `maya_mcp_server.__main__:main`；urls 三条→`github.com/Xxx91n/mcp-for-maya`；version=0.1.0 与 classifier 3-Alpha **保持不动**；description/keywords 可对齐新叙事。
3. **README.md + README_en.md**（D-030①）：结构重排+全量修错——(a) “对比 blender-mcp”诚实三档节；(b) 11 维统一（代码真源：11 checks，分值表按 maya_scene_module max_score 实值）；(c) 65%→论文数字如实归因或去数；(d) pip install→`mcp-for-maya`+`uvx mcp-for-maya`（D-029 script 名）+dist/import 对应关系一行说明；(e) Skills 幻影→真实交付 skills/ 两卡（D-031）；(f) clone URL→新仓库名；(g) 信任段写 zero telemetry, no phone-home；(h) Versioning 小节（semver+0.x→Beta→1.0 晋升条件+里程碑驱动不承诺周期）。
4. **AGENTS.md**（D-030①）：`LOGLEVEL=DEBUG`→`-v/-vv` 实值；`scripts/secrets.py``scripts/dependency.py` 幻影删（或如实标注工具缺失）；审核维度表对齐 11 维；security 行已在。
5. **skills/**（D-031①）：`icev-workflow/SKILL.md`+`scene-review-playbook/SKILL.md`——spec frontmatter（name 小写连字符≤64 匹配目录名、description≤1024 写 what+when、`compatibility: "Tested on Claude Code only; requires mcp-for-maya MCP server"`）+正文显式 Experimental 声明+Tracked in issue #N+每卡≤3 模块<500 行、细则移 references/。
6. **CHANGELOG.md**（D-032②）：Keep a Changelog 1.1.0 格式+[Unreleased] 段+semver 声明。
7. **CONTRIBUTING.md**（D-032②）：最小三节——dev setup（uv/pip -e.[dev]+pytest+ruff+mypy）、PR 流程（conventional commits）、行为准则引用。
8. **SECURITY.md / threat-model.md / docs/**：仅同步改名所致 stale 引用（传播矩阵），不重写内容。
9. **GitHub 侧**（D-028③/D-032③）：(a) 六 roadmap issues 由 agent 经 gh 直建（清单见 D-031②，建好把 #N 回填 skills 卡与 README）；(b) **repo 改名入人工门**——备好 `gh repo rename mcp-for-maya` 命令+受影响文件清单（README/pyproject/CI 徽章位）交付用户；改名后检查 Actions 旧 owner/repo@ref 引用。

### DoD

- [ ] 上述 1-8 文件全落地且与代码实测一致（README 每个数字可对源）
- [ ] 六 issues 已建、#N 已回填 skills 卡与 README
- [ ] 改名命令清单已交付用户（含 PyPI URL 不随重定向提醒）
- [ ] 基线不劣化：pytest/ruff/mypy 跑平（docs-only 变更预期零波动）
- [ ] 发布日清单入档：PyPI 名空闲确认→手动 pytest+build→Trusted Publishers 发真实 0.1.0 或留 v1.0.0→tag/release 入人工门
- [ ] but commit 到新分支（docs-only，不动 src/）

### 负向清单

- 不发 PyPI 任何东西（空包/0.0.1 占位=违规）；不改 import 包名；不动 version/classifier；不建 CODE_OF_CONDUCT/Dockerfile（Maya 桌面不可容器化）；不做 typed-skill 重路线；README 不出现 sandbox/secure 字样描述安全网（D-008）；telemetry 不写“默认关”（写的是“零遥测”）。

## 遗留真机窗口清单（环境限制，未做≠未写）

1. mayapy Tier2 与 GUI Tier3 八项（docs/testing.md）——本机无 Maya；2. MCP Inspector+Claude Code+Codex 多 block 实测（D-025④）；3. PySide2 真机兼容；4. T-05 R-2 headless fallback 真机。

## 其后任务速览

- **T-10a**：GH Actions pytest+ruff 最小门（发 v1.0 前置）；**发布 v1.0.0**（人工门）；**T-10b** 完整质量门；**T-12** Poly Haven v1.1；**T-06/T-07** 内部债。

## 登记债（碰到再修，勿认领）

- _suggest_layout pair-window 截断未披露；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分语义重设计（D-014d）
- test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited；connection_guide 版本扫描复制粘贴三连
- ADR-0010 O-2；_probe_port socket 泄漏（O-5）；native _send_receive 丢 code（R-1 微瑕）
- visual_module verticalFlip 防御默认待 Tier3；lookThru 参数序真机复核；cmds.refresh 异常静默可能回旧帧
- _visual_injected/_injected_sessions 重连跳过重注入；_visual_call/_exec_visual 与 scene_tools 同形双胞胎（绞杀者归并时收）；Scene.gui/_ViewWidget/_MAGIC.get 死面

## suggested skills

- 执行：implement + create-readme（README 重写规范）；评审：code-review；文档：domain-modeling
- 调研：atomcode-research（PyPI 名空闲确认可联网查证）；收尾：handoff、neat-freak；版本控制：gitbutler（but）
