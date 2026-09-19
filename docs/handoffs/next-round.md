# Handoff — maya-mcp-grill 下一轮任务书（rev18）

> 迁移注记（T-11a/D-041④）：本文件自 .scratch 迁入 docs/ 的规范副本；.scratch/ 已 gitignore（报告/audit/probe 等过程件仅存本地）。账本规范路径=docs/decision-ledger.md。

## 本轮验收事实（非计划）

- **rui.txt 锐评全闭环**（D-042）：64 行第二轮锐评 @aed9298 逐条对当前树（=origin/main ce38cfa，git diff 为空）取证——8 实锤全修复、1 夸大（lookThru 必炸）与 1 驳回（总分 100）维持注记；剩余仅 by-design 挂账（#7 真机/T-06 T-07 T-10b 登记债）
- **发布面**：PR #11/#12/#13 MERGED；tag v0.1.0@f88e75a / v0.1.1@ce38cfa；GitHub Release 双版已建；**PyPI 已发布 [0.1.0,0.1.1] latest=0.1.1**
- **基线实测**：pytest 564 passed/4 skipped；ruff src=174/tests=62；mypy 223/3 文件（≈184 M+38 AE+16 scene_tools）；ruff 0.15.20 / mypy 2.1.0 / pytest 9.1.1；`ruff format --check`=37/48 文件未格式化
- **mypy-baseline smoke 已过**（mypy 2.1.0）：sync 捕 223→filter 0 新错；mypy-baseline.txt 已生成未提交（T-10b⑦正式产物先行版，实施时 sync 重生）
- 账本 45 条（D-001..D-045；44 current+D-020 revised）；ADR 0001..0017；CONTEXT.md 30 术语（+棘爪）

## 真源与上下文（先读这些）

- 决策账本 docs/decision-ledger.md（D-001..D-045）
- ADR docs/adr/0001..0017（0017=T-10b spec 全链）
- CONTEXT.md 30 术语
- 锐评原文 .codex_tmp/rui.txt（已全闭环，仅存档）
- T-12a 报告 .scratch/maya-mcp-grill/reports/2026-09-19-t12a-merge-release.md

## 工作约定（承袭）

- GitButler 专用（but commit/branch；禁 git write）；文件写走 Node.js fs（ctx_execute）+字节校验
- 每修复带回归测试（CONTRIBUTING 惯例）；诚实档与代码档分 commit
- atomcode 调研串行单发；ctx 沙箱 cm-fs-preload 缺陷→exec 直跑+ctx_index 手动索引
- 人工门：merge/tag/release/PyPI/分支保护/env reviewer=用户执行

## 任务链（按序）

### T-12c 微补丁档（D-042；docs 级，先行）

1. README.md+README_en.md PyPI 段：“即将推出（0.1.0 发布中）”→实链——`pip install mcp-for-maya`/`uvx mcp-for-maya` 恢复首选位，git 安装留备选
2. PyPI badge ?cacheSeconds=300 入双语 README 徽章行（现仅 CI badge）
3. mypy 221→223 漂移记账确认（登记债已含，rev18 记实测数为准）
4. 人工门尾巴（不自动执行）：分支保护 main contexts=实测 check 名（T-10b 新增 job 后列表会变→宜 T-10b 合并后配）；environment pypi required reviewer

### T-10b 质量门深化（D-044/D-045/ADR-0017；源码+CI 级）

5. .pre-commit-config.yaml：pre-commit-hooks（check-yaml/check-merge-conflict/check-case-conflict/end-of-file-fixer/trailing-whitespace/debug-statements）+astral-sh/ruff-pre-commit 的 ruff-check+ruff-format（rev 与 CI ruff 对齐；注意 uvx ruff 浮动债）
6. **mass reformat 独立 commit**：`ruff format .`→“style: no logic changes”纯格式零逻辑→完整 40 位 SHA 入 .git-blame-ignore-revs→重跑 ruff check 实证计数不跳升（跳升则重基线说明）→E501 移交 formatter 后评估 ignore
7. mypy 基线闸：dev-dep mypy-baseline（pin≥7 天版本）→CI 新 job `python -m mypy src/ | mypy-baseline filter`→mypy-baseline.txt 入库→pyproject [tool.mypy] 增 warn_unused_ignores+warn_unused_configs 棘爪→CONTRIBUTING/AGENTS.md 补 sync 流程说明
8. per-rule ruff：check_ruff_budget.py 升 (rule→count) dict+ruff-baseline.json 一次性迁移
9. coverage 报告态：dev-dep pytest-cov+`pytest --cov` 跑基线人工读一次（不设门）
10. CI 兜底：GHA 步 `pip install pre-commit && pre-commit run --all-files`（contents:read 自托管）
11. Dependabot pre-commit ecosystem 月度（或手动 autoupdate 文档化）
12. 顺带候选（碰到再修）：uvx ruff 浮动→同面 boy-scout pin（登记债已有）

### 下一轮（D-043）

13. issue #7 真机验证推进（D-040 v1.0.0 定义性前提；需用户 Maya 环境——agent 备 mayapy harness+逐项脚本，勾选须真机）

## DoD checkbox（T-12c+T-10b）

- [ ] README 双语 PyPI 段=实链+badge 正常渲染
- [ ] `pre-commit run --all-files` 本地全绿
- [ ] mass reformat commit 纯格式（stat 全为空白/引号/换行级）+SHA 入 ignore-revs
- [ ] reformat 后 ruff check 计数不跳升（实测记录数字）
- [ ] CI mypy job 绿（filter 0 新错）+旧错修复后 sync 重基线演示一次
- [ ] per-rule baseline JSON 迁移后预算门仍只降不升
- [ ] pytest --cov 基线数字入实施报告（不设门）
- [ ] pytest 564+skip 全绿不回退；ruff 预算不升

## 负向清单

- 不装 pre-commit.ci（D-045 供应链通道）；不用 staged-only 渐进格式；mypy 不进 pre-commit 钩；coverage 不设绝对阈值门；macOS 不进全矩阵；mass reformat 零逻辑混入；mypy-baseline.txt 不在本档提交（属 T-10b⑦产物）
- 不顺手修登记债（uvx ruff pin 仅 boy-scout 候选）；不动 issue #7 checkbox（无 Maya 环境不可勾）；不把 dormant 测试计入生产覆盖叙事

## 登记债（碰到再修，勿认领）

- coverage patch 门触发=T-06 归置+真机档；macOS 单冒烟触发=pypistats 用户实证/真实 macOS bug/macOS 产物；pre-commit.ci 若未来豁免最小依赖姿态可后补；ruff format E501 ignore 评估挂 reformat 步
- 沿用 rev17：T-06 休眠归置/ctx 沙箱 preload 缺陷/57 条 AE dormant 覆盖披露/Maya 2022+ commandPort 未公开/D-011 validator/_suggest_layout 截断/checked-skipped 异构/orbit-shot 前缀/玄学评分/test_security:389 I001/AsyncMock/connection_guide 三连/ADR-0010 O-2/_probe_port 泄漏/native 丢 code/visual_module 真机项/_visual_injected 重连/双胞胎 helpers/Scene.gui 等/OSError 白名单/ruff 原生 baseline(#1149)/uvx ruff 浮动/but pr forge/pending publisher/||true/ci↔release 重复/unavailable 消息丢 {e}/budget argv/Qt Raises

## suggested skills

- $but（GitButler）— 全部版本控制写操作
- $implement / tdd — T-10b 实施驱动
- $atomcode-research — 争议点调研（串行单发）
- $handoff — 下轮翻页
- domain-modeling / neat-freak — CONTEXT.md/ADR 维护
