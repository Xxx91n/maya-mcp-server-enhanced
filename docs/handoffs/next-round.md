> 迁移注记（T-11a/D-041④）：本文件为 next-round.md rev16 自 .scratch 迁入 docs/ 的规范副本；.scratch/ 已 gitignore（报告/audit/probe 等过程件仅存本地）。账本规范路径=docs/decision-ledger.md。

# Handoff — maya-mcp-grill 下一轮任务书（rev16）

> 生成时间：2026-09-18（第二轮锐评响应 grill 定稿）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- 第二轮锐评（.codex_tmp/rui.txt，audit @ aed9298）全条目辩证复核完毕：**8 实锤+1 夸大（lookThru“必炸”）+1 驳回（总分100 引用张冠李戴）**
- T-10a 全闭环：PR #8 已合并（aed9298）CI 绿；审计 PASS（140901f）；上游 PR #10 已合并——**本地落后 origin/main 2 commits，实施前先 but pull 并核对**
- 账本 41 条（D-001..D-041；40 current+D-020 revised）；本轮新增 D-037..D-041
- 基线勿劣化：pytest 547+6skip+0fail；ruff src=174/tests=63/repo=237；mypy=221（不入 CI）；pypi.org/pypi/mcp-for-maya 实测 404
- ADR 新增 0016（锐评响应治理）；CONTEXT.md 29 术语（新增**休眠代码**）

## 真源与上下文（先读这些）

- 决策账本 docs/decision-ledger.md（D-001..D-041）
- ADR docs/adr/0001..0016
- CONTEXT.md 29 术语
- T-10a 实施报告（含发布日清单全项）.scratch/maya-mcp-grill/reports/2026-09-18-t10a-implementation.md §11
- 锐评原文 .codex_tmp/rui.txt；审计交接 .scratch/maya-mcp-grill/handoffs/audit-t10a-passed.md

## 工作约定（承袭+新增）

- 写文件经 ctx_execute（node.js fs，绝对路径）；版本控制一律 but（禁 git 写命令）；每轮独立分支
- 授权分层：agent=文件/分支/issues/PR/**issue #7 编辑**；人工门=合并 main、tag、Release、PyPI、pending publisher、environment reviewer、分支保护
- 验收数字一律当次实测
- 已知坑：but pr 不识别 github-Xxx91n SSH alias→but push+gh pr create；Windows ruff JSON 输出绝对路径需 relpath 归一化；冷 venv 首跑探针 >20s；**ctx 沙箱 NODE_OPTIONS cm-fs-preload 缺陷→atomcode 经 exec 直跑+ctx_index 手动索引**（不杀进程、串行单发）
- untrack 文件无 but 原语：删文件→but commit 删除→本地还原（.gitignore 生效后不再跟踪），或 git rm --cached 属 git 写命令须用户批准例外

## 下一任务：T-11 锐评响应修复轮（两档）

### T-11a 诚实档（0.1.0 前置，独立分支+PR）

1. CHANGELOG.md:33 删虚账（改写为事实或直接删除该条）[D-037/D-038]
2. README.md+README_en.md 安装段重排：源码/uv tool install git-url 打头，PyPI 标“即将（0.1.0 发布中）”[D-037]
3. ADR-0003 追加 status 注记（未兑现 as of 0.1.0 / consolidation deferred to T-06 / 内联版为现役实现）[D-038]
4. maya_mcp_helper.py:261-263 括号闭合 [D-037]
5. client.py:49-50 删 DEFAULT_MAX_RETRIES/DEFAULT_RETRY_DELAY 两死常量+:346 注释改写实际行为（Qt JSON 协议/不重试/错误透传）[D-041②]
6. **.scratch 迁移**：decision-ledger.md+current handoff 迁 docs/（落位建议 docs/decision-ledger.md+docs/handoffs/）；.gitignore 加 .scratch/；untrack 全目录保本地；全部路径引用同步（AGENTS.md/工作约定/后续 grill 模板）[D-041④]

### 人工门：0.1.0 发布（T-10a 报告 §11 全项，插队位=D-037③）

pending publisher 预配→environment required reviewer→版本 classifier 决策→tag v0.1.0→release.yml 自动 test→build→publish→gh release create→分支保护 contexts=实测 check 名→PyPI badge（?cacheSeconds=300）

### T-11b 代码档（0.1.1，新分支）

7. AE KeyError：aesthetic_engine.py:910 layers other→unclassified + 模块头 dormant 标注 + AGENTS.md 联动表+ruff 基线说明写休眠状态 [D-038]
8. visual_module.py：三处 lookThru→modelPanel 命名 API——:162 主路径 modelPanel(panel,e=True,camera=cam)；:170 恢复先 modelPanel(q=True,camera=True) 查询再赋回；:179 单参兜底删除 [D-039]
9. stub：lookThru/modelPanel 类型感知消歧（panel/editor 名 vs camera/DAG 名按类型识别）+warn 默认/strict 可选+docstring 声明偏离；顺带过 stub 其他 cmds.* 伪造语义面 [D-039]
10. client.py:464 无条件 +b"\n" [D-041①]
11. native _send_receive 补 ConnectionError→MayaUnavailableError 对等映射——**单独 commit+typed-error 回归测试**（test_client.py 惯例）[D-041③]
12. maya_scene_module.py:2824-2825 is_pc 裸子串→DAG 路径前缀（a+"|" 或 commonpath）[D-037]
13. visual_module 全部 cmds.* 调用（~10 API）人工签名对照+发现项记录 [D-039④]

### issue #7 编辑（agent 授权内）

增补四项：cmds.* 调用面静态签名审计（含 M 端 maya_scene_module）/mayapy 签名采集→stub 回填合约护栏/smoke 覆盖 lookThru-modelPanel 调用形态/无 \n 命令+500ms 读实证 [D-039③/D-041①⑤]

### 文档同步（传播矩阵）

AGENTS.md（docs/ 结构+ dormant 联动行+.scratch 移除）/CONTRIBUTING.md（dev 流程若受影响）/CHANGELOG Unreleased（T-11b 条目归 0.1.1 段）/README 如需

## DoD checkbox

- [ ] pytest 547+skip 全绿（native 对等映射回归测试+1；modelPanel 迁移后 visual 测试经 stub 消歧承接全绿）
- [ ] ruff src=174/tests=63 预算不升（删行则同 PR 降预算，禁 CI 内自动写）
- [ ] CHANGELOG 无未兑现声明；ADR-0003 注记可读；README 双语安装段首条命令可实际执行
- [ ] .scratch 出 git 索引且本地文件全保留；docs/ 下账本+handoff 可达
- [ ] issue #7 四项已增补；全仓无 lookThru 调用残留（含 stub 外文档提及）

## 负向清单

- ADR-0003 status 不改 proposed/superseded（保 accepted+注记）；不另起 supersede ADR
- 不在 T-11 兑现 AE 注入；不删 aesthetic_engine.py；dormant 标注不只做 docstring
- 不接线 retry；不 skip 测试；不写“已修复”未实测项；不在 CI 内自动改预算
- stub 不做无条件 raise；全仓不保留任何 lookThru 调用
- 不顺手修无回归测试的行为修正；cleanup 与行为修正分 commit
- 不执行发布/合并/tag/Release/pending publisher/分支保护等外部动作

## 登记债（碰到再修，勿认领）

- **新增**：ctx 沙箱 cm-fs-preload 缺陷；57 条 AE zombie 测试=dormant 覆盖（549→492 真实数如实披露）；Maya 2022+ commandPort Qt 重写内部未公开；57 测试或含内联契约验证未实测
- 沿用：D-011/ADR-0008 validator 未实现；_suggest_layout 截断；checked/skipped 异构；orbit_cam/shot_cam 前缀；玄学评分；test_security.py:389 I001；AsyncMock never-awaited；connection_guide 三连；ADR-0010 O-2；_probe_port 泄漏；native 丢 code；visual_module 真机项；_visual_injected 重连；双胞胎 helpers；Scene.gui/_ViewWidget/_MAGIC.get；OSError errno 白名单；ruff 原生 baseline(#1149)；uvx ruff 浮动；but pr forge；pending publisher 锁名窗口；||true 吞退出码；ci↔release 重复；unavailable 消息丢 {e}；budget argv 防护；Qt Raises docstring

## suggested skills

- T-11 实施：implement → tdd（native 对等映射等 seam）→ code-review
- 调研：atomcode-research（经 exec+ctx_index 模式）
- 收尾：handoff、neat-freak；版本控制 gitbutler（but）；文档 domain-modeling、writing-for-agents
