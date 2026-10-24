# LLM 客户端 Token / 缓存命中率基准

对比 **opencode / Hermes / pi** 在**同一模型、同一 reasoning 档、同一任务**下的
token 消耗、缓存命中率、成本与耗时。

## 统一变量
- 模型：`opencode-go/deepseek-v4.1-flash`
- reasoning：`max`（`LEVEL` 环境变量可改）
- 工作副本：每个客户端独立一份，运行前从 `projects/base/` 复制，互不污染
- 权限：自动批准

## 目录
```
projects/base/{werkzeug,pytest}   干净基线仓库（.gitignore 排除，需自行 clone）
work/<client>-<project>           运行时副本，每次重建
tasks/*-task.md                   任务定义（issue + failing test）
run/common.sh                     公共变量与 prepare_workdir
run/run_hi_baseline.sh            hi 基准
run/run_task.sh                   任务测试
collect/collect.py                三端 usage 采集
baseline/                         基准说明与结果
results/                          采集结果（CSV / pi session）
```

## 首次准备
```bash
git clone https://github.com/pallets/werkzeug projects/base/werkzeug
git clone https://github.com/pytest-dev/pytest   projects/base/pytest
```

## 运行
```bash
./run/run_hi_baseline.sh

PROMPT='...' ./run/run_task.sh opencode werkzeug
PROMPT='...' ./run/run_task.sh pi werkzeug
PROMPT='...' ./run/run_task.sh hermes werkzeug
```

## 采集
```bash
python3 collect/collect.py --client all \
  --project work/opencode-werkzeug \
  --since <运行起始 epoch 秒>
```

`collect.py` 统一追加 `estimated_cost`（按 `~/.pi/agent/models-store.json` 单价），
便于跨客户端横向比较。

## 指标
- `prompt_tokens = input + cache_read + cache_write`
- `cache_hit_rate = cache_read / prompt_tokens`
- `total_tokens = prompt_tokens + output + reasoning`
- 成本口径：opencode/pi 用 provider 导出 `cost`；Hermes 本地无成本，用 `estimated_cost`

## 已知偏差（报告时必须说明）
1. 三端 system prompt / 工具 schema / 记忆注入不同，输入 token 基线天然不同；这部分用 `hi` 基准单独量化。
2. 缓存命中受 provider prefix cache 策略影响，首轮多为冷启动，建议每项跑 3 次取中位数。
3. `reasoning` 计数口径不一致，且 DeepSeek 模型即使指定档位也可能随机不输出思考内容。
4. opencode 导出 `cost` 与按单价自算存在约 3% 差异（结算舍入/口径），对账以 provider 账单为准。
5. Hermes 会话会附带一次 `mimo-v2.6-flash` 辅助调用，不计入主表但需备注。
