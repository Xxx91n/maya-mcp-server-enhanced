# Handoff — T-03 审计通过，下轮 T-04（安全统一管线+威胁模型）

## 本轮结果
- T-03 审计**通过（带观察项）**：硬验收重跑全绿（369+3skip / ruff 185+244 / mypy 223 / compileall+wheel+stdio 2.14.7-18tools-ping）；D-007/D-015/D-016 全落地；无过程违规。
- 审计报告：D:/Aworker/maya/maya-mcp-server/.scratch/maya-mcp-grill/reports/2026-09-17-audit-t03.md（含声明→证据→结论全表 + 9 条观察项 O1-O9）

## 真源（下轮先读）
- 常驻任务书 rev4（下一任务 T-04 spec 在内）：.scratch/maya-mcp-grill/handoffs/next-round.md
- 决策账本（D-001..D-016 全 current）：.scratch/maya-mcp-grill/decision-ledger.md
- T-04 spec：ADR-0005 + 账本 D-008/D-014b；范围=18 工具统一校验/限流/审计/pattern 收口 + SECURITY.md/威胁模型 8 项 + connection_guide 越权收口（合并式写入/虚假文案/硬编码路径/_get_platform 去重）

## 顺带项（T-04 内处理，审计观察项）
- O4：补 1 个测试钉住 untitled+auto_before_rollback 时 auto 快照落 workspace/checkpoints
- O5：隐藏案例 3 测试加钉“快照已丢失”字面量（missing vs corrupt 区分）
- rev4 登记债两条陈旧项（dist_audit gitignore / AGENTS.md tests 表）下次改文档时顺手删行

## 注意
- 写文件经 ctx_execute(node fs)；版本控制只用 but；新实现轮用独立分支
- 基线口径（勿劣化）：pytest 369+3skip / ruff src=185 全仓=244 / mypy=223
- mayapy 档本机无 Maya 不实跑，写了标 manual tier 即可

## suggested skills
- $implement（T-04 实现）· $tdd（回归先 RED）· $code-review（交付前自审）· $security-review-orchestrator（T-04 为安全任务，取证可用）· $handoff（再交接）
- 版本控制：$but；调研：$atomcode-research（串行+配额）
