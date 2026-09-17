# Handoff — maya-mcp-grill 下一轮任务书（rev5）

> 生成时间：2026-09-17（T-03 审计通过 + round5 grill 定稿，T-04 spec 闭合）。本文档供任意子 Agent 接手执行；结论以决策账本为唯一真源。

## 真源与上下文（先读这些）

- 决策账本（唯一数据源，禁止凭对话记忆补充结论）：`.scratch/maya-mcp-grill/decision-ledger.md`（D-001..D-019 全 current）
- 术语表：`CONTEXT.md`；架构决策记录：`docs/adr/0001..0011`
- 锐评原文（已两轮逐条实物复核；其“单 commit/历史为零”“ruff 245”为错误结论）：`.codex_tmp/rui.txt`
- 规则文件：`AGENTS.md`（含联动清单，按拆分进度需同步修订）
- 历史交接与审计：`.scratch/maya-mcp-grill/handoffs/`、`.scratch/maya-mcp-grill/reports/`

## 已完成（验收事实，非计划）

- **T-01/T-02**：交付 63dfeae（branch fix/t01-t02-stub-and-p0），两轮审计通过（reports/2026-09-16-audit-t01-t02-rev2.md）。
- **T-03**：交付并经 PR #1 合并入 main（5d6cfb2）：checkpoint=exportAll 内存态真快照、rollback=S2 重绑+四字段结构化返回、auto_before_rollback 失败中止+discard_current_state 逃生、untitled ad-hoc（workspace/checkpoints、cp_adhoc_ 前缀）、同名拒绝+prev_ 保留件、快照删改检测报“快照已丢失”、全部 file 操作 prompt=False、'..' 穿越修复；D-007/D-015/D-016 全落地；O1-O9 观察项 fix 轮全部修复（审计：reports/2026-09-17-audit-t03.md）。
- **基线**（2026-09-17 复验口径，勿劣化）：pytest 370 passed + 3 skipped；ruff src=185 / 全仓=244；mypy=223；compileall+wheel+stdio（init 2.14.7 / 18 tools / ping）OK。
- **rui.txt 复核终态**：P0-1~P0-5（含穿透不计违例残留 bug）、P1-2 三连、P1-1 KeyError 全修；P1-1 双实现+伪引用→T-06；P1-3 全 8 子项→T-05；P2 全项→T-09/T-10；connection_guide+security.py+helper 注释→T-04。无孤儿项。

## 工作约定（承袭，勿违）

- 写文件一律经 ctx_execute（node.js fs），防嵌套断连。
- 版本控制一律用 but，禁止 git 写命令；每个实现轮次用独立分支。
- 账本纪律：新增/变更决策先记 D-xxx；与 current 冲突标 revised 呈报，不静默改向。
- 测试纪律（D-004/D-005/D-009）：每修复带回归测试（须在 base src 可复现 RED——注意 editable install 陷阱，PYTHONPATH 指 base 树重跑）；ruff/mypy 预算只降不升。
- 文档纪律：README/AGENTS.md 不超前于代码；落地时同 commit 同步；commit message 字字为真。
- 错误契约（D-019）：新增错误一律按双层 schema——宿主失败走异常+MCP isError+code 前缀；Maya 域结果走 {error:{code,message,suggestion?}}。

## 任务表（依赖序）

| # | 任务 | 覆盖 D-xxx | 交付物/要点 | suggested skills |
|---|------|-----------|------------|------------------|
| T-04 | 安全统一管线 + 威胁模型文档 + connection_guide 收口 | D-008, D-014, D-017, D-018, D-019 | **管线**：18 工具收口统一校验/限流/审计/pattern 扫描；审计=独立 JSONL（platformdirs 用户目录，schema=event_id/timestamp/session_id/tool_name/input_summary 脱敏摘要/outcome 含 rejected/duration_ms/warnings+rule_id；0600+独立轮转+写失败不阻断）+logger 双写；限流=读写分桶 token bucket（变更 ~20/60s、读 ~100/60s、per-session、超限显式错误）；pattern=非 code 参数 warn-only+精确规则 block（filename 穿越、code 命令执行注入）+rule_id×tool×param 排除表；annotations 四 hint 全标（矩阵见 ADR-0005）。**文档**：威胁模型 8 项+SECURITY.md+README 警示框（禁 sandbox/secure 词）。**connection_guide**：userSetup.py 标记块 A′ 语义（不存在直接建/无块待 confirm=True 二次写/有块原位替换/不可解析拒绝/无 force/.bak.<ts>/块自守 try/except+幂等+无 UI 时序依赖/uninstall 对称摘块）+fallback 诚实文案+硬编码路径清除+_get_platform 去重 utils。**顺带**：security.py 三处诚信度（Token bucket 注释随真 bucket 实装修正、函数内 import re、Windows regex 半截）、helper __builtins__ 自欺注释。**错误迁移**：存量裸 {"error":str(e)} 与 _rb_error 迁至 D-019 形。详见 ADR-0005 + ADR-0011 | implement, code-review, security-review-orchestrator |
| T-05 | 连接层 Qt 重写 | D-013, D-014 | readyRead 事件驱动+逐连接队列+长度前缀分帧（8-16MiB）+typed error+指数退避(0.5/1/2s)+localhost-only+健康探针+_failed_ports 去重；修 add_session 丢 bootstrap 返回值；GUI 会话移除 temp-file 注入；native 文档化为 bootstrap/headless 最小通道；顺带：StreamWriter 5MB 上限接线、client.py write_module 死响应、__main__ 调试脚本移出库代码（client.py/session_manager.py 同款）、add_session 默认端口 7002 与文档 7001 对齐。见 ADR-0010 | implement, tdd, research |
| T-06 | 审美引擎单源化 | D-006, D-014 | aesthetic_engine.py 经 write_module 注入为唯一真源；_mcp_scene 审美函数改 采集→调用→格式化；对齐 analyze_aesthetics/scene_review 字段契约；删内联复制品；**重写时清算伪学术引用**（McCamy/mired/“Within 15%”/Aesthetic3D r=0.78/arXiv 2016/Tripo3D/Narrative 2025——不搬进 Maya）；玄学评分算法偏差只记录不重设计（登记债）。见 ADR-0003 | implement, tdd |
| T-07 | 绞杀者拆分 + 验证器注册表 | D-004, D-011 | maya_scene_module 按能力矩阵增量拆子模块；scene_review 检查改自注册 validator（name/severity/family/order）；注册 API 限 register(name,fn,severity,family) 且隔离会话/缓存/回滚内部；单 check 异常记 check_error 不中断；自定义注入走 write_module+注册 API（文档口径=逃生舱，非卖点）。见 ADR-0002/0008 | codebase-design, implement, tdd |
| T-08 | 视觉闭环双工具 | D-002, D-003 | scene_viewport_snapshot（playblast；headless 返回显式能力错误）+ scene_render_preview（低分辨按需）；MCP Image 回传；挂进 ICEV VERIFY 叙事。见 ADR-0001 | implement, research |
| T-09 | 发布卫生 + 文档真实性 | D-001, D-003, D-010 | LICENSE（MIT 留 chadrik notice+自有 line）；pyproject 改名 mcp-for-maya/URLs 指本仓库；README 逐项核对（已核实问题清单见下节）；对比叙事+fork 署名；GitHub 仓库改名 mcp-for-maya；占住 PyPI 名。见 ADR-0001/0007 | neat-freak, implement |
| T-10 | CI/质量门 | D-009 | GitHub Actions（ruff 预算冻结+ratchet / mypy 新文件 strict、maya_scene_module 暂放宽 / pytest）+ pre-commit；预算文件进版本控制。见 ADR-0006 | implement |
| T-11 | 版本支持声明 | D-012 | Maya 2024+/py3.10+ 矩阵入 README+pyproject，2023 及以下不阻止不担保。见 ADR-0009 | implement |
| T-12 | 路线图文档 | D-002, D-003, D-008 | 资产生态薄集成（Poly Haven→scene_plan zone 语义+bbox 尺寸推荐，许可审计内置）；Sketchfab/AI 生成暂缓；safe_mode opt-in P2（zorak1103 模板）；ShotGrid/USD 长期项；scene_adopt(S3) 后续增强。产出 ROADMAP.md | writing-for-agents |

## T-09 README 已核实问题清单（rev5 复核增列，逐条对代码核销）

- “15 个 MCP 工具”（README:209）→ 实际注册 18；“9 维度”（:143）vs “11 维”（:22）互搏→代码实装 11 个 check
- `pip install maya-mcp-server`（:31）指向上游 chadrik 包；“项目提供 4 个 Codex Skills”（:192）仓库无 skills 文件；“省 65% token”（:179/:214）为论文数字挪用非自家 benchmark
- 分值表（:229-241）与代码注释不符；AGENTS.md 同款错表（已部分订正）；LOGLEVEL=DEBUG 与 scripts/ 引用不存在

## 登记债（碰到再修，勿认领为本轮任务）

- _suggest_layout pair-window(i+20) 截断仍未披露（constraints/overlaps 已补 pair_window/pairs_skipped）
- checked/skipped 披露字段三处异构未统一
- orbit_cam/shot_cam 默认名无 CAM_ 前缀
- 玄学评分算法语义重设计（golden ratio 杂物堆偏差/人体工学靠名字/走廊只看 bbox X 分量）——超出“修复对齐”范围，仅登记（D-014d）
- connection_guide 三处版本扫描函数复制粘贴（T-04 顺带可清）

## 未决 spec 项（进对应任务前须先定，禁止当成已拍板）

1. headless 会话视觉工具能力错误的具体契约（T-08 内定）
2. README 声称的 4 个 Codex Skills：删除 or 补真——建议删除并记入 ROADMAP（T-09 内定）
3. 子模块拆分边界明细（T-07 内定）
4. ~~全工具结构化错误返回格式统一规范~~（已定：D-019 双层契约，ADR-0011）
5. CoS 格式是否作为公共契约版本化（T-09/T-12）
6. 首发版本号与发布节奏（T-09 内定）

## 完成判定（Definition of Done）

- pytest 全绿且每修复带回归；ruff/mypy 预算只降不升；CI 三件套在线
- 18 工具经统一管线；威胁模型 8 项齐备；审计 JSONL 落盘可 jq 回放；四 hint 全标
- checkpoint→rollback 在 mayapy 档含 reference-edit 往返用例；D-015 边缘案例 1-4 有测试
- README 每数字可对代码复核；无 sandbox/secure 误用词；无伪学术引用残留
- 错误返回符合 D-019 双层契约；userSetup.py 写入符合 D-017 A′ 语义

## suggested skills

- 执行类：implement, tdd, diagnosing-bugs, code-review
- 设计类：codebase-design, domain-modeling（新决策须回写账本+ADR）
- 收尾类：neat-freak（T-09 文档对账）、handoff（再交接）
- 版本控制：gitbutler（but）
- 调研类：research / atomcode-research（多源需引用时；atomcode 串行+配额注意）
- 安全专项：security-review-orchestrator（T-04 取证）
