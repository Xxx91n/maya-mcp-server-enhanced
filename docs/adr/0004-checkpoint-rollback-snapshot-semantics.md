# checkpoint/rollback 真快照语义（exportAll + 显式 adopt）

checkpoint 由“复制磁盘文件”（拿不到未保存修改）改为 cmds.file(exportAll) 真快照：导出时刻内存态、自包含、落 checkpoints/ 目录。rollback = 打开快照 + 改名回原路径（S2 语义），但前置不变式：任何覆盖路径名操作之前，被覆盖内容必须已有内存态快照（auto_before_rollback 改用 exportAll 而非 copy2）；返回结构化场景身份（scene_name_before / scene_name_after / original_file_status / scene_rebound_to）。文档写明两个诚实边界：(a) 快照不含 undo 历史，回滚后须以 scene_snapshot 重建认知；(b) references 默认展平，快照自包含但不管引用回写。

Status: accepted (2026-09-16)；refined by D-015 (2026-09-16)、D-016 (2026-09-16)

## Considered Options
- 诚实降级为“磁盘备份”文案：否决——无人值守 agentic loop 下 VERIFY 会建立在假前提上（dirty 态 checkpoint 拿到旧态）。
- undo 栈：官方文档排除——file open/new 冲掉 undo 队列，stateWithoutFlush 标注 CAUTION，undo chunk 行为不可靠。
- rollback 命名语义 S1（sceneName 停在 cp 路径）/S3（独立 scene_adopt 工具）：选 S2——最贴合“回滚后继续编辑原场景”直觉；S3 留作后续增强。
- （D-015）untitled 场景直接放行 exportAll 快照：否决——S2 rebind 无原路径可回绑，同一 rollback 调用对不同来源快照行为分叉，重演本 ADR 要消除的状态分叉。取“默认报错 + 显式 name 逃生 → ad-hoc 快照”（文件名标记、rollback 走 S1、返回 scene_rebound_to=null 与 original_file_status="no_original_file"）。
- （D-015）name 静默 sanitize munging：否决——"a/b" 与 "a\\b" 会撞名成 "a_b"，agent 上下文与磁盘分叉；CWE-20 fail-fast 惯例。取严格白名单 ^[A-Za-z0-9_-]+$ 拒绝，error 附 suggestion 字段（清洗建议不自动采用，agent 显式二次调用才算数）。
- （D-015）auto_before_rollback 失败时 warning-continue：否决——违反“覆盖前必有快照”不变式，且是受信 agent + prompt-injection 威胁模型下注入者最想触发的路径。取中止 rollback（结构化 error）+ 显式逃生参数 discard_current_state（默认 false），走逃生返回 safety_snapshot="skipped_by_user"；auto 成功时传逃生参数 → 返回 warning。

## Consequences
- 必须落“带 reference edit 的 checkpoint→rollback 往返”mayapy 回归用例（exportAll 对 reference 编辑的展平行为无官方对照矩阵）。
- 消除 ACRFence 式状态分叉：Agent 上下文与磁盘真相经结构化返回值保持一致。
- （D-015）T-03 必测边缘案例：checkpoints 路径已是文件/不可写 → 预检 + 错误透传；同名 checkpoint → 默认拒绝，overwrite:true 才覆盖且覆盖前旧文件 rename 保留；checkpoint 与 rollback 之间快照被外部删改 → exists 预检 + //Maya ASCII 头校验，报“快照已丢失”而非底层 open 错；rollback open 失败半残态 → 返回值定义 scene_name_after + 建议 agent 立即 scene_snapshot 重建认知。
- （D-015）实现约束：sceneName 结果取绝对路径消歧（resolved/unresolved 双语义；实现=cmds.file(q, expandName=True) 优先 + sceneName 兜底，"absoluteName" 指消歧语义而非字面 flag）；untitled 场景与 auto_before_rollback 的组合语义须显式定义（不得留给 Maya 默认）；所有 file 操作 prompt=False（GUI 模态弹窗会挂死 MCP 往返）；文档标注“单场景文件单会话”假设（多 session 对同文件 rollback 会互踩 rebind）。
- （D-015）不做：retention 上限（YAGNI，list_checkpoints 返回 count 供自查）；独立“放弃当前状态”工具（同一破坏性操作不暴露两个入口）。
- （D-016）文件名方案：cp_{name}.ma（常规）/ cp_adhoc_{name}.ma（untitled→<workspace>/checkpoints/）/ cp_auto_before_rollback_{ts}.ma（rollback 前安全快照）/ prev_{ts}_{filename}.ma（overwrite 保留件，经 preserved_as 披露、可 rollback）。rollback filename 白名单 ^(cp|prev)_[A-Za-z0-9_-]+\.ma$。
