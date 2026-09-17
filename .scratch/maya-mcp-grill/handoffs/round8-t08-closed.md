# Handoff — round8 T-08 视觉闭环 关闭（审计通过）

> 生成：2026-09-17 审计窗口（复审）。T-08 两轮：impl(tll)→audit 打回(轻量)→返修 amend→复审通过。
> 本文件=闭环记录；任务书级 spec 仍在 next-round.md，不重复抄写。

## 本轮事实

- T-08 交付：scene_viewport_snapshot + scene_render_preview（GUI-only，双闸 headless，混合 [ImageContent,TextContent]，净零副作用），分支 fix/t08-visual-loop = tll(3fc27d9)+ymv(d91d54d)。
- 审计两轮：reports/2026-09-17-audit-t08.md（打回：F-1 联动规范漏改 test_security.py + capture_invalid 零覆盖；F-2 skip 数失实传染 handoff）→ reports/2026-09-17-audit-t08-closure.md（通过）。
- 当前基线（勿劣化，.venv=Py3.13 为规范环境）：pytest 546p+6s(4 mayapy+2 PySide6)+1 既有 WinError64 环境失败；ruff src=174/repo=237；mypy=221；compileall/uv build/stdio smoke(20工具) 全绿。

## R-1 残余订正项（非阻断，下窗顺手核销）

- reports/2026-09-17-t08-report.md:41 ignore 变体行 "514 passed" → 订正为 **517**（test_visual_tools.py 现 29 条，546-29=517）。
- handoffs/next-round.md:10 对账式 "553=520+新32" → 新实为 **33**（29 视觉+3 security+1 mayapy batch-gate；漏数的又是那枚 mayapy 用例）。

## 真机窗口清单（承袭 next-round.md §遗留，仍全部未核销）

mayapy Tier2（-m mayapy 含 batch-gate 用例）/ GUI Tier3 八项（docs/testing.md，新增第8项 exists-flag 接受度）/ MCP Inspector+Claude Code+Codex 多 block（D-025④ DoD 项）/ PySide2 兼容 / T-05 R-2 headless native 真机。环境限制：本机无 Maya、无 MCP 客户端——不得以 stub 绿充当真机背书。

## 下一 grill 方向：T-09 发布卫生

spec 全文在 handoffs/next-round.md §下一任务（D-001c/D-003c/D-010/D-020④⑤/D-022）：LICENSE、pyproject 身份/仓库改名 mcp-for-maya、README/README_en 逐项核实清单（9vs11 维、CoS 65%、PyPI/URL 幻影、4 Skills 幻影、LOGLEVEL/scripts 幻影、AGENTS 维度口径）、竞品叙事、telemetry 信任卖点、roadmap issue、T-11 版本声明文档级并入。其后 T-10a 最小 CI 门。

## 登记债（碰到再修，勿认领）

承袭 next-round.md §登记债全表 + 本轮新登：_visual_injected/_injected_sessions 会话重连跳过重注入（同款 parity 缺陷，建议归并时同修）；_visual_call/_exec_visual 与 scene_tools 同形双胞胎（绞杀者归并时收）；Scene.gui/_ViewWidget/_MAGIC.get 死面。

## suggested skills

- 执行：implement, tdd；评审：code-review；版本控制：gitbutler（but）
- 收尾：handoff, neat-freak；可选调研：atomcode-research（T-09 LICENSE/发布名核对可联网查证）
