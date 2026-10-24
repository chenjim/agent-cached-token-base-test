# Baseline: hi（统一 reasoning=max）

模型：`opencode-go/deepseek-v4.1-flash`，reasoning=max

| client | input | output | reasoning | cache_read | cache_write | prompt_tokens | cache_hit_rate | cost_usd |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| opencode | 3361 | 82 | 105 | 27904 | 0 | 31265 | 89.25% | 0.000677712 |
| pi | 14095 | 22 | 0 | 0 | 0 | 14095 | 0.00% | 0.00212745 |
| hermes | 21876 | 166 | 118 | 0 | 0 | 21876 | 0.00% | 0.00345180 |

说明：
- Hermes 本次 session 还有 1 次辅助调用 `mimo-v2.6-flash`（43 input / 8 output），未计入主表。
- Hermes 成本按 opencode-go 单价估算；opencode/pi 使用 provider 导出 cost。
- pi 本次 reasoning=0 为模型随机未输出思考内容，非配置问题。

## 复核（2026-10-24）
- opencode：导出 cost `0.000677712`，按单价自算 `0.000700062`，差约 3.2%（结算舍入/口径差异），对账以 provider 账单为准。
- pi：导出 cost 与自算完全一致 `0.00212745`。
- Hermes：本地 `actual_cost_usd=0`（cost_status=unknown），表中为 `estimated_cost`。
- 三端均已确认 reasoning=max 生效：opencode `reasoning=105`、Hermes `reasoning_tokens=118`、pi `thinking_level_change=max`（本次模型随机未输出思考，reasoning=0）。
- opencode 本次 cache_hit 89.25% 偏高，疑与同 provider 历史前缀缓存复用有关，横向对比时应以同批次多轮中位数为准。

