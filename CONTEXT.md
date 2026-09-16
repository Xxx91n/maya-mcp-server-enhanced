# Maya MCP Server — Domain Context

让 LLM Agent（Codex/Claude 类）通过 MCP 工具直接操控 Autodesk Maya 的项目；核心抽象是给 Agent 空间感知 + 工程级验证回路，而非通用遥控器。

## Language

### 工作流

**ICEV**:
Inspect → Compute → Execute → Verify 四步强制工作流：任何场景修改必须先快照感知、再计算、执行、然后验证。
_Avoid_: 盲改

**视觉闭环 (Visual Loop)**:
把视口/渲染图像回传给多模态 Agent 的验证手段；两个工具：scene_viewport_snapshot（高频便宜）与 scene_render_preview（低分辨按需）。headless 会话无视口，工具须返回显式能力错误。
_Avoid_: 截图工具（过泛）

### 场景认知

**场景快照 (scene_snapshot)**:
一次批量查询返回的全场景空间状态（名字/类型/位置/BBox/父子），是 Agent 场景心智模型的来源。
_Avoid_: 场景信息 dump

**CoS (Chain-of-Symbol)**:
场景数据的紧凑记号化输出格式，用于压缩 token。

**Zone**:
按命名规则映射的功能分区，内置九组：GRP_shell / GRP_entrance / GRP_display / GRP_ip_core / GRP_furniture / GRP_lighting / GRP_path / GRP_decor / GRP_service。
_Avoid_: 区域、层

**命名约定**:
生产命名前缀——GRP_ 组、GEO_ 几何、MAT_ 材质、CAM_ 相机、LGT_ 灯（带角色 key/fill/rim/accent）、LOC_ 定位器；禁用 Maya 默认名（pCube1、group1 等）。

### 验证与事务

**审核 (scene_review)**:
确定性场景审计；每个检查是自注册 validator（携带 name/severity/family/order 元数据），单条异常记 check_error 不中断整轮。
_Avoid_: 评分脚本

**自定义 validator**:
经注册 API（register(name, fn, severity, family)）注入的自定义检查；口径=受信 agent 的扩展机制，非插件生态。
_Avoid_: 插件、沙箱

**checkpoint（真快照）**:
对导出时刻内存态的自包含序列化快照（exportAll，references 默认展平），落 checkpoints/ 目录；不含 undo 历史。
_Avoid_: 文件备份、存档

**rollback**:
打开快照文件并显式重建场景身份；不变式——任何覆盖路径名操作之前，被覆盖内容必须已有内存态快照；返回值显式携带场景身份信息。
_Avoid_: 恢复

**ad-hoc 快照**:
untitled（未保存）场景经显式 name 参数产出的标记性快照；不参与 S2 回滚语义——rollback 打开后停留快照路径（S1），返回 scene_rebound_to=null、original_file_status="no_original_file"。untitled 场景不带 name 的 checkpoint 调用默认报错。 快照落 <Maya workspace>/checkpoints/。
_Avoid_: 无名场景快照

### 连接与注入

**引导通道 (bootstrap channel)**:
commandPort（默认 :7001），仅用于发现会话与注入 helper，不承载工作流量。
_Avoid_: 主通道

**工作通道 (working channel)**:
bootstrap 后创建的专用通道；默认=自研 Qt TCP server（多客户端、长度前缀分帧）；headless（mayapy 无 Qt 事件循环）回退到 native commandPort。

**temp-file 注入**:
大模块落盘临时文件再由 Maya 读取的注入方式；GUI 会话上随分帧协议移除，headless 回退保留。

**薄集成 (thin integration)**:
资产生态接入策略——只接低成本外部源（首片 Poly Haven，免费 CC0 API），挂到 scene_plan 做 zone 语义 + bbox 尺寸推荐；不做自建资产库/爬虫。
_Avoid_: 资产市场

### 安全姿态

**受信方**:
威胁模型中信任的对象 = MCP client/agent；防线不承诺遏制恶意 client。
_Avoid_: 沙箱内执行

**安全网 (safety net)**:
pattern 扫描/限流/校验等防误操作机制；与安全边界严格区分——文档禁用 sandbox/secure 字样描述它们。
_Avoid_: 沙箱、安全边界

### 工程词汇

**绞杀者 (strangler)**:
大模块改造方式——先建 stub 测试脚手架，修复带回归测试落地，拆分随修复触及区域增量进行。
_Avoid_: 大爆炸重构

**stub 层**:
CI 上替代 maya.cmds/OpenMaya 的自建假实现；数学语义必须正确（尤其 8 角点世界 bbox），否则假绿。

**mayapy 档**:
可选的真机 Maya 测试层，本地手动跑，文档化，不卡 CI。
