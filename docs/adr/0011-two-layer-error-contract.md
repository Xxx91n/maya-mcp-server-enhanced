# 工具错误返回：双层契约（宿主失败走 isError；Maya 域结果走结构化 error 对象）

18 个工具的错误返回分两层：宿主侧失败（参数校验/限流/连接/管线拒绝）抛类型化异常 → MCP `isError` 通道、错误文本内嵌 `code` 前缀；Maya 侧域结果统一返回 `{error: {code, message, suggestion?}}` 对象（存量 `_rb_error`、裸 `{"error": str(e)}` 等 dict 全部迁移到此形）；业务成功不包信封。

Status: accepted (2026-09-17)

## Considered Options

- 全量信封 `{ok, data?, error?}`：否决——所有既有返回形状 breaking，且把“调用失败”与“调用成功但域内未过”压进同一层语义。
- 现状异构文档化：否决——裸 dict / 类型化异常 / `_rb_error` 三形态并存会持续衍生第四种。

## Consequences

- `suggestion` 字段沿用 D-015 语义：给建议、不自动采用。
- 区分“调用失败”（宿主层）与“调用成功但域内未过”（assert 未通过、review 违规、rollback 边缘态）是 agent 可执行性关键。
- 此后每任务新增错误形态须按此 schema；rate_limited / rejected 等管线错误属宿主侧，走 isError + code 前缀。
- MCP spec 只规定 isError 通道，本契约为本地一致性决策，无外部标准对应。
