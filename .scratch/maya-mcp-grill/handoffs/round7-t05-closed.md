# Handoff — T-05 闭环快照（审计通过）

> 2026-09-17。T-05 Qt 连接层重写验收通过；活任务书以 next-round.md(rev9) 为准。

## 结论

- 分支 fix/t05-qt-channel = kyn(772b398 feat) + kpt(8a48336 docs) + tyv(369e2a1 审计返修)。
- 审计链：reports/2026-09-17-audit-t05.md（打回 F-1/F-2/F-3）→ reports/2026-09-17-audit-t05-loop1.md（返修未落地时点记录）→ reports/2026-09-17-audit-t05-closure.md（**通过**）。
- 新基线：pytest 517+3skip；ruff src=174 / repo=237；mypy=221；compileall+wheel+stdio+audit JSONL 全绿。

## T-05 交付（验收后口径）

- Qt 主通道：readyRead 事件驱动 + 逐连接 FIFO + uint32-BE 分帧(16MiB) + typed error + 0.5/1/2s 退避 + localhost-only(绑定+peer 拒绝+扫描三处) + health 探针(已接 check_session_health)。
- headless 双端防御：helper 事件循环检测(qt_unavailable_headless 域错) + client liveness gate(ping<=5s 不通回退 native)。
- D-014c 顺带清单全核销；D-019 域 code 在 Qt 路径经 _domain_error_text 保留。
- 观察项：O-1/O-3/O-4/O-6 核销；O-2(版本感知响应规范化)/O-5(_probe_port socket 泄漏)在登记债；R-1 native _send_receive 通用路径仍丢 code(微瑕,债级)。

## 教训沉淀(给后续窗口)

- mock 形状必须与真线等价：返修前 fallback 测试用 error 字段 mock，而真线在 raise_on_error=True 下 raise——测试纪律要求钉契约(pin 参数)而非钉形状想象。
- 预算数字须实测后写报告：ruff repo 首轮失实(237 写错,实为 238)。
- 审计产物(报告/diff patch)建议与功能修复分提交(本轮被 tyv 捎带，R-3)。

## suggested skills

- 执行 T-08：implement, tdd, research/atomcode-research(Maya viewport 捕获路径)
- 评审：code-review(双轴,同先例)
- 版本控制：gitbutler(but)
