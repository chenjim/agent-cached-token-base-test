# AGENTS.md

本仓库是 **LLM 编码客户端 token / 缓存命中率基准**。给 coding agent 的操作手册。
面向人的介绍与测试结论见 [README.md](README.md)。

## 目的
在**同一模型、同一 reasoning 档、同一任务**下对比 opencode / Hermes / pi 的
token 消耗、缓存命中率、成本与耗时。

## 目录结构
```
projects/base/{werkzeug,pytest}   干净基线仓库（gitignore，需自行 clone）
tasks/<project>-task.md           任务定义：PR、base commit、目标测试、Prompt
tasks/patches/<project>-tests.patch  仅含 tests 的 patch，让测试先失败
run/common.sh                     模型/档位变量、BASE_COMMIT 映射、prepare_workdir
run/run_task.sh                   单次任务运行（client × project）
run/run_hi_baseline.sh            hi 基准
collect/collect.py                usage 采集 + 成本估算
results/tasks.csv                 r1 汇总
results/tasks-r2.csv              r2 汇总
results/summary-2rounds.csv       两轮均值
results/aux-calls*.csv            Hermes title_generation 辅助调用（不计入主表）
results/evidence/[rN-]<client>-<project>/  usage.json / diff.patch / pytest.txt / meta.txt
results/pi-sessions/              pi 原始会话 JSONL
docs/figures/                     博文配图（matplotlib 生成）
.venv/                            统一测试环境（gitignore）
```

## 环境准备
```bash
git clone https://github.com/pallets/werkzeug projects/base/werkzeug
git clone https://github.com/pytest-dev/pytest   projects/base/pytest

python3 -m venv .venv
.venv/bin/pip install argcomplete "attrs>=23.1" "coverage>=7.5" "hypothesis>=6.75" \
  mock "numpy>=1.26" "pexpect>=4.9" pyyaml requests setuptools xmlschema \
  "iniconfig>=2" "packaging>=24" "pluggy>=1.5,<2" "pygments>=2.15" \
  cffi cryptography ephemeral-port-reserve pytest-timeout watchdog markupsafe matplotlib
```
测试不使用 `pip install -e .`，而是 `PYTHONPATH=$PWD/src`，因为三端各自持有独立副本。

## 运行
```bash
# hi 基准
./run/run_hi_baseline.sh

# 单次任务（第 N 轮用 ROUND=N，避免覆盖上一轮）
ROUND=2 ./run/run_task.sh opencode werkzeug
ROUND=2 ./run/run_task.sh pi pytest
ROUND=2 ./run/run_task.sh hermes werkzeug

# 改推理档
LEVEL=max ./run/run_task.sh pi pytest
```

## 关键不变量
1. **模型与档位必须三端一致**：`opencode-go/deepseek-v4.1-flash`，默认 `LEVEL=max`。
   - opencode 用 `--model opencode-go/deepseek-v4.1-flash#max`
   - pi 用 `--model opencode-go/deepseek-v4.1-flash:max`
   - Hermes 用 `--model deepseek-v4.1-flash --reasoning max`
2. **每客户端独立工作副本**：`work/[rN-]<client>-<project>`，每次从 base 重建。
3. **必须切断上游历史**：`prepare_workdir` 会 `rm -rf .git && git init`。
   否则 agent 能 `git checkout <PR branch> -- src/` 直接抄官方修复（已实际发生过）。
4. **tests 只来自 patch**：agent 不得修改 `tests/`、`testing/`、`pyproject.toml`。
   验证方式 `git diff HEAD --stat -- tests/` 应为空。
5. **验收必须先失败**：新增任务时确认初始状态是 failing，否则结果无意义。

## 采集口径
```
prompt_tokens = input + cache_read + cache_write
cache_hit_rate = cache_read / prompt_tokens
total_tokens  = prompt_tokens + output + reasoning
```
- opencode：`opencode session export <id>` 取 `info.tokens` / `info.cost`
  （`session list` 需在对应 work 目录里跑，数据按项目隔离）
- pi：解析 `results/pi-sessions/*.jsonl` 的 `message.usage`，逐次累加
- Hermes：`sqlite3 ~/.hermes/state.db` 查 `session_model_usage`，按 `cwd` 关联 `sessions`
- 成本：opencode/pi 用 provider 导出值；Hermes `actual_cost_usd=0`，统一用
  `~/.pi/agent/models-store.json` 单价估算（reasoning 按 output 单价）

## 坑
- **opencode 的 `api_calls` 恒为 1**，是 session 汇总字段，不能横向比较。
- **Hermes 会额外跑一次 `title_generation`**（`mimo-v2.6-flash`），
  `task` 字段可区分，必须从主表剔除，否则污染对比。
- **`reasoning` 计数口径不一致**，且 DeepSeek 即使指定档位也可能不输出思考内容；
  主指标不要依赖该字段。
- **方差很大**：同一配置两轮总 token 可差 1–2 倍，单轮不可下结论。
- **opencode 导出 cost 与按单价自算差约 3%**（结算舍入），对账以账单为准。
- pi 的 `cost` 不含 reasoning 单独计价，跨端比较用 `estimated_cost`。
- pytest 测试需要 `src/_pytest/_version.py`，由 `prepare_workdir` 生成（代替 setuptools-scm）。

## 新增任务
1. 找 merged PR：有明确 bug、改 2–4 个源文件、测试可在 5 分钟内跑完。
2. 取 PR 的 `baseRefOid` 作为 base commit，写入 `run/common.sh` 的 `BASE_COMMIT`。
3. `git diff <base> <pr> -- tests/` 生成 `tasks/patches/<project>-tests.patch`。
4. 在 `tasks/<project>-task.md` 写元信息与 Prompt（Prompt 从 `## Prompt` 下的代码块提取）。
5. 手动验证：测试初始失败、`PYTHONPATH=$PWD/src .venv/bin/python -m pytest ...` 可运行。

## 提交约定
- 只改工作区，不自动 push。
- 结果文件与代码分开提交；commit message 不写 AI 署名。
- 密钥、token 不入库。

## 复现配图
```bash
.venv/bin/python docs/figures/gen_figures.py
```
