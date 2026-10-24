# pytest 任务：junitxml 缩短 message 属性

- 来源 PR：pytest-dev/pytest #15150
- Base commit：`59200df778adf8079df6125d60662908ac0a0646`
- 测试 patch：`tasks/patches/pytest-tests.patch`（只改 testing/）
- 目标测试：`testing/test_junitxml.py`
- 初始状态：收集失败（`_pytest.junitxml` 无 `shorten_message`）

## 运行命令
```bash
cd work/<client>-pytest
PYTHONPATH=$PWD/src /vol1/1000/Project/agent-cached-token-base-test/.venv/bin/python -m pytest testing/test_junitxml.py -q
```

## 验收
- 上述命令全绿
- `testing/` 未被修改
- 记录 `git diff --stat` 的源文件改动

## Prompt
```
Repository: pytest-dev/pytest (checked out at the buggy commit).

Bug: with --junitxml, the message attribute of <failure> and <error> holds the
whole exception text. Long messages (e.g. a big diff at -vv) produce
attributes of tens of thousands of characters, which some XML parsers reject.
The attribute should be shortened while the element text keeps the full report.

Run the tests with:
  PYTHONPATH=$PWD/src /vol1/1000/Project/agent-cached-token-base-test/.venv/bin/python -m pytest testing/test_junitxml.py -q

Right now the test module fails to import because `_pytest.junitxml.shorten_message`
does not exist. Implement it and fix the library source under src/_pytest/ so
that all tests in that file pass.

Do not modify anything under testing/ or pyproject.toml. Stop as soon as the
tests pass. Briefly explain the root cause at the end.
```
