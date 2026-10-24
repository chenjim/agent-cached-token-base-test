# Werkzeug 任务：discard invalid ETag values

- 来源 PR：pallets/werkzeug #3234
- Base commit：`efa80bff0ac50824ea4f7d848a10001cc614c893`
- 测试 patch：`tasks/patches/werkzeug-tests.patch`（只改 tests/）
- 目标测试：`tests/test_http.py`、`tests/test_wrappers.py`
- 初始状态：2 failed / 213 passed

## 运行命令
```bash
cd work/<client>-werkzeug
PYTHONPATH=$PWD/src /vol1/1000/Project/agent-cached-token-base-test/.venv/bin/python -m pytest tests/test_http.py tests/test_wrappers.py -q
```

## 验收
- 上述命令全绿
- `tests/` 未被修改
- 记录 `git diff --stat` 的源文件改动

## Prompt
```
Repository: pallets/werkzeug (checked out at the buggy commit).

Bug: invalid ETag values must be discarded instead of being accepted and kept
in the parsed ETag structures.

Run the tests with:
  PYTHONPATH=$PWD/src /vol1/1000/Project/agent-cached-token-base-test/.venv/bin/python -m pytest tests/test_http.py tests/test_wrappers.py -q

Two tests currently fail. Fix the library source under src/werkzeug/ so all
tests in these two files pass.

Do not modify anything under tests/ or pyproject.toml. Stop as soon as the
tests pass. Briefly explain the root cause at the end.
```
