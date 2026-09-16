# checkpoint/rollback 真快照语义（exportAll + 显式 adopt）

checkpoint 由“复制磁盘文件”（拿不到未保存修改）改为 cmds.file(exportAll) 真快照：导出时刻内存态、自包含、落 checkpoints/ 目录（basename 白名单 ^[A-Za-z0-9_-]+$）。rollback = 打开快照 + 改名回原路径（S2 语义），但前置不变式：任何覆盖路径名操作之前，被覆盖内容必须已有内存态快照（auto_before_rollback 改用 exportAll 而非 copy2）；返回结构化场景身份（scene_name_before / scene_name_after / original_file_status / scene_rebound_to）。文档写明两个诚实边界：(a) 快照不含 undo 历史，回滚后须以 scene_snapshot 重建认知；(b) references 默认展平，快照自包含但不管引用回写。

Status: accepted (2026-09-16)

## Considered Options
- 诚实降级为“磁盘备份”文案：否决——无人值守 agentic loop 下 VERIFY 会建立在假前提上（dirty 态 checkpoint 拿到旧态）。
- undo 栈：官方文档排除——file open/new 冲掉 undo 队列，stateWithoutFlush 标注 CAUTION，undo chunk 行为不可靠。
- rollback 命名语义 S1（sceneName 停在 cp 路径）/S3（独立 scene_adopt 工具）：选 S2——最贴合“回滚后继续编辑原场景”直觉；S3 留作后续增强。

## Consequences
- 必须落“带 reference edit 的 checkpoint→rollback 往返”mayapy 回归用例（exportAll 对 reference 编辑的展平行为无官方对照矩阵）。
- 消除 ACRFence 式状态分叉：Agent 上下文与磁盘真相经结构化返回值保持一致。
