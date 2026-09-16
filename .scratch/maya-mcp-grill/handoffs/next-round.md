# Handoff — maya-mcp-grill 下一轮任务书（rev4）

> 生成时间：2026-09-16（T-03 交付收尾）。本文档供任意子 Agent 接手执行；结论以决策账本为唯一真源。

## 真源与上下文（先读这些）

- 决策账本（唯一数据源，禁止凭对话记忆补充结论）：`.scratch/maya-mcp-grill/decision-ledger.md`（D-001..D-015 全 current）
- 术语表：`CONTEXT.md`
- 架构决策记录：`docs/adr/0001..0010`
- 锐评原文（已逐条实证+本轮复核修复实况；其中“单 commit/历史为零”“ruff 245”为错误结论）：`.codex_tmp/rui.txt`
- 规则文件：`AGENTS.md`（含联动清单，按拆分进度需同步修订）
- 前轮任务书与审计：`.scratch/maya-mcp-grill/handoffs/round3-t03.md`、`.scratch/maya-mcp-grill/reports/`

## 已完成（验收事实，非计划）

- **T-01/T-02** 已交付于 commit 63dfeae（branch fix/t01-t02-stub-and-p0），两轮审计通过（reports/2026-09-16-audit-t01-t02-rev2.md 判定“通过带登记残留”）。
- **T-03** 已交付于 commit lkt（branch fix/t03-checkpoint-rollback，stacked on grill/round4-rui-review-docs）：checkpoint=exportAll 内存态真快照、rollback=S2 重绑+四字段结构化返回、auto_before_rollback 失败即中止+discard_current_state 逃生、untitled ad-hoc（workspace/checkpoints、cp_adhoc_ 前缀）、同名拒绝+prev_ 保留件、快照删改检测报“快照已丢失”、全部 file 操作 prompt=False。隐藏案例 1-4 全部有测试。报告：reports/2026-09-16-report-t03.md。
- 新基线（重跑口径）：pytest 369 passed + 3 skipped；compileall OK；pip wheel OK；stdio init 2.14.2 / tools=18 / ping（scene_checkpoint 含 name/overwrite、scene_rollback 含 filename/discard_current_state）；ruff src=185 / 全仓=244；mypy=223。
- 已落账：D-016（T-03 内定 spec：文件名方案、ad-hoc 位置、白名单、original_file_status 值域）。
- 覆盖 rui.txt：P0-1 错误透传 / P0-2 JSON 传参 / P0-4 _world_bbox / P0-5 采样披露 / P1-2 三连 全修；P1-1 中 KeyError 已修。
- 未修项均有归属：P0-3→T-03、P1-1 双实现+伪引用→T-06、P1-3→T-05、P2 文档/许可/CI→T-09/T-10、connection_guide 越权→T-04。

## 工作约定（承袭，勿违）

- 写文件一律经 ctx_execute（node.js fs），防嵌套断连。
- 版本控制一律用 but，禁止 git 写命令；每个实现轮次用独立分支。
- 账本纪律：新增/变更决策先记 D-xxx；与 current 冲突标 revised 呈报，不静默改向。
- 测试纪律（D-004/D-005/D-009）：每修复带回归测试（须在 base src 可复现 RED——注意 editable install 陷阱，PYTHONPATH 指 base 树重跑）；ruff/mypy 预算只降不升。
- 文档纪律：README/AGENTS.md 不超前于代码；落地时同 commit 同步；commit message 字字为真。

## 任务表（依赖序）

| # | 任务 | 覆盖 D-xxx | 交付物/要点 | suggested skills |
|---|------|-----------|------------|------------------|
| T-04 | 安全统一管线 + 威胁模型文档（并入 D-014b）：18 工具收口统一校验/限流/审计/pattern 扫描；SECURITY.md + README 警示框 + 边界声明（禁 sandbox/secure）+ 端口暴露说明 + 危险工具 annotations + 审计日志 schema；并入 connection_guide 越权收口：userSetup.py 覆盖改合并式写入或显式确认、fallback“已生成”虚假文案修正、硬编码示例路径清除、_get_platform 与 utils.get_platform 去重 | D-008, D-014 | 见 ADR-0005 | implement, code-review, security-review-orchestrator |
| T-05 | 连接层 Qt 重写（并入 D-014c）：readyRead 事件驱动 + 逐连接队列 + 长度前缀分帧（8-16MiB 帧上限）+ typed error + 指数退避(0.5/1/2s) + localhost-only + 健康探针 + _failed_ports 去重；修 add_session 丢 bootstrap 返回值；GUI 会话移除 temp-file 注入；native 文档化为 bootstrap/headless 最小通道；顺带清理：StreamWriter 5MB 上限接线（_MAX_STREAM_BUFFER_SIZE 现仅定义未用）、client.py write_module 死响应、__main__ 调试脚本移出库代码（client.py/session_manager.py 同款） | D-013, D-014 | 见 ADR-0010 | implement, tdd, research |
| T-06 | 审美引擎单源化（并入 D-014a）：aesthetic_engine.py 经 write_module 注入为唯一真源；_mcp_scene 审美函数改 采集→调用→格式化；对齐 analyze_aesthetics/scene_review 采集字段契约；删内联复制品；**重写时清算伪学术引用**（McCamy/mired/“Within 15%”/Aesthetic3D r=0.78/arXiv 2016/Tripo3D/Narrative 2025——不搬进 Maya）；玄学评分算法偏差只记录不重设计（登记债） | D-006, D-014 | 见 ADR-0003 | implement, tdd |
| T-07 | 绞杀者拆分 + 验证器注册表：maya_scene_module 按能力矩阵增量拆子模块；scene_review 检查改自注册 validator（name/severity/family/order）；注册 API 限 register(name,fn,severity,family) 且隔离会话/缓存/回滚内部；单 check 异常记 check_error 不中断；自定义注入走 write_module+注册 API（文档口径=逃生舱，非卖点） | D-004, D-011 | 见 ADR-0002/0008 | codebase-design, implement, tdd |
| T-08 | 视觉闭环双工具：scene_viewport_snapshot（playblast；headless 返回显式能力错误）+ scene_render_preview（低分辨按需）；MCP Image 回传；挂进 ICEV VERIFY 叙事 | D-002, D-003 | 见 ADR-0001 | implement, research |
| T-09 | 发布卫生 + 文档真实性：LICENSE（MIT 留 chadrik notice + 自有 line）；pyproject 改名 mcp-for-maya/URLs 指本仓库；README 逐项核对（18 工具、11 维、分值表、删虚假承诺：上游 pip install/4 Codex Skills/LOGLEVEL/scripts/）；对比叙事 + fork 署名；GitHub 仓库改名 mcp-for-maya；占住 PyPI 名 | D-001, D-003, D-010 | 见 ADR-0001/0007 | neat-freak, implement |
| T-10 | CI/质量门：GitHub Actions（ruff 预算冻结+ratchet / mypy 新文件 strict、maya_scene_module 暂放宽 / pytest）+ pre-commit；预算文件进版本控制 | D-009 | 见 ADR-0006 | implement |
| T-11 | 版本支持声明：Maya 2024+/py3.10+ 矩阵入 README+pyproject，2023 及以下不阻止不担保 | D-012 | 见 ADR-0009 | implement |
| T-12 | 路线图文档：资产生态薄集成（Poly Haven→scene_plan zone 语义+bbox 尺寸推荐，许可审计内置）；Sketchfab/AI 生成暂缓；safe_mode opt-in P2（zorak1103 模板：默认关+mode 字段+safety-net-not-boundary）；ShotGrid/USD 长期项；scene_adopt(S3) 后续增强 | D-002, D-003, D-008 | ROADMAP.md | writing-for-agents |

## 登记债（碰到再修，勿认领为本轮任务）

- _suggest_layout pair-window(i+20) 截断仍未披露（constraints/overlaps 已补 pair_window/pairs_skipped）
- checked/skipped 披露字段三处异构未统一
- orbit_cam/shot_cam 默认名无 CAM_ 前缀
- 玄学评分算法语义重设计（golden ratio 杂物堆偏差/人体工学靠名字/走廊只看 bbox X 分量）——超出“修复对齐”范围，仅登记（D-014d）
- connection_guide 三处版本扫描函数复制粘贴（T-04 顺带可清）

## 未决 spec 项（账本未覆盖——进实现前须先定，禁止当成已拍板）

1. headless 会话视觉工具能力错误的具体契约（T-08 内定）
2. README 声称的 4 个 Codex Skills：删除 or 补真——建议删除并记入 ROADMAP（T-09 内定）
3. 子模块拆分边界明细（T-07 内定）
4. 全工具结构化错误返回格式统一规范（自 T-03 起每任务定 schema 时保持一致）
5. CoS 格式是否作为公共契约版本化（T-09/T-12）
6. 首发版本号与发布节奏（T-09 内定）
7. ~~untitled 场景 + auto_before_rollback 组合~~（已定：D-016d，auto 快照落 workspace ad-hoc 目录，失败即中止）
8. ~~ad-hoc 快照文件名标记~~（已定：D-016a，cp_adhoc_{name}.ma 落 <workspace>/checkpoints/）

## 完成判定（Definition of Done）

- pytest 全绿且每修复带回归；ruff/mypy 预算只降不升；CI 三件套在线
- 18 工具经统一管线；威胁模型 8 项齐备；LICENSE/pyproject/仓库名/包名一致
- checkpoint→rollback 在 mayapy 档含 reference-edit 往返用例；D-015 边缘案例 1-4 有测试
- README 每数字可对代码复核；无 sandbox/secure 误用词；无伪学术引用残留

## suggested skills

- 执行类：implement, tdd, diagnosing-bugs, code-review
- 设计类：codebase-design, domain-modeling（新决策须回写账本+ADR）
- 收尾类：neat-freak（T-09 文档对账）、handoff（再交接）
- 版本控制：gitbutler（but）
- 调研类：research / atomcode-research（多源需引用时；atomcode 串行+配额注意）
