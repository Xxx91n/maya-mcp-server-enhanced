# 第二轮锐评响应：诚实档先行、ADR 注记惯例、歧义 API 处置与决策入 docs

第二轮外部锐评（audit @ aed9298）经逐条实证复核（8 实锤+1 夸大+1 驳回）后采用分层处置框架：诚实项立即修（CHANGELOG 虚账/README 安装段/ADR-0003 状态注记/helper 括号/死常量/.scratch 出仓）→人工门 0.1.0 发布插队→代码项 T-11 修复轮落 0.1.1；AE 治理=ADR-0003 保 accepted 追加未兑现 status 注记+引擎 dormant 机器可见标注；lookThru 歧义 API 全换 modelPanel 命名参数 API；stub 改类型感知消歧 warn/strict 双档；v1.0.0 DoD 增“issue #7 真机验证全绿”；决策账本+current handoff 迁 docs/，.scratch 整体 gitignore。

Status: accepted (2026-09-18)

## Considered Options

- **先发 0.1.0 锁名后修复**：否决——CHANGELOG:33 虚账会随 tag 封进发布物（PyPI 元数据永久留存，keep-a-changelog 修正窗口必须在发布前用完）。
- **ADR-0003 回改 proposed**：否决——Fowler/Nygard 语义 accepted 记录永不重开，失效仅 superseded（有替代决策）/deprecated（不再适用）两正道；澄清性 status 注记是唯一允许的 accepted 内修改。
- **ADR-0003 另起 supersede**：否决——无替代决策可指（兑现窗口 T-06 是未来归属非已做决策），status 注记更诚实。
- **T-11 兑现 AE 注入（锐评“正路”）**：否决——侵入 T-06 绞杀者模块归置决策面；D-013 native 端 >10K 字符 stale-response quirk 正落 1350 行引擎注入区间，“成本中”被低估；修复轮伦理=止损虚账非提前兑现架构。
- **删 aesthetic_engine.py+57 死测试**：否决——57 测试需逐条甄别（或含内联契约验证）非整文件可删；删除=烧掉 ADR-0003 否决理由的论证原文，T-06 时该理由可能重新成立；T-06 是已记录有治理依据的复用计划，落 dead-vs-deprecate 框架“留存但隔离”格。
- **dormant 标注仅 docstring**：否决——无机器可见锚点=装饰；必须入 AGENTS.md 联动表+ruff 基线说明让休眠税可查证。
- **保留 lookThru 改 camera-first**：否决——仍押注文档未写清的位置序；两序都能活的消歧语义不等于契约，歧义 API 整体退场。
- **现状不动只修 stub**：否决——真机风险原样保留。
- **stub 未知相机名无条件 raise（锐评原案）**：否决——拒绝真机合法输入=假阳性，违 Google Testing Blog 忠实度原则（fake 须与真实行为一致）；改 warn 默认/strict 可选双档+docstring 声明偏离。
- **v1.0.0 协议验证项降级 best-effort**：否决——稀释 5-Production/Stable 语义；真机层是本项目唯一系统性盲区（stub 仅契约层），无真机验证的 Stable=第二次 CHANGELOG:33。
- **native 通道接线实现 retry**：否决——新特性非清理；零引用死常量不构成 Chesterton 栅栏，需求驱动单独立项。
- **.scratch 外科式（残留模式 ignore+全链跟踪）**：否决——报告噪音留公共主干；“决策与结论进 docs（资产），过程与探测留 scratch（噪音）”为更优治理（Fowler ADR 同仓惯例+本仓 docs/adr 先例）。
- **.scratch 全 ignore 仅留账本于 scratch**：否决——账本埋没不可发现且断 current handoff 的 commit 防丢通道。

## Consequences

- **分层框架**（D-037）：诚实档→人工门 0.1.0→代码档 T-11→0.1.1。锐评驳回项入档防再传：“ADR-0011 权重表总分仍 100”指控=引用张冠李戴（该 ADR 无权重表；代码 :3276 归一化正确；README:241 与 README_en:218 均明写归一化）；lookThru“必炸”打折——官方 docs 两序并存按类型消歧、maya-capture 工业库生产用 panel-first、但单参依赖 active view（headless 实锤报错）故 :179 兜底确为哑弹。
- **AE 三件套**（D-038）：CHANGELOG:33 删虚账（[Unreleased] 区直接改免标注，keep-a-changelog 2.0+semantic-release 维护者共识）；ADR-0003 保 accepted+status 注记（未兑现 as of 0.1.0/consolidation deferred to T-06/内联版为现役实现）；修 AE KeyError（compute_lighting_quality_score layers other→unclassified）；dormant 机器可见（AGENTS.md 联动表+ruff 基线说明）；T-06 兑现时自由选“修复注入”或“内联抽取重写”。
- **视觉/API**（D-039）：visual_module.py 三处 lookThru 全换 modelPanel 命名参数 API——主路径 modelPanel(panel,e=True,camera=cam)，恢复路径先 modelPanel(q=True,camera=True) 查询再赋回，单参兜底删除；stub 改类型感知消歧+warn 默认/strict 可选+docstring 声明偏离，顺带过 stub 其他 cmds.* 伪造语义面；issue #7 增静态签名审计/mayapy 签名采集→stub 回填/smoke 覆盖调用形态三项；T-11 内 visual_module 全部 cmds.* 调用（~10 API）人工签名对照。
- **v1.0.0 门**（D-040）：issue #7 清单全绿=v1.0.0 tag 前置（D-032“外部测试”显式化，同向非冲突）；0.1.0 不受影响（alpha 语义）但真机未验状态必须经 #7 显式披露不得暗示已验证。
- **P2 五件**（D-041）：client.py:464 无条件 +b"\n"（commandPort 行提交语义官方明定+2016 源码 splitlines 实证，off-by-one 滞留实锤；空行被 strip/splitlines 消化无副作用；响应侧 \x00 语义已证实正确）+#7 补“无\n命令+500ms读”实证项；删 DEFAULT_MAX_RETRIES/RETRY_DELAY+:346 注释改写实际行为；native _send_receive 补 ConnectionError→MayaUnavailableError 对等映射（单独 commit+typed-error 回归测试，test_client.py 惯例）；decision-ledger.md+current handoff 迁 docs/、.scratch 整体 gitignore+untrack 保本地、账本规范路径改 docs/decision-ledger.md（grill 模板约定同步更新+全部路径引用同步）；maya_scene_module cmds.* 静态审计入 #7。
- **证据强度说明**：lookThru 类型消歧=官方示例两序并存+社区印证的强推断（Maya 闭源无源码行号）；Maya 2022+ commandPort Qt 重写内部未公开（\n 语义以官方文档+2016 源码为准、实证项兜底）；“audit/handoff reports 入仓”无专门权威文献（ADR 治理+gitignore 惯例外推合成）；57 测试或含内联契约验证为可能性推断非实测。
