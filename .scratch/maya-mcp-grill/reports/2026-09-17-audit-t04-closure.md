# T-04 审计闭环报告 — 返修复审（通过）

Date: 2026-09-17
Auditor: 审计 Agent（独立窗口）
Scope: 修复提交 ulw 56f565a（fix/t04-security-pipeline，叠于 ovz+qtv 之上；工作区干净）
前序: reports/2026-09-17-audit-t04.md（裁定打回：4 必修 + 6 建议）

## 裁定：通过

F-1~F-10 全部实物复核为真，且关键修复均经 stdio 实测而非仅代码阅读。
修复 commit 同时落审计脚本留档与报告订正，过程合规。

## §1 复验矩阵（重跑同一套验收）

| 验收项 | 返修声明 | 实测 | 结论 |
|---|---|---|---|
| pytest | 457 passed + 3 skipped（+14 回归） | 457 passed, 3 skipped (11.25s) | 一致 ✓ |
| ruff src/ | 174 | Found 174 | 一致 ✓（再降） |
| ruff . | 237 | Found 237 | 一致 ✓ |
| mypy src/ | 221 | Found 221 in 3 files | 一致 ✓ |
| compileall | clean | clean | ✓ |
| wheel | 成功 | maya_mcp_server-0.1.0-py3-none-any.whl (115076B) | ✓ |
| stdio | 18 工具四 hint | 复用前轮脚本仍全绿 | ✓ |

## §2 打回项逐条复核（实物证据）

| 项 | 要求 | 实物证据 | 结论 |
|---|---|---|---|
| F-1 | 宿主侧失败全量 [code] | SessionLookupError[session_unavailable]×3 (session_manager:260/271/278)、ServerNotReadyError[server_not_started] (server.py:112)、ClientType() 包 InputValidationError (server.py:435-438)、client.py:584 TypeError→InputValidationError。实测：scene_snapshot/execute_code/scene_rollback 无会话 → isError [session_unavailable] No Maya sessions available (suggestion: call add_session...) | 修复 ✓ |
| F-2 | §5 矩阵与代码一致 | §5 重写为 verbatim 3 行表（9 读 / 6 mutation / 3 destructive），与 pipeline.TOOL_ANNOTATIONS 逐行一致；§4 新增 resources 绕管线注记；§3 措辞 ../ | 修复 ✓ |
| F-3 | 逃审计路径封闭 | session_id="_default" 预初始化 + _resolve_session_id 移入 try + 函数内 try/except 兜 RuntimeError→_default；新测试 test_session_resolution_failure_still_audited | 修复 ✓ |
| F-4 | traversal 收紧 | security.py re.compile(r"\.\.[\\/]")。实测：a..b.ma 过扫描（败于 session_unavailable 而非误杀）；../x.ma 与 ..\x.ma 均 [blocked_pattern] rejected | 修复 ✓ |

## §3 建议项逐条复核

| 项 | 证据 | 结论 |
|---|---|---|
| F-5 审计双写/永久静默 | record()：_append 失败仅 warn-once-per-streak（_warned 标志，成功即复位）+ logger.info 无条件执行；恢复路径有测试 | 修复 ✓ |
| F-6 标记 region 伪造 | _block_region 改整行等值（stripped==MARKER_BEGIN/END）；引述文本不再造 region；两个新测试钉死 | 修复 ✓ |
| F-7 suggestion 丢失 | server.py:313 isinstance(e,PipelineError) 分支带 suggestion=e.suggestion 重抛 | 修复 ✓ |
| F-8 死代码 | _WARN/rate_limit_max_calls/finally:pass 已删；check→try_consume；_refill→public refill，get_remaining 走公开口 | 修复 ✓ |
| F-9 文档格式 | AGENTS.md:162 行尾空格删净（且补 dry_run 字样）；pipeline 注释 (7)→(6)、(2+1)→(3) | 修复 ✓ |
| F-10 未暴露参数 | maya_setup_guide 签名新增 dry_run: bool=False（实测 stdio 接受）；uninstall_user_setup 删死 port 参数 | 修复 ✓ |

## §4 顺带项与附带发现

- dispatch 阶段 coded 异常 outcome 语义分清：内层 try 置 error，外层 PipelineError 仅在前置拒绝时置 rejected。实测：a..b.ma 无会话 → audit outcome=error；../x.ma → rejected；version_not_found 域错 → error。语义分层正确。
- 文档字面转义清除：threat-model/SECURITY/next-round 中 \\uXXXX 与 __BT__ 残留已全解码（grep=0）。
- 报告 §1 测试分项订正为实数（+32/+12/+24/+5），§6 表述收敛，横幅改“待复审”——本报告出具后可转正。

## §5 残余观察项（不挡本轮，入债/后续）

- tests/test_security.py:389 I001 import 排序仍在预算内残留（ruff repo=237 含它）。
- test_scene_tools_json.py::test_server_execute_code_ok 的 coroutine-never-awaited RuntimeWarning（存量测试 wart，两轮审计均见）。
- add_session 默认端口 7002 vs 文档 7001 —— 已在 T-05 顺带清单。
- code-os-system 连带 block os.popen —— 超 spec 字面的同类防御，可接受；规则注释未写明（微瑕不挡）。
- MCP resources 绕管线（无审计无限流）——threat-model §4 已如实标注，观察转文档化完成。

## §6 过程核查

- 修复提交 ulw 落同一 GitButler 分支；commit message 属实。
- 返修带齐回归测试 +14（每个 F 至少一枚钉）。
- 预算纪律维持只降不升。
- 无新增过程违规；前轮呈报的报告措辞问题已自行订正。

**T-04 验收通过。下一任务按任务表：T-05（Qt 连接层重写，D-013/D-014，ADR-0010）。**
