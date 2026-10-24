# 任务测试结果（第一轮）

模型：`opencode-go/deepseek-v4.1-flash`，reasoning=`max`
日期：2026-10-24

## 任务来源
| 项目 | PR | Base commit | 目标测试 | 初始状态 |
|---|---|---|---|---|
| werkzeug | pallets/werkzeug #3234 discard invalid ETag values | `efa80bff` | `tests/test_http.py` + `tests/test_wrappers.py` | 2 failed |
| pytest | pytest-dev/pytest #15150 junitxml shorten message | `59200df7` | `testing/test_junitxml.py` | 收集失败（缺 `shorten_message`）|

每端使用独立工作副本，`.git` 已重置为单一 base commit，无法 checkout 上游修复。

## 结果

### werkzeug
| client | api_calls | input | output | reasoning | cache_read | prompt_tokens | cache_hit | total | cost | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| opencode | 1 | 35557 | 4414 | 2021 | 383488 | 419045 | 91.51% | 425480 | $0.010345 | 52s |
| pi | 14 | 43109 | 5770 | 1140 | 368512 | 411621 | 89.53% | 418531 | $0.011034 | 69s |
| hermes | 32 | 95446 | 16210 | 10033 | 1548288 | 1643734 | 94.19% | 1669977 | $0.034708* | 567s |

### pytest
| client | api_calls | input | output | reasoning | cache_read | prompt_tokens | cache_hit | total | cost | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| opencode | 1 | 24036 | 2211 | 1266 | 238080 | 262116 | 90.83% | 265593 | $0.006406 | 76s |
| pi | 11 | 26397 | 6044 | 3637 | 234112 | 260509 | 89.87% | 270190 | $0.008288 | 68s |
| hermes | 25 | 91531 | 13139 | 8202 | 927232 | 1018763 | 91.02% | 1040104 | $0.029316* | 168s |

\* Hermes 本地 `actual_cost_usd=0`，为按 opencode-go 单价估算值。

> Hermes 会话还会触发一次 `title_generation` 辅助调用（`mimo-v2.6-flash`，约 250 input / 13 output），
> 属于会话标题生成，不在被测推理链路内，已从主表剔除并单列于 `results/aux-calls.csv`。

## 正确性
六次运行全部通过目标测试（werkzeug 215 passed，pytest 149 passed / 2 skipped），均未修改测试。

## 观察
1. **opencode 的 `api_calls` 恒为 1**：只在 session 汇总层记录一次，不反映真实请求次数；pi/Hermes 为逐次调用累加。该字段不可横向比较。
2. **缓存命中率三端接近**（89.5%–94.2%），Hermes 略高，因其 system prompt 更长且多轮前缀稳定。
3. **总 token Hermes 是 opencode 的 3.9 倍**（werkzeug）和 3.9 倍（pytest），主要来自超长 system prompt 与更多轮次（32 / 25 次调用）。
4. **成本**：按估算口径，Hermes 约为 opencode 的 3.4 倍，pi 约 1.1–1.6 倍。
5. **pi 的 reasoning 与自算成本存在偏差**：pi 导出的 cost 不含 reasoning 单独计价，自算按 output 单价计入 reasoning，故 pytest 项差 $0.0022。
6. **wall time**：opencode/pi 相近（52–76s），Hermes 明显更慢（168–567s），与轮次多、system prompt 长相关。

## 待改进
- `api_calls` 需换成真实请求数（opencode 从 `part`/`message` 表统计 assistant 消息数）。
- 每项只跑 1 次，建议各 3 次取中位数。
- werkzeug 任务较简单（3 文件 45 行），后续可换更复杂的复现任务。
