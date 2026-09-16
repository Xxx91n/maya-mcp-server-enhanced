# Handoff — maya-mcp-grill 第三轮任务书(T-03 方向)

> 生成: 2026-09-16 审计窗口(第二轮复核通过后)。供下一子 Agent 接手。

## 当前状态(已验收事实)

- T-01/T-02 已完成并通过两轮审计: fix 分支 commit 63dfeae(change-id kzr)。
  - stub 脚手架 tests/maya_stub/(语义正确的矩阵/8角点 bbox)+ 53 个新测试(284->337 收集)。
  - P0 修复全部落地: 错误透传(client.raise_for_error 单点消毒)、_scene_call JSON 传参灭注入面、_world_bbox 7 处统一、采样披露、scene_assert exists:false/bbox_min、zone total_objects、orbit locator+aim+warnings、check_constraints error 守卫。
- 验收基线(重跑用此口径): pytest 335+2skip;compileall OK;pip wheel OK;stdio init 2.14.7/18 tools/ping;ruff src<=185 全仓<=244;mypy<=227。
- 审计产物: .scratch/maya-mcp-grill/reports/{2026-09-16-report.md(rev2),2026-09-16-audit-t01-t02.md,-rev2.md},audit/diff-fd1b557.patch(v1 diff)。

## 真源(先读)

- 决策账本(唯一真源): .scratch/maya-mcp-grill/decision-ledger.md — D-001..D-013 current。
- 上轮任务书: .scratch/maya-mcp-grill/handoffs/next-round.md(T-01..T-12 全景)。
- 锐评原文: .codex_tmp/rui.txt;ADR: docs/adr/0001..0010;术语: CONTEXT.md。

## 下一个 grill/实现方向: T-03 — checkpoint/rollback 重做(D-007,ADR-0004)

 spec 要点(账本 D-007 原文为准):
 1. save_checkpoint 改 cmds.file(exportAll) 真快照 + basename 白名单 ^[A-Za-z0-9_-]+$ 落 checkpoints/。
 2. rollback = 打开cp+改名回原路径;前置 exportAll 的 auto_before_rollback;结构化返回 scene_name_before/after/original_file_status/scene_rebound_to。
 3. 不变式: 任何覆盖路径名操作前,被覆盖内容必有内存态快照。
 4. 文档写明两诚实边界: 快照不含 undo 历史(回滚后须 scene_snapshot 重建认知);references 默认展平不管回写。
 5. mayapy 档须落“带 reference edit 的 checkpoint->rollback 往返”回归用例。
 对应 rui.txt P0-3: 现状是 copy2 磁盘旧文件、.. 未校验、rename 静默覆盖原始场景。

## 工作约定(承袭,勿违)

- 写文件经 ctx_execute(node fs);版本控制只用 but;新/变决策先记 D-xxx。
- 测试纪律: 每修复带回归测试(须能在 base src 复现 RED: PYTHONPATH 指 base 树重跑——注意 editable install 陷阱,勿直接跑 tests/)。
- ruff/mypy 预算只降不升;文档不得超前于代码;commit message 字字为真。
- 登记债(勿认领为本轮任务,碰到再修): _suggest_layout pair-window 披露、checked/skipped 异构、AGENTS.md tests/ 表、orbit_cam/shot_cam 命名前缀、dist_audit/ 未 gitignore。

## suggested skills

- 执行: implement, tdd, diagnosing-bugs
- 评审: code-review(双子轴;交付前自审 commit message 与实物一致性)
- 版本: gitbutler(but);交接: handoff
