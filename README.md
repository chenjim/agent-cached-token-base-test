# 同一模型，三个 Agent，谁在偷偷烧 token？

我每天在 opencode、Hermes、pi 之间切来切去。三个都跑 `opencode-go/deepseek-v4.1-flash`，
都开着 `reasoning=max`，干的是同一类活：读代码、改 bug、跑测试。

有个问题一直没答案：**同一个模型，换个壳子，token 到底差多少？**

账单上看不出——三端都算在同一个订阅里。缓存命中率更是各家自说自话。
于是我干脆搭了个测试台，用真实的开源 bug 跑三遍。

仓库：[github.com/chenjim/agent-cached-token-base-test](https://github.com/chenjim/agent-cached-token-base-test)

## 先定死变量，再谈结果

这类对比最容易翻车的地方，是"看起来一样其实不一样"。我锁死了这些：

| 维度 | 取值 |
|---|---|
| 模型 | `opencode-go/deepseek-v4.1-flash` |
| 推理档 | `max` |
| 权限 | 自动批准 |
| 工作副本 | 每个客户端独立一份 |
| 验收 | 目标测试全绿，且不许改测试 |

推理档必须统一。第一次跑的时候我给 opencode/pi 用了默认档、Hermes 用了 `low`，
三边 `reasoning` 一个是 0，一个 105，一个 66——这种数据放在一起比，没有意义。

现在统一传法：

```bash
# opencode
opencode run --standalone --auto --model "opencode-go/deepseek-v4.1-flash#max"

# pi
pi --provider opencode-go --model "opencode-go/deepseek-v4.1-flash:max" -p

# Hermes
hermes chat -Q --oneshot --yolo --provider opencode-go \
  --model deepseek-v4.1-flash --reasoning max
```

## 任务：两个真实 bug，不是玩具题

第一版我用的是 `sum()` 少加一的玩具仓库。跑完发现三端都 30 秒解决，
token 差异全被 system prompt 的固定开销吃掉了，测不出东西。

换成从上游 PR 反推：

| 项目 | PR | 初始状态 |
|---|---|---|
| werkzeug | [#3234](https://github.com/pallets/werkzeug/pull/3234) 丢弃非法 ETag | 2 failed |
| pytest | [#15150](https://github.com/pytest-dev/pytest/pull/15150) junitxml 消息截断 | 收集失败（缺函数） |

做法是取 PR 的 **base commit**，只把 PR 里 `tests/` 的改动单独 apply 上去，
让测试先红，然后让 agent 去把源码改绿。

这几步脚本不长，但很关键：

```bash
git clone -q --local --no-hardlinks "$src" "$dst"
git -C "$dst" checkout -q "$commit"
# 抹掉上游历史，否则 agent 会直接 checkout 官方修复
rm -rf "$dst/.git"
git -C "$dst" init -q && git -C "$dst" add -A
git -C "$dst" commit -q -m "bench: base state"

git -C "$dst" apply tasks/patches/$project-tests.patch
git -C "$dst" commit -q -m "bench: apply failing tests"
```

## 踩坑：agent 会抄答案

第一次跑 werkzeug，opencode 用了 53 秒就宣布搞定，diff 跟官方修复一模一样。

因为它在我 clone 的工作副本里看到了 `origin/pr3234` 分支，于是：

```
$ git checkout 5b0dc6d6 -- src/werkzeug/datastructures/etag.py ...
```

这不是模型的错，是我的测试台漏了。把 `.git` 整个重置成单一 commit 之后，
同一道题 opencode 用了 72 秒，改法也和官方不同——这才是我想要的。

顺带一提，三端的修法确实不一样：opencode 和 pi 常改 `sansio/http.py`，
Hermes 会绕去 `datastructures/range.py`。同一个 bug，多种合法解法。

## 数据

三轮，每轮 6 次运行，共 18 次，全部通过目标测试，没有人动过测试文件。

![三轮平均总 token](https://blog-chenjim.oss-cn-shanghai.aliyuncs.com/2026/261024-agent-token-bench-01-tokens.png-blog)

| 项目 | 客户端 | 第 1 轮 | 第 2 轮 | 第 3 轮 | 中位数 | 成本/次（均值） | 命中率（均值） |
|---|---|---:|---:|---:|---:|---:|---:|
| werkzeug | opencode | 425K | 331K | 1049K | **425K** | $0.0129 | 89.5% |
| werkzeug | pi | 419K | 724K | 568K | **568K** | $0.0127 | 90.7% |
| werkzeug | hermes | 1670K | 1796K | 771K | **1670K** | $0.0310 | 93.3% |
| pytest | opencode | 266K | 320K | 502K | **320K** | $0.0098 | 89.7% |
| pytest | pi | 270K | 282K | 390K | **282K** | $0.0095 | 90.5% |
| pytest | hermes | 1040K | 615K | 367K | **615K** | $0.0197 | 91.2% |

均值会被离群值带偏（第三轮 opencode 在 werkzeug 上飙到 1049K），所以结论按**中位数**看。

口径：

```
prompt_tokens = input + cache_read + cache_write
cache_hit_rate = cache_read / prompt_tokens
total_tokens  = prompt_tokens + output + reasoning
```

Hermes 本地不记成本（`actual_cost_usd` 恒为 0），表里是按 opencode-go 单价估算的。
另外它每次会话还会多跑一次 `title_generation`（`mimo-v2.6-flash`，约 250 token 生成标题），
这个不属于推理链路，我已从主表剔除，单独存到 `results/aux-calls.csv`。

## 缓存命中：真的差不多

![缓存命中率](https://blog-chenjim.oss-cn-shanghai.aliyuncs.com/2026/261024-agent-token-bench-02-cache-hit.png-blog)

三轮均值都在 89%–93% 之间，三个客户端的差距**小于各自的波动范围**——
换句话说：缓存命中率不是这三者的差异来源，谁也没比别人省。

Hermes 略高（93.3%），因为它 system prompt 更长、前缀更稳定，
长前缀反而更容易吃到缓存，这点反直觉但合理。

opencode 波动最大（81%–95%），跟会话重建时机有关，还没深挖。

## 成本差距才是重点

![单次成本](https://blog-chenjim.oss-cn-shanghai.aliyuncs.com/2026/261024-agent-token-bench-03-cost.png-blog)

三轮均值看，Hermes 在 werkzeug 上是 opencode 的 2.4 倍、pytest 上 2.0 倍。
原因三个叠加：

1. system prompt 明显更长（规则、记忆、技能清单全塞进去）
2. 轮次更多：pytest 那道题 pi 跑 11–14 次调用、Hermes 跑 11–25 次
3. 每轮都要重新带上完整上下文

有意思的是第三轮 Hermes 突然变便宜了（pytest 只花 $0.0127，比第一轮低 57%）。
它那次探索路径更短，11 次调用就收敛——同一套配置，结果能在 2.5 倍区间里晃。

pi 则意外地稳：总 token 和 opencode 接近，成本还低一截。
它的 `cost` 字段不含 reasoning 单独计价，跨端比较我用的是按单价重算的 `estimated_cost`。

## 但先别急着下结论

![三轮方差](https://blog-chenjim.oss-cn-shanghai.aliyuncs.com/2026/261024-agent-token-bench-04-variance.png-blog)

这是我最想强调的一张图：**同一配置、同一个任务，三轮之间最大差 2.5 倍。**

- Hermes 在 werkzeug 上：1670K → 1796K → 771K
- opencode 在 pytest 上：266K → 320K → 502K
- pi 相对稳，但也有 1.7 倍波动

模型的探索路径是随机的，多走两步、多读两个文件、多跑一次全量测试，token 就上去了。

我最初拿前两轮的数据得出"Hermes 是 opencode 的 3.9 倍"，补了第三轮之后，
这个倍数变成 1.9–3.9 倍不等——**任何单轮结论都不该当定论。**

脚本里留了 `ROUND` 参数，想跑几轮都行：

```bash
ROUND=3 ./run/run_task.sh pi werkzeug
```

## 怎么采集的

三端存储方式完全不同，得分别处理：

```bash
# opencode：必须在对应 work 目录里跑，数据按项目隔离
cd work/pi-werkzeug && opencode session export <session_id>

# pi：直接解析 JSONL
python3 -c "...message.usage..."

# Hermes：SQLite
sqlite3 ~/.hermes/state.db \
  "select * from session_model_usage where session_id='<id>'"
```

`collect/collect.py` 会把三边整理成同一套字段，并补上 `estimated_cost`。

有个坑值得记一下：**opencode 的 `api_calls` 恒为 1**。那是 session 汇总字段，
不是真实请求数。我一开始拿它和 pi 的 14 次、Hermes 的 32 次并排比，结论完全是错的。

## 目前能说的结论

- **缓存命中率不是差异来源**：三端 89%–93%，差距小于波动范围
- **总 token 差异主要来自 context 设计**：按中位数，Hermes 是 opencode 的 1.9–3.9 倍
- **成本排序稳定**：pi ≈ opencode < hermes，两个项目都成立
- **方差比差异更大**：同一配置三轮晃 2.5 倍，单轮数据只能算参考
- **想省钱，先改 context 设计（规则/记忆/工具），不是换客户端**

## 还没做完的

- 三轮还是偏少，5 轮更稳
- werkzeug 那题只有 45 行改动，偏简单，该换更复杂的
- pytest 的测试 patch 里 import 了 `shorten_message`，等于把函数名告诉了模型，
  比 werkzeug 那题多了提示，两题难度不完全对等
- 没测多轮对话场景，只测了单次任务

仓库里所有原始数据都在：`results/evidence/<client>-<project>/` 下有 diff、pytest 输出、
usage JSON 和运行元信息。想复现：

```bash
git clone https://github.com/chenjim/agent-cached-token-base-test.git
cd agent-cached-token-base-test
# 具体命令见 AGENTS.md
```

---

*测试环境：飞牛 NAS（i5-1240P，无 GPU），2026-10-24。模型全走云端，本地只负责调度和跑测试。*
