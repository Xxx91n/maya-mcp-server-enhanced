# Handoff — maya-mcp-grill 下一轮任务书

> 生成时间：2026-09-16。本文档供任意子 Agent 接手执行；结论以决策账本为唯一真源。

## 真源与上下文（先读这些）

- 决策账本（唯一数据源，禁止凭对话记忆补充结论）：`.scratch/maya-mcp-grill/decision-ledger.md`（D-001..D-013 全 current）
- 术语表：`CONTEXT.md`
- 架构决策记录：`docs/adr/0001..0010`
- 锐评原文（已逐条实证，仍须辩证看待——其中“单 commit”为错误结论，实际 18 commits）：`.codex_tmp/rui.txt`
- 规则文件：`AGENTS.md`（含联动清单，按 D-004 拆分进度需同步修订）

## 工作约定

- 写文件一律经 ctx_execute（node.js fs），防嵌套断连。
- 版本控制一律用 `but`（GitButler），禁止 git 写命令。
- 账本纪律：新增/变更决策必须先记 D-xxx 再动手；与 current 决策冲突时标 revised 并呈报，不静默改向。
- 测试纪律（D-004/D-005/D-009）：每个 P0 修复必带回归测试；ruff/mypy 预算只降不升。
- 文档纪律：README/AGENTS.md 在对应代码落地前不得提前写成已实现；落地时同 commit 同步。

## 任务表（依赖序）

| # | 任务 | 覆盖 D-xxx | 交付物 | suggested skills |
|---|------|-----------|--------|------------------|
| T-01 | Maya 端测试脚手架：tests/maya_stub/ 自建 maya.cmds+maya.api.OpenMaya 假实现（含语义正确的矩阵/8角点bbox数学）；pytest 接线；mayapy 真机档文档化（本地手动、不卡 CI） | D-004, D-005 | stub 包 + 首批可跑测试 + 真机档说明 | tdd, implement |
| T-02 | P0 正确性修复批：server.py 错误透传（error 字段不再丢弃）+删除 get_output() 幻觉引用；scene_tools 全量 JSON 序列化传参（消灭 rules_escaped 尸体与注入面）；抽 world_bbox 8角点统一 measure/conflicts/建议路径；采样上限披露（checked/skipped 字段）；scene_assert exists:false 与 bbox_min 实装；zone coverage total_objects 修正；camera_orbit 改建 center locator 再约束 | D-004, D-005（修复清单源自 rui.txt P0-1/2/4/5 与 P1-2） | 修复 + 每项回归测试 | tdd, diagnosing-bugs, implement |
| T-03 | checkpoint/rollback 重做：exportAll 真快照 + basename 白名单 + auto_before_rollback 改 exportAll + 结构化场景身份返回（scene_name_before/after/original_file_status/scene_rebound_to）+ 两诚实边界入文档 + mayapy 档 reference-edit 往返回归用例 | D-007 | 见 ADR-0004 | tdd, implement |
| T-04 | 安全统一管线 + 威胁模型文档：18 工具收口统一校验/限流/审计/pattern 扫描；SECURITY.md + README 警示框 + 边界声明（禁用 sandbox/secure）+ 端口暴露说明 + 危险工具 annotations + 审计日志 schema | D-008 | 见 ADR-0005 | implement, code-review, security-review-orchestrator |
| T-05 | 连接层 Qt 重写：readyRead 事件驱动 + 逐连接队列 + 长度前缀分帧（8-16MiB 帧上限）+ typed error + 指数退避 + localhost-only + 健康探针 + _failed_ports 去重；修 add_session 丢 client bug；GUI 会话移除 temp-file 注入；native 文档化为 bootstrap/headless 最小通道 | D-013 | 见 ADR-0010 | implement, tdd, research |
| T-06 | 审美引擎单源化：aesthetic_engine.py 经 write_module 注入；_mcp_scene 审美函数改为采集→调用→格式化；对齐 analyze_aesthetics 与 scene_review 采集字段契约；删除内联复制品；KeyError 路径修掉 | D-006 | 见 ADR-0003 | implement, tdd |
| T-07 | 绞杀者拆分 + 验证器注册表：maya_scene_module 按能力矩阵增量拆为子模块；scene_review 检查改为自注册 validator（name/severity/family/order）；注册 API 限 register(name,fn,severity,family) 且隔离内部状态；单 check 异常记 check_error；自定义注入走 write_module+注册 API（文档口径=逃生舱） | D-004, D-011 | 见 ADR-0002/0008 | codebase-design, implement, tdd |
| T-08 | 视觉闭环双工具：scene_viewport_snapshot（playblast；headless 返回显式能力错误）+ scene_render_preview（低分辨按需）；MCP Image 回传；挂进 ICEV VERIFY 叙事 | D-002, D-003 | 见 ADR-0001 | implement, research |
| T-09 | 发布卫生 + 文档真实性：LICENSE（MIT 留 chadrik notice + 自有 line）；pyproject 改名/URLs；README 全面核对（18 工具、11 维、分值表、删除虚假承诺：上游 PyPI 安装命令、4 Codex skills、LOGLEVEL、scripts/）；对比叙事 + fork 署名；仓库改名 mcp-for-maya；占住 PyPI 名 | D-001, D-003, D-010 | 见 ADR-0001/0007 | neat-freak, implement |
| T-10 | CI/质量门：GitHub Actions（ruff 预算冻结+ratchet / mypy 新文件 strict、maya_scene_module 暂放宽 / pytest）；pre-commit；预算文件进版本控制 | D-009 | 见 ADR-0006 | implement |
| T-11 | 版本支持声明：README+pyproject 写 Maya 2024+/py3.10+ 支持矩阵，2023 及以下不阻止不担保 | D-012 | 见 ADR-0009 | implement |
| T-12 | 路线图文档：资产生态薄集成（Poly Haven→scene_plan zone 语义+bbox 尺寸推荐，许可审计内置）；暂缓 Sketchfab/AI 生成；safe_mode opt-in P2（zorak1103 模板）；ShotGrid/USD 长期项；scene_adopt(S3) 后续增强 | D-002, D-003, D-008 | ROADMAP.md | writing-for-agents |

## 未决 spec 项（账本未覆盖——进入实现前须先定，禁止当成已拍板）

1. headless 会话上视觉工具能力错误的具体契约（错误类型/文案）。
2. README 声称的 4 个 Codex Skills：删除 or 补真——建议删除并记入 ROADMAP。
3. 子模块拆分边界明细（snapshot/review/aesthetics/planning 职责线）。
4. 全工具结构化错误返回格式统一规范。
5. scene_review/scene_validate 采样披露字段格式（checked/skipped 命名与位置）。
6. CoS 格式是否作为公共契约版本化。
7. 首发版本号与发布节奏（mcp-for-maya 的 0.1.0 起步？）。

## 完成判定（Definition of Done）

- pytest 全绿且新增回归覆盖每个 P0；ruff/mypy 预算文件只降不升；CI 三件套在线。
- 18+2 工具全部经统一管线；威胁模型文档 8 项齐备；LICENSE/pyproject/仓库名/包名一致。
- checkpoint→rollback 在 mayapy 真机档含 reference-edit 往返用例。
- README 每个数字可对代码复核；无 sandbox/secure 误用词。

## suggested skills

- 执行类：implement, tdd, diagnosing-bugs, code-review
- 设计类：codebase-design, domain-modeling（新决策须回写账本+ADR）
- 收尾类：neat-freak（T-09 文档对账）、handoff（再交接）
- 版本控制：gitbutler（but）
- 调研类：research / atomcode-research（多源需引用时；注意 atomcode 串行+配额）
