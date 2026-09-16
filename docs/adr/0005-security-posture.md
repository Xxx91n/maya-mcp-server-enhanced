# 安全姿态：统一管线 + 诚实威胁模型；AST safe_mode 仅路线图 opt-in

所有 18 个工具入口收口到统一校验+限流+审计+pattern 扫描管线（随 JSON 序列化传参修复同次重构完成）。威胁模型文档按 8 项清单写：显式威胁模型 / README 风险警示框 / 边界声明（regex 黑名单等不是防线，禁用 sandbox、secure 字样）/ 防线清单 / 端口与网络暴露说明 / 危险工具 MCP annotations（readOnlyHint、destructiveHint）/ SECURITY.md 漏洞报告渠道 / 审计日志 schema 与回放方式。AST 白名单 safe_mode 记入路线图 P2 做 opt-in（若做照 zorak1103 模板：默认关、响应带 mode 字段、明写 safety net not a security boundary），首发不承诺。

Status: accepted (2026-09-16)

## Considered Options
- 只修转义正确性：否决——13 个场景工具绕过 security.py 会被第一次安全审计点名（blender-mcp #201/#207/#261 先例）。
- AST 白名单当防线：证据否决——语言级 jail 可平凡绕过（TakoVM wontfix、mcp-use 对抗 fuzzing、RestrictedPython 近期 GHSA），只能当幻觉减速网。

## Consequences
- 威胁模型口径：受信方 = MCP client/agent；风险 = 被注入指令让 agent 把服务器能力用于用户未意图的目的（confused-deputy 通用形态）。
- 叙事上“安全”只能指：正确性、审计、回滚、误操作减速；不得暗示能关住恶意 client。
