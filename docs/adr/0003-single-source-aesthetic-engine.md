# 审美引擎单一真源：aesthetic_engine.py 注入 Maya

双实现已漂移（standalone 引擎 classify_light_type 返回 unclassified，而 compute_lighting_quality_score 用 other 键 → KeyError）。决定：aesthetic_engine.py（纯 Python）为唯一真源，经 write_module 注入 Maya；_mcp_scene 审美函数改为 采集场景数据 → 调用注入引擎 → 格式化输出，并对齐 analyze_aesthetics 与 scene_review 的采集字段契约。

Status: accepted (2026-09-16)

## Considered Options
- 删引擎留 Maya 端内联实现：否决——生产逻辑只能靠 stub 间接测。
- 双实现 + parity 测试：否决——债还在，只是加报警器。

## Consequences
- 引擎直接进 CI 测生产代码；双实现漂移问题根除。
