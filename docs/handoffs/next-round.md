> 迁移注记（T-11a/D-041④）：本文件自 .scratch 迁入 docs/ 的规范副本；.scratch/ 已 gitignore（报告/audit/probe 等过程件仅存本地）。账本规范路径=docs/decision-ledger.md。

# Handoff — maya-mcp-grill 下一轮任务书（rev17）

> 生成时间：2026-09-18（T-11 锐评响应修复轮交付后）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-11a 诚实档完成**：tsn/xps/zmz/ktx @ `t11a/review-honesty` → **PR #12**（OPEN）。CHANGELOG 虚账已删；README 双语 Git 安装打头（PyPI 标未发布）；ADR-0003 accepted+未兑现注记；helper 括号闭合；client 死常量+撒谎注释清理；**.scratch 已迁 docs/ 且出 git 索引（本地 38 文件全保留）**
- **T-11b 代码档完成**：nkq/uon/zrz/mvt/xlo/okk @ `t11b/review-code-fixes` → **PR #13**（OPEN，base=t11a）。AE KeyError+dormant 机器可见标注；lookThru 生产调用全退场→modelPanel 命名 API；stub 类型感知消歧+warn/strict+偏离声明；native `\n` 终止符；native ConnectionError→MayaUnavailableError 对等映射；is_pc→DAG 前缀；cmds.* 签名经 atomcode 官方页核验全合法
- **spec-docs 档**：ouw @ `grill/round11-r2-review-spec-docs` → **PR #11**（OPEN）
- **issue #7 已增补四项** + D-040 未验证披露注记（0.1.0 alpha 真机未验明写）
- 基线现状：**pytest 557+6skip+0fail**；ruff src=174/tests=62（预算已从 63 ratchet 降至 62）；mypy=221（不入 CI）；pypi.org/pypi/mcp-for-maya 实测 404
- 账本 41 条（D-001..D-041；40 current+D-020 revised）；ADR 0001..0016；CONTEXT.md 29 术语
- T-11 实施报告：.scratch/maya-mcp-grill/reports/2026-09-18-t11-implementation.md

## 真源与上下文（先读这些）

- 决策账本 docs/decision-ledger.md（D-001..D-041）
- ADR docs/adr/0001..0016
- CONTEXT.md 29 术语
- T-11 实施报告 §3 如实披露；锐评原文 .codex_tmp/rui.txt
- PR #11/#12/#13（gh 视角确认合并状态，勿凭 but 猜）

## 工作约定（承袭）

- 写文件经 ctx_execute（node.js fs，绝对路径）；版本控制一律 but（禁 git 写命令）；每轮独立分支
- 授权分层：agent=文件/分支/issues/PR/**issue #7 编辑**；人工门=合并 main、tag、Release、PyPI、pending publisher、environment reviewer、分支保护
- 验收数字一律当次实测
- 已知坑：but pr 不识别 forge→but push+gh pr create --base <parent>；Windows ruff JSON 绝对路径需 relpath；冷 venv 首跑探针 >20s；ctx 沙箱 NODE_OPTIONS cm-fs-preload 缺陷→atomcode 经 exec 直跑+ctx_index 手动索引
- untrack 文件无 but 原语：删文件→but commit 删除→本地还原

## 下一任务：合并后验证 + 发布人工门（按序）

### T-12a 人工门（不可自动执行）

1. PR #11/#12/#13 评审合并（栈序：#11→#12→#13；合并栈顶自动携带祖先）
2. 0.1.0 发布序列（T-10a 报告 §11 全项）：pending publisher 预配→environment required reviewer→版本 classifier→tag v0.1.0→release.yml test→build→publish→gh release→分支保护 contexts→PyPI badge
3. 0.1.1 发布：T-11b 合并后 tag v0.1.1（CHANGELOG [0.1.1] 段已备）

### T-12b 合并后核对（agent 可做）

4. 合并后 but pull → 全量验证复跑（pytest/ruff/compileall/uv build/stdio smoke）确认栈合入无回归
5. docs/handoffs/next-round.md 翻 rev18 记合并后基线
6. 登记债分流：issue 化或保留（见下）

### 登记债（碰到再修，勿认领）

- **T-06 休眠代码处置**：aesthetic_engine.py 注入/consolidation 决策（ADR-0003 注记指向）——机器可见标注已就位（模块头 DORMANT/AGENTS 联动行/CONTRIBUTING 预算说明/测试披露）
- ctx 沙箱 cm-fs-preload 缺陷；57 条 AE zombie 测试=dormant 覆盖（如实披露）；Maya 2022+ commandPort Qt 重写内部未公开；真机 \n 语义实证挂 issue #7
- 沿用：D-011/ADR-0008 validator 未实现；_suggest_layout 截断；checked/skipped 异构；orbit_cam/shot_cam 前缀；玄学评分；test_security.py:389 I001；AsyncMock never-awaited；connection_guide 三连；ADR-0010 O-2；_probe_port 泄漏；native 丢 code；visual_module 真机项；_visual_injected 重连；双胞胎 helpers；Scene.gui/_ViewWidget/_MAGIC.get；OSError errno 白名单；ruff 原生 baseline(#1149)；uvx ruff 浮动；but pr forge；pending publisher 锁名窗口；||true 吞退出码；ci↔release 重复；unavailable 消息丢 {e}；budget argv 防护；Qt Raises docstring

## DoD checkbox（下一轮）

- [ ] 合并后 pytest 557+skip 仍全绿；ruff src=174/tests=62 预算不升
- [ ] issue #7 实机 checklist 项如实推进（有 Maya 环境才可勾）
- [ ] 发布动作均人工执行且留 gh 证据链
- [ ] PyPI 发布后 README PyPI 段由"即将"改实链（诚实项闭环）

## 负向清单

- 合并/tag/Release/PyPI/publisher/分支保护不自动执行
- T-06 休眠代码不提前注入；dormant 标注不删
- 不动已 OPEN PR 的历史（amend/rebase pushed 分支须用户批准）

## suggested skills

- 合并后验证/发布陪跑：implement → code-review；调研 atomcode-research（exec+ctx_index 模式）
- 收尾：handoff、neat-freak；版本控制 gitbutler（but）
