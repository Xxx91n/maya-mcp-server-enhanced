# 对标 blender-mcp 的定位策略与 v1.0 发布范围/排序

对标策略=能力分层+差异化深化而非工具数量对齐；v1.0 发布面=工程纪律对齐+视觉闭环+发布卫生+最小质量门；任务序=T-05→T-08→T-09(+T-11 并入)→T-10a→发布 v1.0→T-10b→T-12(v1.1)→T-06→T-07；telemetry 默认关；Codex Skills 幻影承诺删除并立项 v1.x。

Status: accepted (2026-09-17)

## Considered Options

- **全能力对齐（B）**：否决——fork 型面面俱到项目死于耦合漂移（emisar google-researcher-mcp 复盘）；MCP 无锁定效应，工具数量战赢不了（Copilot 40→13、Block Linear 30+→2、Stripe curated+泛化 execute 优于全 API 镜像、Anthropic code-execution 官方定调 98.7% token 降幅）。用户保留“以后逐项再议”为长期方向。
- **仅工程纪律对标（C）**：否决——视觉闭环缺口是对标最大短板兼传播演示点（blender-mcp 星数大半来自开箱即炫），不补则“有了眼睛”的自家叙事无实物。
- **任务序 B（内部债先清）**：否决——违背 RERO/MVP 共识（Raymond 原文、zerobrew 一手复盘、HN 133731 正反分歧收敛于“用户可见质量要丝滑、内部整洁度与首发无关”）；发布清单三件套=README 一屏/LICENSE/可试 demo，不含内部重构。
- **任务序 A 原版（T-10 完整版在发布后）**：修正——发布后改动无护栏；拆分为 T-10a（发布前最小门：GH Actions 跑 pytest+ruff）+T-10b（发布后完整门：pre-commit+mypy ratchet，T-06/T-07 动工前置）。Fowler“自测试代码是 CI 必要前置”；Azure Strangler Fig 要求 OE:11 安全部署实践——无 CI 的绞杀拆分=无护栏大爆炸。
- **telemetry 默认开启（跟随 blender-mcp）**：否决——rtk #1154 被社区要求 opt-out→opt-in 翻转（PR 已落地）；Blender 官方扩展政策倾向禁 telemetry；能执行任意代码的 DCC 工具默认外联是信任负资产。折中=默认关+首跑一次性明示+DO_NOT_TRACK/env+CI 自动禁用（TanStack/Prisma/Homebrew 范式），README 当信任卖点。
- **Codex Skills v1.0 做真交付（B）**：否决——未经跨模型/harness 评测的 skills 是实证负资产（HUST+Microsoft：68.8% 功能失败归因相关 skill、IRF/RRO 模式；Carey/MongoDB：66% 退化实测、评测成本高）；对“工作流纪律”卖点项目是自毁招牌。
- **skills 随 PyPI 包自动落盘**：否决——无先例无标准，skills 靠文件系统发现。

## Consequences

- **能力矩阵三档**：v1.0=工程纪律对齐（LICENSE/CI/uvx/版本）+视觉闭环+护城河保持；v1.x=Sketchfab/Poly Pizza/export_scene/API 内省/skills；不做=AI 生成模型+一等对象 CRUD（execute_code 已覆盖）。矩阵是 README 对比叙事（D-003c）的落地载体。
- **视觉闭环=传播级一等公民**，非纯工程项；对 T-05 仅软依赖——base64+尺寸限幅可在现有传输先行（blender-mcp 截图即在未分帧 socket 上运行，issue #189 修法也是 base64 直回），分帧红利后收；分帧不进 T-08 DoD。
- **Poly Haven（T-12）移出首发列 v1.1 首弹**（修订 D-020①）：资产库是留存增强项非首发钩子；活口=T-05+T-08 后若确属薄层（<2天）可挤首发，但不得以推迟发布为代价。
- **safe_mode 叙事位让位给默认开启的事务安全**（checkpoint+rollback+ICEV vs 对方 opt-in AST）：差异化打击点=“它的安全是开关，我们的安全是事务”；AST safe_mode 维持 D-008 路线图 P2 opt-in 挂账。
- **telemetry**：默认关+首跑一次性明示+DO_NOT_TRACK/env 关闭+CI 自动禁用；README 明示“不偷偷上传”。
- **Codex Skills**：v1.0 删 README 幻影承诺，话术=“Skills (planned v1.x): ICEV workflow card, scene_review playbook — see roadmap issue #N”+开 issue；B′ 活口=T-09 若确认内容已以文档形态存在，可交付 2 张纯流程卡（ICEV 工作流卡+scene_review playbook）标“experimental, tested on Claude Code only”，含具体默认值的高 IRF 风险内容（如命名约定卡）不做；否则纯 C。
- **竞品清单**：dcc-mcp-maya（55★/535commits/活跃，29 skill 包+Codex 插件市场分发+progressive skills 打法=Maya 侧直接竞品）；Blender 官方 MCP+Claude connector、Autodesk APS 入局=赛道拥挤化信号，差异化护城河窗口期有限。
- **T-10 拆分**：T-10a=GH Actions(pytest+ruff) 半天量级随发布前完成；T-10b=pre-commit+mypy ratchet+覆盖率门，T-06/T-07 动工前必须就位。
- **T-11 并入 T-09**（文档级版本声明）。
- 调研证据强度说明：RERO/zerobrew 为泛 OSS 证据非 MCP 特有；Copilot/Block/Stripe 数字为 dev.to 二手转述；blender-mcp issue #201 仅搜索摘要级；“skills 提升 DCC agent 纪律”无垂类实证（行业空白）。
