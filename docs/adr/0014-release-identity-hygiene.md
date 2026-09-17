# 发布身份与卫生策略：三层命名分叉、版本两阶段与授权门

PyPI dist=mcp-for-maya 与 import=maya_mcp_server 合法分叉（PyPA 官方认可 fork 是常见分叉原因）、console script 随 dist 名；版本 0.1.0→4-Beta→1.0.0+Production/Stable 两阶段晋升；外部副作用按可逆性分层授权——issues agent 直建、repo 改名/tag/PyPI 发布/Release 入人工确认门；PyPI 占名只发真实包否决空壳。

Status: accepted (2026-09-18)

## Considered Options

- **PyPI 空包/0.0.1 占位**：否决——官方 Name Retention 政策明定“no functionality or is empty”属 name squatting 可被移除；0.0.1 空包是社区最反感形态（orsinium 抢注数据）；mcp-for-maya 为垂直名被抢概率低，要占就发真实最小包。
- **import 名改 mcp_for_maya**：否决——PyPA 官方：“a distribution package could provide an import package with a different name…fork of an existing library is a common reason”；Pillow/PIL、PyYAML/yaml、bs4 先例；import 名在 MCP 客户端 config 中不可见，改名零收益却拉满与上游 chadrik 的合并冲突面。
- **script 名保留 maya-mcp-server**：否决——uvx 按“命令名=包名”惯性解析（官方文档+uv#7804 用户困惑+uv#21135 维护者立场“两者应一致”）；switchboard-relay 实证 dist/script 不匹配令 README 一行命令失效。
- **直接首发 1.0.0**：否决——semver §5“1.0.0 定义公共 API”=兼容性冻结承诺，MCP 工具面公开使用后必仍将调整；0.y.z 期 minor bump 无违约压力。
- **GitHub Releases 替代 CHANGELOG.md**：否决——Keep a Changelog 官方 FAQ：Releases 是 non-portable changelog，迁移即丢、discoverability 差；惯例两者并存。
- **纯删 README skills 幻影承诺（v1.x 从零立项）**：修正为交付 2 张 experimental 纯流程卡——Skill 失败率数据打击的是“捆绑脚本”品类（Snyk ToxicSkills 36% injection 源于脚本），纯 Markdown 流程卡不在暴露面；SkillsBench 实证 focused ≤3 模块为高分品类；experimental 标注是成熟惯例（spec 自身 allowed-tools 字段、MS Agent Framework）；dcc-mcp-maya 证实 MCP server 附 skills 是既定模式。
- **agent 自主执行 repo 改名/PyPI 发布**：否决——一次性高副作用公开行为（PyPI 元数据 URL 不随 GitHub 重定向、镜像缓存旧名），惯例入人工确认门；agent 备命令清单+受影响文件列表，用户执行或逐条批准。

## Consequences

- **范围边界**（D-028）：T-09=仓库内全量（LICENSE/pyproject/README 双语/AGENTS/版本策略）+GitHub 改名与六 roadmap issues 立即做；PyPI 零发布进 T-09，占名=首个真实发布（可选 0.1.0 或直接 1.0.0）；改名先行使元数据 URL 一次写对新名；改名后检查 Actions 对旧 owner/repo@ref 引用（不重定向），绝不重用旧名建新仓库；DoD 含发布日清单（PyPI 名空闲确认→Trusted Publishers→issue 号回填）。
- **三层命名**（D-029）：pyproject name="mcp-for-maya"；[project.scripts] 双入口 mcp-for-maya+maya-mcp-server 同指 main；src/maya_mcp_server/ 与 import 名不动；README 写明 dist/import 对应关系；blender-mcp 2026-09-16 已用同款结构发 mcp-for-blender 2.0.0（旧名 2.4KB wrapper——我们无需，旧 dist 属上游）。
- **README 形态**（D-030）：结构重排+全量修错——新增“对比 blender-mcp”诚实三档节（我方独有 ICEV/CoS/checkpoint/注册表/视觉闭环 vs 它方独有资产生态/一等对象 CRUD vs 共有）；全部数字以代码为真源；撰写遵循 create-readme skill（GFM+GitHub admonition、克制 emoji、不含 LICENSE/CONTRIBUTING/CHANGELOG 节）；README_en 平行同步；AGENTS.md LOGLEVEL/scripts 幻影同修。
- **LICENSE 与信任叙事**（D-030）：MIT 双行版权 Copyright (c) 2026 Chad Dombrova（上游 notice 法律义务）+ Copyright (c) 2026 Xxx91n；README 信任段“zero telemetry, no phone-home”——代码实测零遥测，较 D-020④“默认关”更强且属实（措辞细化非推翻）。
- **Skills 交付**（D-031）：B′ 触发——skills/icev-workflow + skills/scene-review-playbook 两张纯流程卡；严格 spec frontmatter（name 小写连字符≤64 匹配目录名、description≤1024、compatibility="Tested on Claude Code only; requires mcp-for-maya"）+正文“Experimental. Evaluated on Claude Code only; untested on Codex/Gemini CLI/Cursor. Tracked in issue #N”+每卡≤3 模块<500 行、细则移 references/；四条件缺一退回纯删。
- **Roadmap issues**（D-031）：六张——Poly Haven v1.1（含 AC：asset 类型/缓存/无网降级）、Skills 立项 v1.x（v1.0 前置先建、含跨模型评测计划）、安全与权限模型 v1.x（safe_mode 为子任务）、export_scene+内省 v1.x、asset sources beyond Poly Haven（exploratory）、真机验证 pinned checklist + v1.0 feedback pinned issue。
- **版本与文档骨架**（D-032）：保持 0.1.0+3-Alpha；feature-complete+外部测试升 4-Beta；1.0.0 与 5-Production/Stable 同 commit；版本策略节写明晋升条件（D-021“v1.0”=semver 语义下 API 冻结承诺）；CHANGELOG.md（Keep a Changelog 1.1.0）+CONTRIBUTING.md 最小三节+README Versioning 小节；CODE_OF_CONDUCT 缓。
- **授权分层**（D-032）：agent 自主=文件/分支/issues/PR；人工确认门=repo 改名、push main、tag、Release、PyPI 发布、secret。
- **证据强度说明**：gh CLI 改名风险无单一官方规范页（惯例+社区材料，置信中）；SkillsBench 为学术论文非生态普查；experimental 卡实际用户接受度无直接数据；mcp-for-maya PyPI 空闲状态未实测（发布日清单确认）；授权分层属社区惯例非强制规范。
