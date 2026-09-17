# Handoff — maya-mcp-grill 下一轮任务书（rev10）

> 生成时间：2026-09-17（grill round7 定稿：T-08 spec 闭合）。供任意子 Agent 接手；结论以决策账本为唯一真源。

## 本轮验收事实（非计划）

- **T-05 通过**（前轮）：Qt 连接层重写验收完成。分支 fix/t05-qt-channel(kyn+kpt+tyv)。审计链 audit-t05→tyv 返修→audit-t05-closure(通过)。
- **基线（勿劣化）**：pytest **517+3skip**；ruff src=174/repo=237；mypy=221；compileall+wheel+stdio(18工具四hint ping audit JSONL)全绿。
- **锐评复核（round7 实物复验）**：rui.txt 无孤儿——P1-3 八子项 T-05 全核销（readyRead 真接/add_session 保留 bootstrap/端口 7001/5MB 接线/__main__ 清除）；P1-2 三连仍真；开账仅剩 T-06(P1-1)+T-09/T-10(P2)+登记债。
- **round7 决策**：D-023（捕获机制）→D-024（落位注入）→D-025（API 契约）→D-026（副作用纪律）→D-027（测试+文档矩阵）。落地 **ADR-0013**；CONTEXT.md 新增「净零副作用」「文档传播矩阵」两术语+stub 层/mayapy 档精化。

## 真源与上下文（先读这些）

- 决策账本：.scratch/maya-mcp-grill/decision-ledger.md（D-001..D-027；D-020 revised→D-021，余皆 current）
- 术语表 CONTEXT.md；ADR docs/adr/0001..0013（0013=视觉闭环架构，T-08 全部 spec 的真源）
- 规则文件 AGENTS.md（联动表含 pipeline/connection_guide 行）
- 审计 smoke 脚本：.scratch/maya-mcp-grill/audit/{stdio-smoke,stdio-ratelimit,probe,probe-repair}.mjs
- T-08 调研证据：atomcode 5 轮 ~60 源（Autodesk 官方文档×5、maya-capture capture.py+tests.py 全文、blender-mcp addon.py+PR#266+#189、Playwright MCP、dcc-mcp-maya capabilities.py、Google Testing Blog、Diataxis、tech-artists headless 帖）

## 工作约定（承袭）

- 写文件一律经 ctx_execute（node.js fs / python fs）；版本控制一律 but（禁 git 写命令）；每轮独立分支。
- 账本纪律：新决策先入 D-xxx；测试纪律：每修复带回归（base 可复现 RED）；预算只降不升（ruff 174/237、mypy 221）。
- 文档纪律：README/AGENTS/threat-model 不超前于代码、同 commit 同步、字字为真；**文档传播矩阵**——本 commit 只修"本次变更使其失真"的行，其余错数落 PR 描述清单交 T-09。
- 错误契约 D-019（双层）；审计不变式：每个 tools/call 必落 audit.jsonl 一行；管线 try 外不得有可能抛出的代码。

## 任务序（D-021 定案）

```
~~T-05 Qt 连接层重写~~ ✅
T-08 视觉闭环           ← 下一任务，spec 已闭合
T-09 发布卫生           ← T-11 版本声明文档级并入
T-10a 最小质量门        ← GH Actions 跑 pytest+ruff
─── 发布 v1.0 ───
T-10b 完整质量门        ← pre-commit+mypy ratchet，T-06/T-07 动工前置
T-12 Poly Haven         ← v1.1 首弹
T-06 审美引擎单源化     ← 内部债，在 T-10b 护栏下做
T-07 注册表+绞杀拆分    ← 内部债
```

## 下一任务：T-08 视觉闭环（D-002/D-003a/D-020②/D-021/D-023..D-027/ADR-0013）

### 交付物

1. **`src/maya_mcp_server/visual_module.py`**（注入名 `_mcp_visual`）：GUI-only 捕获代码；lazy 注入于首次视觉工具调用（复用 _mcp_scene 幂等注入模式，按 session 追踪）；headless 会话永不注入；模块内防御 omui/PySide import 失败→同款结构化错误。
2. **`src/maya_mcp_server/visual_tools.py`** + `register_visual_tools(mcp)`：server.py 与 register_scene_tools 并排调用；工具 docstring 声明 GUI-only + 六条副作用披露（见下）。
3. **`pipeline.TOOL_ANNOTATIONS`** +2 行：scene_viewport_snapshot/scene_render_preview=read 类（readOnly:true——以净零副作用为成立前提）。
4. **stub 扩展**：cmds.py 补 GUI 面（getPanel/modelEditor/lookThru/lsUI/objectTypeUI/playblast+假 panel 注册表，edit 真改状态 query 读回同值）；新 tests/maya_stub/openmayaui.py（M3dView/MImage 假实现，writeToFile 写确定性字节）。
5. **测试**：契约层终态钉（成功+异常路径 registry 终态==入前快照）+单条宽松 restore 断言；mock 仅难触发分支；禁像素断言/精确调用序列 pin。
6. **文档**（传播矩阵）：README/README_en 工具数→20+清单（顺带把 15 陈旧错数修真）；server.py instructions（ICEV VERIFY 加 visual confirmation）；AGENTS.md 结构+联动表补 visual_module/visual_tools 行；threat-model §5 矩阵+2 工具行逐行对齐。**其余错数落 PR 描述清单交 T-09**。

### scene_viewport_snapshot（D-023/D-025）

- 机制：`M3dView.active3dView().readColorBuffer()`；VP2 走 `img.create(w,h,4,MImage.kFloat)→readColorBuffer→convertPixelFormat(kByte)`（官方补丁，否则全黑）；`cmds.refresh(force=True)` 先刷；WYSIWYG 含 HUD/选区=特性。
- 编码：`MImage.writeToFile(tempdir png)→QImage.scaled 降采样→JPEG→base64→删文件`；无 PIL 依赖。
- 参数：session, max_size=800(最长边), format jpeg|png 默认 jpeg, quality=80(仅 jpeg)。
- docstring 写 "png recommended for wireframe/line-art review"（jpeg 默认是有意偏离，描述兜底）。

### scene_render_preview（D-023/D-025/D-026）

- 机制：`cmds.playblast(frame=currentTime, format="image", compression="png", offScreen=True, viewer=False, showOrnaments=False, widthHeight=[w,h], percent=100, forceOverwrite=True, editorPanelName=显式钉面板)`→临时文件→base64→清理。
- 参数：session, camera=None(默认当前 lookThru), width=640, height=360, max_size/format/quality 同上；**width/height 服务端向上取整 ÷4**（playblast Windows 硬约束）+docstring 声明"实际尺寸以返回元数据为准"（clamp）。
- **副作用纪律**（D-026 全部落实）：`_active_model_panel()` 两级探测（withFocus→modelEditor 校验→activeView 兜底）；`_look_thru_restored` context manager（modelEditor -q -camera 读原→lookThru→try/finally 恢复；finally 内 modelEditor(panel,q=True,exists=True) 防御；restore 失败吞掉记日志不掩盖业务错误）；`currentTime` save/restore 防 undo bug #21；`objExists(camera)` 预检；docstring 六条披露（瞬时跳变不可 undo/净零副作用/时间跳变/不弹 viewer/失败语义/强杀除外）。

### 返回契约（D-025）

- `[ImageContent(annotations.audience=["assistant","user"]), TextContent(JSON 元数据)]`；snapshot 元数据={session,camera(回传 lookThru),width,height,format,bytes,panel}；preview 额外 source:"playblast"。
- FastMCP 混合返回类型未逐字确认→兜底 python-sdk 手构 CallToolResult。

### headless 双闸（D-024/D-025）

- 宿主侧：`client.framed_channel==False`→短路（D-019 第一层 isError+code 前缀，零往返）。
- Maya 侧：`about(batch=True) OR 无 modelPanel`→`{error:{code:gui_session_required,message,suggestion}}`（第二层）。
- **硬性**：服务端校验产物非空（headless playblast 实证静默产空文件），不透传成功。

### DoD

- [ ] 上述 6 交付物全落+注册 20 工具可列
- [ ] 契约测试全绿（注入轨迹/双闸两层/annotations/非空校验/base64+magic/元数据字段/÷4/降采样数学/temp 清理/终态往返）
- [ ] 基线不劣化（pytest/ruff/mypy 预算只降不升）
- [ ] 文档传播矩阵执行+PR 描述列遗留 stale 项
- [ ] mayapy 手动层 checklist：垂直翻转方向/kFloat@2025+/真实视口内容/playblast 实物/lookThru 还原
- [ ] MCP Inspector+Claude Code+Codex 双客户端多 block 渲染实测

### 不做（负向清单）

panel 选择/ornaments/帧范围参数；headless 渲染器回退（v1.x 候选，须 opt-in+method 标注）；独立面板（v1.x 换 maya-capture 库）；fake 层像素断言；精确调用序列 pin；.rnd 分支；inViewMessage 抑制。

## 其后任务速览

- **T-09**（D-001c/D-003c/D-010/D-020④⑤/D-022）：LICENSE(MIT+上游 notice)、pyproject 身份/URLs、仓库改名 mcp-for-maya、README 逐项核实（T-08 已修 tool count→20，余 9/11维/65%/pip 指向/Skills 幻影按 D-022 话术/LOGLEVEL/scripts/）、能力矩阵对比叙事、telemetry 信任卖点、roadmap issue、T-11 版本声明并入
- **T-10a**（D-009/D-021）：GH Actions pytest+ruff；**T-10b**：pre-commit+mypy ratchet+覆盖率
- **T-12**（D-003b/D-021）：Poly Haven 薄集成挂 scene_plan，v1.1
- **T-06**（D-006/D-014a）：审美单源化+伪引用清算
- **T-07**（D-004/D-011/D-014c）：验证器注册表+绞杀拆分

## 竞品与对标情报（ADR-0012）

- mcp-for-blender（28.8k★）：截图=offscreen 临时 PNG→base64 ImageContent(max_size=800)，裸 Image 丢元数据（我们的混合块更优）；issue#189 文件路径耦合跨 OS 断裂教训（我们 TCP+base64 天然规避）；PR#266=method 标注先例
- dcc-mcp-maya（55★/535commits）：capabilities.py 实证"声明能力+运行时 skill_error"模式（与我们 capability error 同构）；29 skill 包+progressive skills
- Playwright MCP：image+text 混合返回先例；issue#1581 base64 图吃 70-80% 上下文（jpeg+800px 的量化依据）；~25k token MCP 图像上限

## 登记债（碰到再修，勿认领）

- _suggest_layout pair-window 截断未披露；checked/skipped 三处异构；orbit_cam/shot_cam 无 CAM_ 前缀；玄学评分语义重设计（D-014d）
- test_security.py:389 I001；test_scene_tools_json.py AsyncMock never-awaited；connection_guide 版本扫描复制粘贴三连
- ADR-0010 后果项"版本感知响应规范化"未实现（O-2）；_probe_port socket 泄漏（O-5）；native _send_receive 通用路径丢 code（R-1 微瑕）
- T-05 R-2：headless bootstrap→native 落会话真机未实测——首个摸到 mayapy/GUI 的窗口顺手补验（T-08 真机 checklist 时可顺带）

## 未决 spec 项

- ~~#1 headless 视觉工具能力错误契约~~ ✅ 核销（D-023/D-025：双闸两层+gui_session_required）
- #3 拆分边界→T-07 绞杀者内定；#5 CoS 版本化→T-09；#6 版本号/发布节奏→T-09

## suggested skills

- 执行：implement, tdd（契约层终态钉法已钉死，TDD seam=stub fake）
- 评审：code-review（完成后双轴审计，同 T-03/T-04/T-05 先例）
- 调研：atomcode-research（可选：pip download dcc-mcp-maya 审其截图实现补信息缺口）
- 真机窗口：Maya GUI 会话跑 mayapy 手动 checklist（翻转/kFloat/真内容/Inspector+双客户端）
- 收尾：handoff（再交接）、neat-freak
- 版本控制：gitbutler（but）
