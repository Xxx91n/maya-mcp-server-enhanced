# T-08 复审报告 — 视觉闭环（裁定：通过，附残余订正项 R-1）

Date: 2026-09-17
Auditor: 审计 Agent（独立窗口，不动手修）
Scope: fix/t08-visual-loop 复审 = tll(3fc27d9, amended) + ymv(d91d54d, amended)；audit/t08 zsm 未被触碰；zz 干净无 fixup commit
前序: reports/2026-09-17-audit-t08.md（打回返工裁定）

## 裁定：通过

F-1/F-2 主体修复全部实物复核为真，硬验收重跑全绿。残余两处 scratch 文档陈旧格（R-1）
属非阻断订正项——实现层零问题，修复窗口可闭；R-1 由下一 docs 触手（T-09 起手）顺手核销。

## §1 复审矩阵（同一套验收全量亲跑）

| 验收项 | 返修声明 | 审计实测 | 结论 |
|---|---|---|---|
| compileall | OK | OK | ✓ |
| pytest 三件套 | 127 passed | 127 passed (4.10s) | ✓ |
| pytest 全量 | 1f(flake)/546p/6s | 1 failed(同枚环境性 WinError64), 546 passed, 6 skipped | ✓ |
| ruff src/ / repo | 174 / 237 持平 | 174 / 237 | ✓ ratchet 未破 |
| mypy src/ + 新文件 | 221 / 0err | 221 in 3 files / Success 2 files | ✓ |
| uv build | wheel+sdist | whl+tar.gz 重建成功 | ✓ |
| stdio smoke | 20工具/ann全/hint无缺口/ping{} | toolCount=20、missingAnnotations=[]、hintGaps=[]、ping={} | ✓ |
| 双件安全测试 | 93 passed | 三件套内 test_security+test_visual_tools 全绿（127 含其 93+） | ✓ |

## §2 返修落点核对

| 返修项 | 实物证据 | 结论 |
|---|---|---|
| F-1 test_security.py +3 钉 | test_security.py:235-250 TestPipelineErrorContract 新增 gui_session_required/capture_empty/capture_invalid，各钉 [code] 前缀+suggestion 渲染，模式与既有三钉一致 | 真 |
| F-1 capture_invalid 两分支钉 | test_visual_tools.py:359-397 test_bad_base64（!!!not-base64!!! payload）+ test_magic_mismatch（GIF89a 冒充 jpeg）→ 各 pytest.raises(InvalidCaptureError)，精确覆盖 visual_tools.py:141-144/:153-157 | 真 |
| F-2 报告主行订正 | report:39 "546 passed, 6 skipped（4 mayapy + 2 PySide6；.venv 无 PySide6）"=实测 | 真 |
| F-2 next-round.md 基线行 | :8 "546+6skip+1"、:10 skip 构成注明 | 真（对账式有算术毛边，R-1） |
| F-2 规范环境声明 | report:114-115 明写系统 python3.11 装 PySide6 会得 4-skip 假象；实测 .venv=Python 3.13.13 无 PySide6 | 真且有价值（环境陷阱已文档化） |
| O-1 修复 mkstemp prefix | visual_module.py:262 prefix="_mcp_visual_"→产物与测试 glob 同前缀，覆盖洞闭合 | 真 |
| O-5 修复 frame int 强转 | visual_module.py:350 frame=int(cmds.currentTime(query=True)) | 真 |
| O-6 Tier3 第 8 项 | testing.md 清单 7→8 项，:71 exists pre-check 真机接受度入列 | 真 |
| O-4 登记不挡 | report:119 明记 _visual_injected parity 债 | 真（合规登记） |
| amend 归位 | tll←visual_module/test_visual_tools/test_security/testing.md；ymv←report/next-round.md；无 fixup commit；audit zsm 未动 | 真 |

## §3 残余订正项 R-1（非阻断，须订正）

修复窗口订正了 F-2 主数（skip 5→6、全量 541→546），但漏改两处被自家返修改变了真值的旧格：

1. **report:41 ignore 变体行**仍写 "514 passed（旧测试基线状态，-32 新钉）"——test_visual_tools.py
   现为 29 条（27+2），实测该命令输出 **1 failed, 517 passed, 6 skipped**（546-29=517）。
   "-32 新钉"注记同样毛边（见下）。
2. **next-round.md:10 对账式**"553 collected = 旧 520 + 新 32"——实测 collected=553，
   旧基线 520，**新实为 33**（29 视觉契约 + 3 security 钉 + 1 mayapy batch-gate）。
   被漏数的又是 test_visual_module_batch_gate_in_real_maya——与 F-2 原始漏数同源。

处置：非阻断。下窗（T-09 起手或任意 docs 触手）将 report:41 订正为 517 并将对账式改为
"553 = 旧520 + 新33（29 视觉 + 3 security + 1 mayapy gate）"。属 scratch 档诚实性维护，
不影响产品面证据链（主数全部已核真）。

## §4 结论

- T-08 视觉闭环实现 = spec 忠实 + 验收全绿 + 返修达标。**T-08 关闭**。
- 登记债/真机清单维持：mayapy Tier2、GUI Tier3 八项、MCP Inspector+双客户端、PySide2、
  _visual_injected/_injected_sessions 重连缺陷、lookThru 参数序、verticalFlip 方向。
- 下一任务 = T-09 发布卫生（spec 已在 handoffs/next-round.md §下一任务）。
