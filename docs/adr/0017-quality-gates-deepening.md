# 质量门深化：mypy 基线闸 + pre-commit 薄集 + formatter 采纳 + per-rule 预算

第二轮锐评对账全闭环后，T-10b 完成 T-10a 未闭的质量门半弧：mypy 223 存量错误（集中 3 遗留文件）经 **mypy-baseline** 基线化入 CI（mypy|mypy-baseline filter，行号归零防合并冲突、逐 PR 分辨引入/修复、resolve 后 sync=天然 ratchet；mypy 2.1.0 兼容性本机 smoke 实证）；新增 pre-commit 官方框架薄集（8 钩子含 ruff-check+ruff-format，mypy 刻意不进钩子），CI 以 GHA `pre-commit run --all-files` 兜底；**ruff-format 正式采纳**——一次性 mass reformat 独立 commit+完整 SHA 入 .git-blame-ignore-revs；ruff 预算升 per-rule 温和版（rule→count）；coverage 仅报告不设门；macOS 矩阵缓行带显式翻案条件。

Status: accepted (2026-09-19)

## Considered Options

- **mypy 基线选自研总量计数预算（仿 check_ruff_budget.py）**：否决——裸计数随文件增删自然波动（本仓实证 277→223 漂移）、无法分辨“减 5 旧错加 5 新错”；mypy#9540 官方定 baseline out-of-scope，mypy-baseline 是类型域唯一逐 PR 可分辨的成熟机制；代价=例外批准的第三方 dev 依赖（版本 pin≥7 天+smoke 已过）。
- **mypy 逐文件/按错误码预算**：否决——223 错集中 3 文件且同质（untyped-decorator 类为主），细分收益不抵维护成本。
- **mypy 进 pre-commit 钩子**：否决——隔离环境慢+additional_dependencies 复制依赖集=社区公认痛点；mypy 留 CI 基线闸，本地反馈靠 IDE。
- **永不引入 formatter 仅守 lint 门（初案）**：否决——调研推翻：Black 官方迁移指南明定“一次性 mass reformat+.git-blame-ignore-revs”为标准路径；引号/换行/尾逗号风格是 PR 无意义 diff 最大源，守 lint 不加 formatter=付 90% 工具链成本拿 10% 收益；37/48 文件 churn 对本仓规模可吸收且当前无在飞分支=最佳窗口。
- **渐进式 staged-only 格式化**：否决——适用条件=巨型 monorepo+高频在飞分支，本仓不满足；格式 diff 混入功能改动=review 反模式。
- **pre-commit.ci 第三方 App**：否决——repo 写权限+每周 autoupdate PR=上游 hook 仓库被攻破自动流入 main 的通道（OWASP CICD-SEC-08+Trivy 供应链事件实证）；官方 pre-commit/action 已 maintenance-only；hook rev 维护走 Dependabot pre-commit ecosystem 月度或手动 autoupdate 过人眼。
- **coverage 设绝对阈值门**：否决——stub 主导+休眠模块稀释下总量百分比双向失真（Codecov/Vinted/r-devops 三源：patch coverage 才测真东西）；门控触发=T-06 休眠归置+真机档后对新代码 patch 设门。
- **macOS 进全矩阵**：否决——Maya 无 macOS 可 CI 自动化形态（runner 仅测纯 Python，差异已被 ubuntu/windows 覆盖）+$0.062/min=Linux 10 倍成本；翻案条件=pypistats macOS 用户实证/真实 macOS bug/打 macOS 产物→届时单冒烟 job。

## Consequences

- **mypy 基线闸**（D-044①）：dev-dep mypy-baseline（pin≥7 天版本）；CI 新 job `python -m mypy src/ | mypy-baseline filter`；mypy-baseline.txt 入库；resolve 后 `mypy-baseline sync` 重基线=ratchet；配套 pyproject [tool.mypy] 增 warn_unused_ignores+warn_unused_configs 棘爪（已 strict=true）；ADR-0006/D-009 ratchet 心智平移类型域。
- **pre-commit 薄集**（D-044②/D-045）：.pre-commit-config.yaml——check-yaml/check-merge-conflict/check-case-conflict(Win 开发+Linux CI 实证风险)/end-of-file-fixer/trailing-whitespace/debug-statements+ruff-check+ruff-format（rev 与 CI ruff 对齐）；CI 兜底=GHA 步 `pip install pre-commit && pre-commit run --all-files`（contents:read 自托管）；CONTRIBUTING 补 dev-setup 节。
- **formatter 采纳**（D-045①）：`ruff format .` 一次性独立 commit（“style: no logic changes”，纯格式零逻辑变更=硬约束，含逻辑则掩盖 bug 作者+毁 ignore-revs 语义）+完整 40 位 SHA 入 .git-blame-ignore-revs（GitHub UI 原生读；缩写静默忽略）；reformat 后重跑 ruff check 实证计数不跳升（机制推断只降/平——format 不改 AST、E501 被 formatter 接管后可 ignore）否则重基线说明；Black 风格自此为全仓强制规范=已知情接受的品味承诺。
- **per-rule ruff 预算**（D-044③）：check_ruff_budget.py 升 (rule→count) dict+ruff-baseline.json 一次性迁移；堵“规则间互相倒贴”泄漏（修 10 E501 混进 5 F401 净降过关）；无大型开源先例=自研机制自负、风险低。
- **coverage 报告态**（D-044④）：pytest-cov dev-dep+pytest --cov 拿真实基线人工读一次；不设门。
- **macOS 缓**（D-044⑤）：翻案条件入登记债。
- **证据强度说明**：mypy 2.x 兼容性原缺口已被本机 smoke 关闭（sync 捕 223→filter 0 新错）；“format 只降不升 lint 计数”为机制推断需落地实测确认；pre-commit.ci 精确 OAuth scopes 未抓到一手页（issue#6+写权限需求佐证）；per-rule 预算无大型开源先例（机制可行靠自研 comparator）。
