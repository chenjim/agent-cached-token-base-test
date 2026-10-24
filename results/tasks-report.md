# 任务测试结果（三轮）

模型：`opencode-go/deepseek-v4.1-flash`，reasoning=`max`
日期：2026-10-24

## 任务来源
| 项目 | PR | Base commit | 目标测试 | 初始状态 |
|---|---|---|---|---|
| werkzeug | pallets/werkzeug #3234 discard invalid ETag values | `efa80bff` | `tests/test_http.py` + `tests/test_wrappers.py` | 2 failed |
| pytest | pytest-dev/pytest #15150 junitxml shorten message | `59200df7` | `testing/test_junitxml.py` | 收集失败（缺 `shorten_message`）|

每端独立工作副本，`.git` 重置为单一 base commit，每轮重新从 base 复制。

## 第 1 轮
| 项目 | client | 调用 | input | output | reasoning | cache_read | 总 token | 命中率 | 成本 | 耗时 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| werkzeug | opencode | 1 | 35557 | 4414 | 2021 | 383488 | 425480 | 91.51% | $0.01035 | 52s |
| werkzeug | pi | 14 | 43109 | 5770 | 1140 | 368512 | 418531 | 89.53% | $0.01103 | 69s |
| werkzeug | hermes | 32 | 95446 | 16210 | 10033 | 1548288 | 1669977 | 94.19% | $0.03471* | 567s |
| pytest | opencode | 1 | 24036 | 2211 | 1266 | 238080 | 265593 | 90.83% | $0.00641 | 76s |
| pytest | pi | 11 | 26397 | 6044 | 3637 | 234112 | 270190 | 89.87% | $0.00829 | 68s |
| pytest | hermes | 25 | 91531 | 13139 | 8202 | 927232 | 1040104 | 91.02% | $0.02932* | 168s |

## 第 2 轮
| 项目 | client | 调用 | input | output | reasoning | cache_read | 总 token | 命中率 | 成本 | 耗时 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| werkzeug | opencode | 1 | 60662 | 4301 | 1726 | 264192 | 330881 | 81.33% | $0.01351 | 72s |
| werkzeug | pi | 25 | 42307 | 4429 | 1171 | 675968 | 723875 | 94.11% | $0.01103 | 222s |
| werkzeug | hermes | 34 | 141504 | 16005 | 9448 | 1629440 | 1796397 | 92.01% | $0.04139* | 702s |
| pytest | opencode | 1 | 50997 | 2427 | 3711 | 262699 | 319834 | 83.74% | $0.01212 | 128s |
| pytest | pi | 11 | 34117 | 3414 | 1171 | 243328 | 282030 | 87.70% | $0.00790 | 112s |
| pytest | hermes | 16 | 45978 | 8707 | 5704 | 554752 | 615141 | 92.35% | $0.01721* | 104s |

## 第 3 轮
| 项目 | client | 调用 | input | output | reasoning | cache_read | 总 token | 命中率 | 成本 | 耗时 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| werkzeug | opencode | 1 | 46719 | 4113 | 4069 | 993664 | 1048565 | 95.51% | $0.01490 | 97s |
| werkzeug | pi | 21 | 64198 | 4380 | 1490 | 497920 | 567988 | 88.58% | $0.01465 | 156s |
| werkzeug | hermes | 20 | 48815 | 8592 | 3760 | 709376 | 770543 | 93.56% | $0.01686* | 535s |
| pytest | opencode | 1 | 26930 | 3260 | 5805 | 466048 | 502043 | 94.54% | $0.01088 | 80s |
| pytest | pi | 14 | 23743 | 5524 | 2251 | 358144 | 389662 | 93.78% | $0.00930 | 142s |
| pytest | hermes | 11 | 35230 | 6555 | 4163 | 320640 | 366588 | 90.10% | $0.01268* | 75s |

## 三轮汇总
| 项目 | client | 总 token 中位数 | 总 token 均值 | 成本均值 | 命中率均值 | 耗时均值 |
|---|---|---:|---:|---:|---:|---:|
| werkzeug | opencode | 425,480 | 601,642 | $0.012917 | 89.45% | 74s |
| werkzeug | pi | 567,988 | 570,131 | $0.012699 | 90.74% | 149s |
| werkzeug | hermes | 1,669,977 | 1,412,306 | $0.030985 | 93.25% | 601s |
| pytest | opencode | 319,834 | 362,490 | $0.009801 | 89.70% | 95s |
| pytest | pi | 282,030 | 313,961 | $0.009457 | 90.45% | 107s |
| pytest | hermes | 615,141 | 673,944 | $0.019734 | 91.16% | 116s |

\* Hermes 本地 `actual_cost_usd=0`，为按 opencode-go 单价估算值。
Hermes 每轮额外一次 `title_generation`（`mimo-v2.6-flash`），已剔除，见 `aux-calls*.csv`。

## 正确性
18 次运行全部通过目标测试（werkzeug 215 passed；pytest 149 passed / 2 skipped），
`tests/` 与 `testing/` 均未被修改，diff 只落在 `src/`。

## 观察
1. **方差主导**：三轮之间最大差 2.5 倍（hermes werkzeug 1796K vs 771K；opencode werkzeug 331K vs 1049K）。
   结论必须看中位数或更多轮次。
2. **缓存命中率三端同档**（89%–93%），差距小于波动范围，不是差异来源。
3. **按中位数，Hermes 是 opencode 的 1.9 倍（pytest）到 3.9 倍（werkzeug）**。
4. **成本排序**：pi ≈ opencode < hermes，两个项目都成立。
5. **opencode `api_calls` 恒为 1**，是 session 汇总字段，不可横向比较。
6. pi 的 `cost` 不含 reasoning 单独计价，跨端比较用 `estimated_cost`。
7. 第三轮 Hermes 明显收敛（pytest 11 次调用、367K），说明其上限高但不是每次都高。

## 存档
- 汇总：`results/tasks.csv`(r1)、`results/tasks-r2.csv`、`results/tasks-r3.csv`、`results/summary-3rounds.csv`
- 原始：`results/evidence/[rN-]<client>-<project>/`（usage.json、diff.patch、pytest.txt、meta.txt）
- pi 会话：`results/pi-sessions/`
