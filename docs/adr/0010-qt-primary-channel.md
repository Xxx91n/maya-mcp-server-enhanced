# 连接层：Qt 主工作通道 + native 仅 bootstrap/headless 回退

工作流量收敛到自研 Qt TCP 通道并整体重写：readyRead 事件驱动、逐连接命令队列、长度前缀分帧（帧上限 8–16 MiB）、typed error（MayaUnavailableError / MayaTimeoutError）、指数退避（0.5/1/2s）、localhost-only 强制、健康探针、_failed_ports 去重。commandPort 降级为 bootstrap/发现 + headless（mayapy 无 Qt 事件循环）最小通道并文档化不承诺大载荷。GUI 会话上 temp-file 注入随分帧协议移除；headless 回退保留 temp-file/分块 send。修 add_session 丢弃 bootstrap 返回值 bug。

Status: accepted (2026-09-16)

## Considered Options
- 双通道对等：否决——无成熟先例维护两条对等工作通道；一主一备是收敛形态（dcc-mcp-maya 自研桥+commandPort 兼容、blender-mcp 单 socket+队列）。
- 收敛 native 单通道：否决——commandPort 天花板由宿主决定（bufferSize 4096 超限断连、Maya 2024 echoOutput 损坏、单客户端），修不到 Qt 水平。

## Consequences
- commandPort 侧仍需探针失败去重与版本感知响应规范化。
- Qt 重写后实测吞吐无外部基准，需自测。
