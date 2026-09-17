# 安全姿态：统一管线 + 诚实威胁模型；AST safe_mode 仅路线图 opt-in

所有 18 个工具入口收口到统一校验+限流+审计+pattern 扫描管线（随 JSON 序列化传参修复同次重构完成）。威胁模型文档按 8 项清单写：显式威胁模型 / README 风险警示框 / 边界声明（regex 黑名单等不是防线，禁用 sandbox、secure 字样）/ 防线清单 / 端口与网络暴露说明 / 危险工具 MCP annotations（readOnlyHint、destructiveHint）/ SECURITY.md 漏洞报告渠道 / 审计日志 schema 与回放方式。AST 白名单 safe_mode 记入路线图 P2 做 opt-in（若做照 zorak1103 模板：默认关、响应带 mode 字段、明写 safety net not a security boundary），首发不承诺。

Refined by D-017（userSetup.py 写入语义 A′）与 D-018（管线执行细则），2026-09-17。

Status: accepted (2026-09-16; refined 2026-09-17)

## Considered Options

- 只修转义正确性：否决——13 个场景工具绕过 security.py 会被第一次安全审计点名（blender-mcp #201/#207/#261 先例）。
- AST 白名单当防线：证据否决——语言级 jail 可平凡绕过（TakoVM wontfix、mcp-use 对抗 fuzzing、RestrictedPython 近期 GHSA），只能当幻觉减速网。
- userSetup.py 整文件覆写+force 逃生（现状+B）：否决——PlatformIO #5473（覆写用户 extensions.json 定级数据丢失 bug）、CVE-2025-53773（注入驱使 Copilot 改 settings.json 开 YOLO→RCE，与本威胁模型同构）、conda 4.8 bashrc 污染；可执行启动文件的整文件覆写能力是注入后最高价值武器。
- userSetup.py 两步 nonce 确认（C）：否决——nonce 是流程级控制，被注入 agent 拿到后可自动回传，无法把用户意图带进协议（Quarkslab：防线必须在工具层；Pillar Security：工具级防滥用）。
- 审计只标准化 logger 格式：否决——logger 轮转/级别过滤会丢审计事件，与应用日志混排破坏逐行取证（ToolHive 分流 AUDIT 级别先例）。
- 限流单桶全局：否决——收紧则误饿读循环（ICEV 一轮≈4 调用），放宽则不可逆写操作无差别放纵；分桶是两侧各自正确的前提。
- pattern 扫描命中即 deny（traditional mode）：否决——OWASP CRS 已弃用（误杀→用户压力关 WAF→安全全失）；成熟形态=检测与拦截解耦（anomaly scoring）。

## Consequences

- 威胁模型口径：受信方 = MCP client/agent；风险 = 被注入指令让 agent 把服务器能力用于用户未意图的目的（confused-deputy 通用形态）。
- 叙事上“安全”只能指：正确性、审计、回滚、误操作减速；不得暗示能关住恶意 client。
- **userSetup.py 写入语义（D-017，A′）**：标记块 `# >>> mcp-for-maya >>>` 幂等 upsert——文件不存在直接建；存在无块且可解析→返回拟插入块内容、待 `confirm=True` 二次调用才写（摩擦点，非 nonce 握手）；存在有块→原位替换；不可解析/异常→拒绝+fallback，不提供任何整文件覆写参数。写入前 `.bak.<timestamp>` 并在返回值报告备份路径；块内容 try/except 自守+幂等注册+不依赖 UI 创建时序（userSetup.py 早于 UI 执行，conda 4.8 教训）；uninstall 对称摘块、文件仅剩块时询问是否删文件；fallback 文案“没做说成没做”：否定式状态句+归因句+两条互斥行动路径，手动块与工具写入逐字节相同。
- **审计日志（D-018）**：独立 JSONL 文件落 platformdirs 用户目录 + 保留 logger 双写；schema = event_id(UUID)/timestamp(ISO8601 UTC)/session_id/tool_name/input_summary(allowlist 脱敏摘要 ≤200 字符，非纯哈希，不记凭据)/outcome(success|error|rejected——rejected 必记，探测攻击第一信号)/duration_ms/warnings(rule_id+命中片段)；文件 0600 权限+独立轮转（不与应用日志混）；审计写失败不阻断工具执行；jq 按 session/tool 回放。
- **限流（D-018）**：读写分桶 token bucket——变更类 ~20 次/60s、读取类 ~100 次/60s、per-session；超限返回显式错误让 agent 停手（静默丢弃诱发 LLM 重试循环）；现有 "Token bucket" 注释名不符实（实为滑动窗口）随真 bucket 实装修正。
- **pattern 扫描（D-018）**：非 code 参数默认 warn-only 记审计（rule_id+命中片段）；block 仅保留零误杀精确规则（filename 参数的 `\.\./` 穿越、code 参数的 `os.system|subprocess|eval(`）；配 rule_id×tool×param 排除调优表，防误杀逼人关管线。
- **annotations（D-018）**：18 工具四 hint 全标（OpenAI Apps SDK 三 hint 必填已为过审硬要求）——execute_code/write_module/maya_setup_guide(install)=destructive:true；读类=readOnly:true+idempotent:true；additive 写文件类=destructive:false；scene_rollback=destructive:false（恢复性质，标 true 误伤确认 UX）+idempotent:false；全 openWorld:false。hints 是协作信号非 contract，服务端管线照旧。
- **同任务顺带清算**（D-014b 面）：security.py 三处诚信度（"Token bucket" 注释、函数内 import re、Windows 路径 regex 半截漏文件名）；helper "controlled namespace" 注释自欺（紧跟全量 __builtins__）；connection_guide 虚假"已生成"文案/硬编码示例路径/_get_platform 去重 utils。
