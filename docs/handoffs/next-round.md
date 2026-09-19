# Handoff — maya-mcp-grill 下一轮任务书（rev19）

> 迁移注记（T-11a/D-041④）：本文件自 .scratch 迁入 docs/ 的规范副本；.scratch/ 已 gitignore（报告/audit/probe 等过程件仅存本地）。账本规范路径=docs/decision-ledger.md。

## 本轮验收事实（非计划）

- **T-12c+T-10b 已落地 impl/t10b-quality-gates**（12 commits 含审计返工，未 push/未开 PR）：README PyPI 实链+badge（wxx）→ pre-commit 薄集 8 钩+CI 兜底+dependabot+boy-scout pin（nyq）→ mass reformat 37 文件纯格式（uzu，SHA 12e31cad7b39859272d15359bb6baa76b0db423d 入 .git-blame-ignore-revs/vwm）→ ruff-check 债文件 exclude 11 文件（okz）→ ledger 尾空白 autofix（tyr）→ per-rule 预算迁移 src83/tests39+6 测试（lts）→ **mypy 基线闸（uqt，审计 B-1 返工后）**：mypy==2.1.0+stub 三件套精确钉（types-maya-strict 2025.0.6/types-psutil 7.2.2.20260906/types-PySide6 6.10.3.0，均≥7d）、baseline 223/3 于全量 .[dev] 环境重生成（原 212/7 生于无 stub 环境，与 CI 不自洽被打回）、CI 步 rc>1 崩溃守卫、warn_unused_* 棘爪 → coverage+ruff-report gitignore（rqu）→ dependabot pip ecosystem（klw）→ CONTRIBUTING pre-commit/CI 等价措辞修正（mku）
- **基线实测（rev19.1 口径，CI 等价环境复验）**：pytest 570 passed/4 skipped（4×mayapy 真机档）；ruff src 83/tests 39（post-format，per-rule）；mypy **223/3 文件**（全 stub 环境；漂移链 221→223→212→223，基线计数随 stub 环境+formatter 敏感）；coverage TOTAL **66%**（不设门）；pre-commit 8/8 绿；uv build 0.1.1 成功；MCP stdio 握手 v2.14.2+tools/list 20 工具
- **发布面不变**：PR #11/#12/#13 MERGED；v0.1.0/v0.1.1 双 tag+Release+PyPI latest=0.1.1
- 账本 45 条（D-001..D-045）；ADR 0001..0017；CONTEXT.md 30 术语（+棘爪）

## 真源与上下文（先读这些）

- 决策账本 docs/decision-ledger.md（D-001..D-045）
- ADR docs/adr/0001..0017（0017=T-10b spec 全链）
- CONTEXT.md 30 术语（冻结预算/棘爪/休眠代码为本轮直接相关）
- T-12c+T-10b 实施报告 .scratch/maya-mcp-grill/reports/2026-09-19-t12c-t10b-implementation.md
- 审计报告 .scratch/maya-mcp-grill/reports/2026-09-19-audit-t12c-t10b.md（FAIL→B-1 已返工，m-1..m-6 全带走）

## 工作约定（承袭）

- GitButler 专用（but commit/branch；禁 git write）；文件写走 Node.js fs（ctx_execute）+字节校验
- 每修复带回归测试（CONTRIBUTING 惯例）；诚实档与代码档分 commit
- atomcode 调研串行单发；ctx 沙箱 cm-fs-preload 缺陷→exec 直跑+ctx_index 手动索引
- 人工门：merge/tag/release/PyPI/分支保护/env reviewer=用户执行

## 任务链（按序）

### T-10b 收尾人工门（用户执行，agent 不代劳）

1. 审阅+推送 impl/t10b-quality-gates 并开 PR、合并（含 grill spec 栈底 commit osn 需同批处置：先合 grill/round12 或一并 review）
2. **若 rebase/force-push 过 impl 分支**：.git-blame-ignore-revs 内 SHA 已失效→重取 uzu 后新 SHA 刷新（文件注释+报告已声明）
3. 分支保护 main：required contexts=实测 check 名（lint「ruff budget gate」/mypy「mypy baseline gate」/test 四格/ci 聚合）——T-10b 合并后配置
4. environment pypi required reviewer 配置

### 下一轮主线（D-043 排序 / D-040 门）

5. **issue #7 真机验证推进**：v1.0.0 定义性前提（D-040）——mayapy Tier2+GUI Tier3 八项+PySide2+Inspector 多客户端+headless fallback 全绿方可 tag v1.0.0；agent 备 mayapy harness+逐项脚本，勾选须真机（需用户 Maya 环境）

### 候选顺延（不自动认领）

6. T-06 休眠归置（aesthetic_engine 38 mypy 错+dormant 覆盖披露随归置决策一并处理）
7. T-07 / Poly Haven（issue#2/D-003b）未排期

## DoD checkbox（下一轮 issue #7 前置）

- [ ] impl/t10b-quality-gates PR merged（人工门 1-4 全落）
- [ ] mayapy harness+逐项脚本落 tests/（pytest -m mayapy 可跑，不卡 CI）
- [ ] issue #7 checklist 真机逐项勾选（用户环境执行）

## 负向清单

- 不装 pre-commit.ci；不用 staged-only 渐进格式；mypy 不进 pre-commit 钩；coverage 不设绝对阈值门；macOS 不进全矩阵；mass reformat 零逻辑混入；mypy-baseline.txt 属本档产物已入库（rev18 限制已解除）
- 不顺手修登记债；不动 issue #7 checkbox（无 Maya 环境不可勾）；不把 dormant AE 测试/覆盖计入生产覆盖叙事；不把 PySide6 缺失 skip 记为失败
- ruff-check hook exclude 清单只出不进：新债文件不得入 exclude（烧账经 per-rule 预算门）

## 登记债（碰到再修，勿认领）

- 已消（审计返工）：mypy filter 对 crash 无感→CI 步改 rc>1 显式守卫；mypy~=2.1.0 宽钉→==2.1.0+stub 钉版。沿用债：mypy-baseline.txt 行号归零依赖上游契约，mypy 2.x 输出格式变更需重验；**残留环境漂移面**：runtime deps（fastmcp/psutil/platformdirs/PySide6）仍在 spec 区间浮动，上游发版可能改变 mypy 错误面使 CI 与基线瞬时不一致——完整 lock 政策仍缓（同 boy-scout 债类）
- 沿用 rev18：coverage patch 门触发=T-06 归置+真机档；macOS 单冒烟触发=pypistats 用户实证/真实 macOS bug/macOS 产物；pre-commit.ci 若未来豁免最小依赖姿态可后补；ruff format E501 ignore 评估（reformat 后 E501 仅存 6 处 src+0 tests，评估必要性已弱）
- 沿用 rev17：T-06 休眠归置/ctx 沙箱 preload 缺陷/57 条 AE dormant 覆盖披露/Maya 2022+ commandPort 未公开/D-011 validator/_suggest_layout 截断/checked-skipped 异构/orbit-shot 前缀/玄学评分/test_security:389 I001/AsyncMock/connection_guide 三连/ADR-0010 O-2/_probe_port 泄漏/native 丢 code/visual_module 真机项/_visual_injected 重连/双胞胎 helpers/Scene.gui 等/OSError 白名单/ruff 原生 baseline(#1149)/but pr forge/pending publisher/ci↔release 重复/unavailable 消息丢 {e}/budget argv/Qt Raises（uvx ruff 浮动与 ||true 两条已随 nyq 顺手修除，移出清单）

## suggested skills

- $but（GitButler）— 全部版本控制写操作
- $implement / tdd — issue #7 harness 实施驱动
- $atomcode-research — 争议点调研（串行单发）
- $handoff — 下轮翻页
- domain-modeling / neat-freak — CONTEXT.md/ADR 维护
