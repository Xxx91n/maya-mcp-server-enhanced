# 质量门：基线冻结 + ratchet，分层严格度

CI（GitHub Actions：ruff + mypy + pytest）+ pre-commit 为发布必需。ruff 全仓库错误数预算冻结、只降不升（ratchet）；mypy strict 对新文件强制、maya_scene_module.py 暂放宽并在拆分完成后收 strict；pytest 全绿且每个 P0 修复必须带回归测试。

Status: accepted (2026-09-16)

## Considered Options
- 首日全绿（清完 188 ruff + 277 mypy 再发布）：否决——阻塞全部修复主线。

## Consequences
- 存量债随绞杀者拆分逐步偿还；预算文件进版本控制。
