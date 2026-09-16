# 公开发布定位与首发范围

本仓库按公开发布推进（GitHub + PyPI，对标 blender-mcp 发布纪律）。首发范围 = 修复对齐现有承诺 + 视觉闭环（两工具：scene_viewport_snapshot 高频便宜 / scene_render_preview 低分辨按需）。资产生态链仅长期方向，按薄集成切片：第一片仅 Poly Haven 并接入 scene_plan 做 zone 语义 + bbox 尺寸推荐，Sketchfab/AI 生成模型暂缓，不做自建资产库/爬虫。README 叙事定位 = 验证回路+审计+回滚 vs 裸 exec 的对比，并尽早占住 PyPI 包名。

Status: accepted (2026-09-16)

## Considered Options
- 仅自用：否决——安全/许可/文档要求会降级。
- 团队内部平台：否决——与公开叙事与发布卫生要求不符。

## Consequences
- LICENSE、PyPI 命名冲突、README 数字一致性、威胁模型声明均为发布阻断项。
- security.py 卖点叙事必须在注入面修复（JSON 传参）之后才可写。
