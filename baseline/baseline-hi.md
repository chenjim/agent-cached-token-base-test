# Baseline：hi 空任务固定开销

模型 `opencode-go/deepseek-v4.1-flash`，reasoning=max。
输入只有 "hi"，用于量化客户端自身的固定开销（system prompt、工具 schema、记忆/技能注入）。

| client | input | output | reasoning | cache_read | prompt_tokens | 命中率 | 总 token | 成本 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| opencode | 6148 | 63 | 38 | 10240 | 16388 | 62.48% | 16489 | $0.001014 |
| pi | 14534 | 157 | 130 | 1280 | 15814 | 8.09% | 16101 | $0.002356 |
| hermes | 21532 | 380 | 373 | 2816 | 24348 | 11.57% | 25101 | $0.003690* |

\* Hermes 本地 `actual_cost_usd=0`，为按 opencode-go 单价估算。
Hermes 另有一次 `mimo-v2.6-flash` 的 `title_generation`（235/8），未计入。

## 怎么读
- `input` 差 3.5 倍（6148 / 14534 / 21532）：这就是三端 system prompt 的体量差。
  Hermes 注入规则、记忆、技能清单；pi 带完整工具定义；opencode 最精简。
- 缓存命中在这里不代表稳态：hi 是新会话，`cache_read` 来自 provider 侧的前缀复用，
  opencode 命中率高是因为其 system prompt 与历史会话前缀高度重合。
- 空任务成本只占实际任务的一小部分（opencode $0.0010 vs 任务 $0.0129），
  所以三端差异主要来自**多轮对话的上下文累积**，不是开场固定开销。

## 复现
```bash
./run/run_hi_baseline.sh
```
原始数据：`results/evidence/hi-baseline/`（usage-{opencode,pi,hermes}.json、meta.txt）
