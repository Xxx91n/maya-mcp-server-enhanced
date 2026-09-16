# scene_review 验证器注册表（收窄版）

拆分时每个检查改为自注册 validator（name/severity/family/order 元数据）；注册 API 限 register(name, fn, severity, family) 且与会话/缓存/回滚内部状态隔离；单条 validator 异常记 check_error 计入报告不中断整轮；自定义注入走 write_module + 注册 API，文档口径=受信 agent 的扩展机制（逃生舱），非发布卖点；entry-point 自动发现后置。

Status: accepted (2026-09-16)

## Considered Options
- 固定 11 维只整理边界：否决——工作室规范差异是刚需（USD Validation 的 Explicit Validators、ShotGrid hook 注入、Pyblish 会话内注册先例）。
- 全量 Pyblish 式插件系统：否决——发现/生命周期是框架中最贵最难维护的部分（Pyblish 被社区判定勿改；无主流工具要求插件包分发 validator）。

## Consequences
- README 不得暗示沙箱或插件生态；自定义 validator 通道不引入新威胁但引入隔离义务（schema 隔离 + 错误隔离）。
