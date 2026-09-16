# 支持范围：Maya 2024+（Python 3.10+）

官方支持 Maya 2024/2025/2026（Maya 内置 Python ≥3.10），与宿主 requires-python>=3.10 对齐；2023 及以下不阻止不担保，README 如实声明。

Status: accepted (2026-09-16)

## Considered Options
- 宽支持到 2022（py3.7）：否决——注入代码须降级到 py3.7 兼容，砍表达能力换覆盖面，收益不对等。
- 不声明范围：否决——发布后会被版本 issue 打脸。

## Consequences
- 注入侧代码（_mcp_scene、aesthetic_engine）可用 py3.10 语法；stub 层只需模拟一套 API 面。
