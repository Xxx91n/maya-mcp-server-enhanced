# T-05 Qt 连接层重写 — 实施报告

日期: 2026-09-17 ｜ 分支: `fix/t05-qt-channel` (commit `kyn`) ｜ 覆盖: D-013, D-014(c), D-019, ADR-0010

## 交付清单

### 1. Qt 通道重写 (D-013 主体)
- `maya_mcp_helper.py`: uint32-BE 长度前缀分帧(`encode_frame`/`FrameDecoder`/`FrameTooLargeError`),上限 `MAX_FRAME_SIZE = 16 MiB`(8–16 MiB 带内);`dispatch_request` + `handle_frame` 公开 seam;`ClientChannel` 每连接独立 FIFO 队列(传输无关,可无 Qt 测试);`QtCommandServer` 重写为 `readyRead` 事件驱动(去掉 50ms 轮询 QTimer);`QHostAddress.LocalHost` 绑定 + `peerAddress().isLoopback()` 双重回环强制;`health` 方法返回 status/port/clients/uptime。
- `client.py`: `MayaQtClient._send_receive` 改为分帧读写(`readexactly` + 响应 id 关联 + 响应上限校验);`framed_channel` ClassVar 能力位(Qt=True/native=False);`CONNECT_RETRY_DELAYS=(0.5,1.0,2.0)` 4 次尝试;`health()` 探针。

### 2. 类型化错误 (D-013 + D-019 兼容)
- `MayaUnavailableError(code="maya_unavailable")`;`MayaConnectionError = MayaUnavailableError` 别名向后兼容;`MayaTimeoutError(code="maya_timeout")` 为其子类。连接超时/读超时/连接中断分别归入 timeout/unavailable。

### 3. session_manager 修复
- `add_session()` 现在存储 `bootstrap()` 返回的专用通道 client(原 bug:存的是 config 端口的临时 client,会话落在错的 key 上);并维护 `_config_to_session` 映射 + finally 释放 config 连接。
- `_failed_ports: dict[key, monotonic_ts]` 去重,冷却 `failed_port_retry_after=60s`;端口消失即重置记录。
- 扫描 localhost-only:非回环地址跳过;`0.0.0.0`/`::` 归一为 `127.0.0.1`。

### 4. D-014(c) 顺带清单
- `StreamWriter` 5 MiB 上限接线(原为孤儿常量):超限时丢最旧 chunk、单块超限保留尾部。
- `MayaClient.write_module()` 修复死响应:native 通道的 `create_module` 错误藏在 result JSON 内层,现解析并抛 `MayaExecutionError(code: message)`。
- 删除 `client.py` / `session_manager.py` 的调试 `__main__` 块;删除 `bootstrap_new`(被 framed bootstrap 取代)。
- `server.add_session` 默认端口 7002→7001;端口校验 `1<port`→`0<port` 与 `validate_session_key` 对齐(登记债核销)。

### 5. 注入分流
- `scene_tools._ensure_module_injected`:>15K 模块按 `client.framed_channel` 分流——GUI/Qt 走分帧直连(移除 temp-file),native/headless 保留 temp-file 回退。

### 6. Headless 回退
- `bootstrap(client_type="qt")` 中 Qt 启动失败 → 警告并回退到专用 native commandPort(D-013: headless 下 native 是最小工作通道)。

## 验证证据(可复跑)

| 检查 | 命令 | 结果 |
|------|------|------|
| 单元测试 | `python -m pytest tests/ -q` | **513 passed, 3 skipped**(基线 457 → +56 回归) |
| Ruff src | `python -m ruff check src/ --output-format concise` | Found 174 errors(= 基线 174) |
| Ruff repo | `python -m ruff check . --output-format concise` | Found 237 errors(= 基线 237) —— 返修后实测；首轮曾自引入 test_client.py F401 导致 238，已核销 |
| mypy | `python -m mypy src/` | Found 221 errors in 3 files(= 基线 221) |
| 编译 | `python -m compileall -q src/` | clean |
| 打包 | `pip wheel . --no-deps -w dist/` | `maya_mcp_server-0.1.0-py3-none-any.whl` 构建成功 |
| 启动+测活 | `node .scratch/maya-mcp-grill/audit/stdio-smoke.mjs` | 进程启动;tools: 18;missingAnn/hintGaps: [];ping 正常;blocked call→isError `[blocked_pattern]`;bad result_type→isError `[invalid_input]` |
| 审计落盘 | 读 `%LOCALAPPDATA%\mcp-for-maya\mcp-for-maya\Logs\audit.jsonl` | smoke 触发的 rejected/error 事件已写 JSONL |
| Qt 实测 | `pytest tests/test_qt_channel.py::TestQtServerIntegration` | 1 passed(PySide6 6.11.1 真实 QTcpServer readyRead 回环) |

### 平台 test 闭环
- **Qt framed**: asyncio peer 线级回环 + 真实 QTcpServer(PySide6)回环 ✅
- **native/headless**: 注入分流测试 + bootstrap 失败降级回退测试 ✅
- **真实 Maya**: `mayapy -m pytest tests/ -m mayapy` 为手动本地层,本机无 Maya 运行时,未跑(层保持,非新增空洞)。

## 已知限制 / 风险
- `ClientChannel._drain` 在 Maya 主线程同步执行——长命令仍阻塞事件循环(与旧实现一致,属既定语义)。
- Qt 端响应 >16 MiB 坍缩为 `response_too_large` 错误帧;client 侧请求 >16 MiB 直接 `InputValidationError`。
- `_probe_port` 对新增 `MayaTimeoutError`(Unavailable 子类)按既有 `except MayaConnectionError` 覆盖。

## 未做
- 未推远端、未开 PR(按约定)。
- 未动 ruff/mypy 存量债(基线持平)。


---

## 返修记录（2026-09-17，响应 audit-t05 裁定：打回返工）

审计：reports/2026-09-17-audit-t05.md。必修 F-1/F-2/F-3 全部修复，观察项按如下处置。

### F-1 headless 回退死代码 + 僵尸会话 — 已修

- **A 层（契约修正）**：`bootstrap()` 的 `START_QT_SERVER` 改用 `raise_on_error=False`（client.py），`start_qt_server` 的错误按真线形状从 `result.error` / `result.result`(dict 或 JSON 串） 解析——回退分支真实可达。
- **B 层（双端防御）**：
  - 服务端：`start_qt_server` 在绑定前检测事件循环——`cmds.about(batch=True)` 或 `QCoreApplication.instance() is None` → 返回 `{"error":{"code":"qt_unavailable_headless","suggestion":...}}` 域错，不再产生 listen-成功但 readyRead 永不派发的僵尸端口。
  - 客户端：Qt client `connect()` 后过 liveness gate——`asyncio.wait_for(client.ping(), QT_PROBE_TIMEOUT=5s)`，不通则断连回退 native commandPort。即使服务端检测缺失（旧版本 helper），僵尸通道也不会登记为会话。
- **回归钉（真线形状）**：`test_qt_start_error_response_falls_back_to_native`（断言 `raise_on_error=False` 契约 + `{"error":{...}}`→native）、`test_qt_zombie_channel_falls_back_to_native`(connect 成功 + ping=False→native)、`TestHeadlessGuard::test_no_event_loop_returns_domain_error`(monkeypatch `QCoreApplication.instance()->None`→域错+未绑定）、`test_start_qt_server_with_event_loop`（真 QCoreApplication 下正常绑定，反向覆盖）。

### F-2 ruff ratchet — 已修

- 删除 `tests/test_client.py` 自引入的 `PortType` 未用 import。实测 `ruff .` = 237（回到基线），本表 §1 行已订正。

### F-3 域错误 code 不丢 — 已修

- 新增 `_domain_error_text(error)`：`{code,message}` → `"code: message"`，与 native `write_module` 对齐；Qt `_send_receive` 的 `raise_on_error` 分支与 `raise_for_error` 均改走该函数。
- 双 schema（已知域错 `{code,message,suggestion?}` vs 异常兜底 `{type,message,traceback}`）已在 `dispatch_request` docstring 注释明示。
- 回归钉：`TestQtSendReceiveDomainCode::test_unknown_method_raises_with_code`（真 asyncio peer，`unknown_method` code 出现在异常文本）。

### 观察项处置

- **O-1** health 接线：`SessionManager.check_session_health` 对 framed client 走 `health()`（status=="ok"），native 走 ping。
- **O-3** fail-closed：`peerAddress()` 异常 → 断开拒绝（原 except:pass 放行已改）。
- **O-4** loopback 单口径：`server.add_session` 改用 `is_loopback_host`（127.0.0.0/8、::1、localhost* 全收）。
- **O-6** 小修：`_CONFIG_PORT_TIMEOUT=60.0` 提常数（两处 60.0 magic）；`_send_receive` docstring 补 `MayaTimeoutError`；AGENTS.md tests/ 清单补 `test_qt_channel.py`。
- **O-2** ADR-0010 “版本感知响应规范化” 未实现 → 已登记债（handoff rev8 登记债区）。
- **O-5** `_probe_port` MayaConnectionError 分支 socket 泄漏：基线既有，未认领（登记债）。
- **O-7** commit id 为 GitButler change-id（kyn/kpt）；sha 见 `but log`/`git log`。
- **O-8** PySide2 fallback 移除→PySide6-only，与 D-012(Maya 2024+) 一致，事实确认。

### 复验（返修后实测）

- `pytest tests/ -q` → **517 passed, 3 skipped**（首轮 513 → +4 新钉）
- `ruff src/` = 174；`ruff .` = 237；`mypy src/` = 221 —— 全部基线持平
- `compileall` clean；wheel 构建成功；stdio-smoke 18 工具/四 hint/ping/blocked/invalid 全绿；audit.jsonl 落盘
- **诚实声明**：Qt 实测仅到 stub + PySide6 真 QTcpServer 回环层；本机无 Maya 运行时，真 Maya/mayapy 档未跑（既有手动层空缺）。
