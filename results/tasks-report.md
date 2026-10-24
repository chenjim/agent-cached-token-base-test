# 任务测试结果（两轮）

模型：`opencode-go/deepseek-v4.1-flash`，reasoning=`max`
日期：2026-10-24

## 任务来源
| 项目 | PR | Base commit | 目标测试 | 初始状态 |
|---|---|---|---|---|
| werkzeug | pallets/werkzeug #3234 discard invalid ETag values | `efa80bff` | `tests/test_http.py` + `tests/test_wrappers.py` | 2 failed |
| pytest | pytest-dev/pytest #15150 junitxml shorten message | `59200df7` | `testing/test_junitxml.py` | 收集失败（缺 `shorten_message`）|

每端使用独立工作副本，`.git` 重置为单一 base commit，无法 checkout 上游修复。
每轮重新从 base 复制，不继承上一轮改动。

## 两轮明细

### 第 1 轮
| 项目 | client | 调用 | input | output | reasoning | cache_read | 总 token | 命中率 | 成本 | 耗时 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| werkzeug | opencode | 1 | 35557 | 4414 | 2021 | 383488 | 425480 | 91.51% | $0.01035 | 52s |
| werkzeug | pi | 14 | 43109 | 5770 | 1140 | 368512 | 418531 | 89.53% | $0.01103 | 69s |
| werkzeug | hermes | 32 | 95446 | 16210 | 10033 | 1548288 | 1669977 | 94.19% | $0.03471* | 567s |
| pytest | opencode | 1 | 24036 | 2211 | 1266 | 238080 | 265593 | 90.83% | $0.00641 | 76s |
| pytest | pi | 11 | 26397 | 6044 | 3637 | 234112 | 270190 | 89.87% | $0.00829 | 68s |
| pytest | hermes | 25 | 91531 | 13139 | 8202 | 927232 | 1040104 | 91.02% | $0.02932* | 168s |

### 第 2 轮
| 项目 | client | 调用 | input | output | reasoning | cache_read | 总 token | 命中率 | 成本 | 耗时 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| werkzeug | opencode | 1 | 60662 | 4301 | 1726 | 264192 | 330881 | 81.33% | $0.01351 | 72s |
| werkzeug | pi | 25 | 42307 | 4429 | 1171 | 675968 | 723875 | 94.11% | $0.01103 | 222s |
| werkzeug | hermes | 34 | 141504 | 16005 | 9448 | 1629440 | 1796397 | 92.01% | $0.04139* | 702s |
| pytest | opencode | 1 | 50997 | 2427 | 3711 | 262699 | 319834 | 83.74% | $0.01212 | 128s |
| pytest | pi | 11 | 34117 | 3414 | 1171 | 243328 | 282030 | 87.70% | $0.00790 | 112s |
| pytest | hermes | 16 | 45978 | 8707 | 5704 | 554752 | 615141 | 92.35% | $0.01721* | 104s |

\* Hermes 本地 `actual_cost_usd=0`，为按 opencode-go 单价估算值。
Hermes 每次会话还触发一次 `title_generation` 辅助调用（`mimo-v2.6-flash`），
已从主表剔除，单列于 `results/aux-calls.csv` / `aux-calls-r2.csv`。

## 两轮均值
| 项目 | client | 总 token 均值 | 成本均值 | 命中率 r1/r2 | 耗时 r1/r2 |
|---|---|---:|---:|---|---|
| werkzeug | opencode | 378,180 | $0.011927 | 91.51% / 81.33% | 52s / 72s |
| werkzeug | pi | 571,203 | $0.011033 | 89.53% / 94.11% | 69s / 222s |
| werkzeug | hermes | 1,733,187 | $0.038047 | 94.19% / 92.01% | 567s / 702s |
| pytest | opencode | 292,714 | $0.009263 | 90.83% / 83.74% | 76s / 128s |
| pytest | pi | 276,110 | $0.008092 | 89.87% / 87.70% | 68s / 112s |
| pytest | hermes | 827,622 | $0.023262 | 91.02% / 92.35% | 168s / 104s |

## 正确性
12 次运行全部通过目标测试（werkzeug 215 passed；pytest 149 passed / 2 skipped），
`tests/` 与 `testing/` 均未被修改，diff 只落在 `src/`。

## 观察
1. **方差很大**：同一客户端同一任务两轮总 token 可差 1–2 倍（pi werkzeug 418K→724K，Hermes pytest 1040K→615K）。
   两轮不足以定论，需要更多轮次取中位数。
2. **缓存命中率**：opencode 波动最大（81%–91%），pi 与 Hermes 较稳定（87%–94%）。
3. **Hermes 总 token 仍是 opencode 的 2–4.6 倍**，差距随任务轮次放大。
4. **成本排序稳定**：pytest 上 pi < opencode < hermes；werkzeug 上 opencode ≈ pi < hermes。
5. **opencode 的 `api_calls` 恒为 1**，是 session 汇总字段，不可横向比较。
6. pi 的 `cost` 与自算存在 0–26% 偏差（reasoning 计价口径不同），横向对比建议用 `estimated_cost`。

## 存档
- 汇总：`results/tasks.csv`（r1）、`results/tasks-r2.csv`、`results/summary-2rounds.csv`
- 原始：`results/evidence/[r2-]<client>-<project>/`（usage.json、diff.patch、pytest.txt、meta.txt）
- pi 会话：`results/pi-sessions/`
