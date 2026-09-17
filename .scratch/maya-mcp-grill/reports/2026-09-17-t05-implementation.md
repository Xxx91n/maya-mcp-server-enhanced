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
| Ruff repo | `python -m ruff check . --output-format concise` | Found 237 errors(= 基线 237) |
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
