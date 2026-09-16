# AUDIT CLOSURE — T-03 观察项修复闭环

> 2026-09-17 · 修复窗口（应用户指示由修复方执行）· 基线 commit yty（fix/t03-checkpoint-rollback）
> 前置报告：reports/2026-09-17-audit-t03.md（判定=通过带观察项）

## 判定：观察项全清，终审无遗留

| 观察项 | 修复 | 证据 |
|--------|------|------|
| O1 报告版本笔误 2.14.2 | report-t03.md 订正为 2.14.7 | grep 实测一致 |
| O2 “+34 新用例”口径含糊 | 订正为“+34 通过项、+1 skip；31+3=34 collected” | 报告表内文 |
| O3 诚实边界/单会话假设未上用户面 | README.md/README_en.md 回滚段补边界行；server.py instructions 增 self-contained+single-session 行；两 README 特性表补 scene_checkpoint_list | README.md:172-173、README_en.md:110、server.py:90-91 |
| O4 D-016d 无测试钉/无 docstring | 新增 test_rollback_untitled_auto_snapshot_lands_workspace（断言 auto 快照落 ws/checkpoints、cp_auto_before_rollback_ 前缀）；rollback_to_checkpoint docstring 补 untitled 段落 | tests/test_checkpoint_rollback.py |
| O5 隐藏案例3未钉字面量 | missing→断言“快照已丢失”+missing；corrupt→断言“快照已丢失”+header/corrupt | 同文件两测试已加固 |
| O6 spec 字面 absoluteName 漂移 | ADR-0004 Consequences 订正：实现=expandName 优先+sceneName 兜底，absoluteName 指消歧语义 | ADR-0004 L19 |
| O7 prev_ 同秒撞名静默丢件 | prev_{ts}_{file} 撞名追加 _{i} 后缀循环（与 _auto_snapshot 同款），白名单兼容 | maya_scene_module.py save_checkpoint |
| O8 rev4 登记债陈旧×2 | 删 “dist_audit/ 未 gitignore”；AGENTS.md 债项只留 orbit_cam/shot_cam 半条 | next-round.md 登记债 |
| O9 AGENTS.md “15 tools”陈旧+README 表缺行 | 订正为 13（grep @mcp.tool 实测）；README×2 表补 scene_checkpoint_list | AGENTS.md:16、README×2 行20 |

## 验收重跑（修复后同一套口径）

- pytest tests/ -q → **370 passed + 3 skipped**（+1：O4 新测试）
- ruff：src=185 / 全仓=244（修过一处新增 E501 后回落预算内）
- mypy：223（不动）· compileall OK · stdio init 2.14.7 / tools=18 / ping {}
- 过程说明：修复中一次 ruff 186/245 超预算（server.py 新 instruction 行超长），已拆行修复回落——非最终态违规。

## 残留说明

- 无新增债务；rev4 登记债中 orbit_cam/shot_cam CAM_ 前缀仍为存量（未动）。
- mayapy 档依旧本机未实跑（无 Maya），manual tier 不变。
