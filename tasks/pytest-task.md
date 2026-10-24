# pytest 任务模板

## 仓库
`projects/base/pytest`

## 待填 issue
- Issue URL：
- Issue 标题：
- Issue 描述：
- Failing test：`testing/...py::test_...`
- Base commit：

## 验收
- `pytest testing/<file>.py -q` 全绿
- 不修改 tests/
- `git diff --stat` 记录修改文件数/行数

## 统一 Prompt 模板
Repository: pytest-dev/pytest.
Issue: <粘贴 issue 标题与描述>.
There is a failing test in testing/<path>.py::test_xxx.
Fix the bug without editing tests. Run the specific test and stop when it passes.
Explain root cause briefly.
