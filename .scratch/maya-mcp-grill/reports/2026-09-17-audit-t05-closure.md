# T-05 审计闭环报告 — 返修复审（通过）

Date: 2026-09-17
Auditor: 审计 Agent（独立窗口，不动手修）
Scope: fix/t05-qt-channel = kyn(772b398 feat) + kpt(8a48336 docs) + tyv(369e2a1 返修)；工作区干净
前序: reports/2026-09-17-audit-t05.md（裁定打回：F-1/F-2/F-3 必修 + 8 观察）；reports/2026-09-17-audit-t05-loop1.md（返修未落地时点记录，已被本轮 supersede）

## 裁定：通过

F-1/F-2/F-3 全部实物复核为真，回归测试按真线形状重写；O-1/O-3/O-4/O-6 核销，O-2/O-5 入登记债。复验全套绿。

## §1 复验矩阵（返修后亲跑）

| 验收项 | 返修声明 | 实测 | 结论 |
|---|---|---|---|
| pytest | 517 passed, 3 skipped | 517 passed, 3 skipped (22.09s) | 一致 ✓ |
| ruff src/ | 174 | Found 174 | 一致 ✓ |
| ruff . | 237（回基线） | Found 237；F401 已删 | 一致 ✓（ratchet 恢复只降不升） |
| mypy src/ | 221 | Found 221 in 3 files | 一致 ✓ |
| compileall | clean | clean | ✓ |
| wheel | 成功 | maya_mcp_server-0.1.0-py3-none-any.whl | ✓ |
| stdio-smoke | 全绿 | 18 工具/四 hint/ping {}/blocked→isError [blocked_pattern]/BOGUS→isError [invalid_input] | ✓ |
| audit.jsonl | 落盘 | 158→162 行，本次 smoke 的 rejected+error 已写 | ✓ |
| Qt/headless 钉 | 4 枚真线形状 | TestQtServerIntegration+TestHeadlessGuard+TestBootstrapFallback 6 passed | ✓ |

## §2 必修项复核（实物证据）

| 项 | 要求 | 实物证据 | 结论 |
|---|---|---|---|
| F-1 | headless 回退真实可达 + 无僵尸会话 | A 层：client.py:621-635 `raise_on_error=False` + payload dict/JSON 串双解析→qt_error；回退分支 :676-692 可达。B 层服务端：helper.py:571-586 `cmds.about(batch=True)` 或 `QCoreApplication.instance() is None`→`qt_unavailable_headless` 域错（{code,message,suggestion}）。B 层客户端：:653-672 connect 后 `wait_for(ping, QT_PROBE_TIMEOUT=5s)` 不通→断连回退，旧 helper 亦封死。测试 4 钉全真线形状：error-response 钉断言 `(START_QT_SERVER, False)` 契约；zombie 钉 connect 成功+ping False→native；no_event_loop 钉 monkeypatch QCoreApplication→域错且未绑定；with_event_loop 反钉真 QCoreApplication 绑定成功 | 修复 ✓ |
| F-2 | ruff repo ≤237 + 报告订正 | tests/test_client.py PortType import 已删（grep=0）；实测 repo=237；报告 §1 订正并在返修附录注明失实经过 | 修复 ✓ |
| F-3 | Qt 路径域 code 不丢 | `_domain_error_text()` client.py:82-96 统一 "code: message"；Qt _send_receive :906 与 raise_for_error :108-110 均保留 wire code；dispatch_request docstring 明示双 schema；test_unknown_method_raises_with_code 真 asyncio peer 钉 | 修复 ✓ |

## §3 观察项复核

| 项 | 处置 | 实物证据 | 结论 |
|---|---|---|---|
| O-1 health 接线 | 核销 | session_manager.py:402-411 framed→health() status=="ok"，native→ping | 核销 ✓ |
| O-3 fail-closed | 核销 | helper.py:528-531 peerAddress 异常→disconnectFromHost+return | 核销 ✓ |
| O-4 loopback 单口径 | 核销 | server.py:362-368 is_loopback_host + allow_remote_connections 门 | 核销 ✓ |
| O-6 小修 | 核销 | _CONFIG_PORT_TIMEOUT=60.0 常数（:24/199/368）；docstring 补 MayaTimeoutError；AGENTS.md:35 收 test_qt_channel.py | 核销 ✓ |
| O-2/O-5 | 登记债 | handoff rev8 登记债区 :66（版本感知规范化 + _probe_port socket 泄漏） | 入账 ✓ |
| O-7/O-8 | 事实确认 | change-id 惯例；PySide6-only 合 D-012 | 记录 |

## §4 残余观察（不挡本轮）

- R-1 native `_send_receive` 通用错误路径（client.py:493-495）仍只取 message 丢 code——Qt 路径已修后两通道不对称反转；建议后续统一走 `_domain_error_text`。降级为债级微瑕。
- R-2 F-1B 服务端检测依赖 `cmds.about(batch=True)`/`QCoreApplication.instance()`——stub 与真 Qt 均已钉，但 mayapy 真机档本机仍不可跑（既有手动层空缺）；建议 T-08 或首个有真机的窗口顺手实测一次 headless bootstrap→native 落会话。
- R-3 返修 commit tyv 一并提交了审计产物（audit-t05.md、audit-t05-loop1.md、diff-t05-review.patch）——.scratch 审计轨迹落账可接受，但审计 diff 产物混入功能修复提交属轻度噪声；后续窗口注意分开提交。
- R-4 回退分支内 START_COMMAND_PORT 仍走 raise_on_error=True：回退失败即真实失败，语义正确，记录事实。

## §5 过程核查

- 返修落同一分支 tyv(369e2a1)，commit message 属实；未推远端未开 PR ✓。
- 测试纪律恢复诚实：mock 形状与 _send_receive 真实行为逐点等价（raise_on_error=False 契约钉住）。
- 预算纪律恢复：repo 237 持平；报告与 handoff 均已如实订正，未宣称通过（"待复审"），由本报告转正。
- 无新增过程违规。

**T-05 验收通过。下一任务按任务序：T-08 视觉闭环（D-002/D-003a/D-020②/D-021）。**
