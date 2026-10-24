#!/usr/bin/env bash
# 公共变量与工作副本准备：每客户端独立副本，避免互相污染
set -euo pipefail

ROOT=/vol1/1000/Project/agent-cached-token-base-test
MODEL_ID=deepseek-v4.1-flash
MODEL=opencode-go/$MODEL_ID
LEVEL=${LEVEL:-max}

# 任务定义：project -> base commit
declare -A BASE_COMMIT=(
  [werkzeug]=efa80bff0ac50824ea4f7d848a10001cc614c893
  [pytest]=59200df778adf8079df6125d60662908ac0a0646
)

# 准备干净工作副本：work/<name>-<project>
# 1) 从 base 仓库本地克隆（保留 .git，便于 git diff）
# 2) 检出任务 base commit
# 3) 应用 tests-only patch（让测试先失败）
prepare_workdir() {
  local name=$1 project=$2
  local src="$ROOT/projects/base/$project"
  local dst="$ROOT/work/$name-$project"
  local commit="${BASE_COMMIT[$project]:-}"
  local patch="$ROOT/tasks/patches/$project-tests.patch"

  [ -d "$src" ] || { echo "缺少基线仓库: $src" >&2; exit 1; }
  rm -rf "$dst"
  mkdir -p "$ROOT/work"

  git clone -q --local --no-hardlinks "$src" "$dst"
  if [ -n "$commit" ]; then
    git -C "$dst" checkout -q "$commit"
  fi
  # 抹掉上游历史与 PR 引用，防止 agent 直接 checkout 官方修复
  rm -rf "$dst/.git"
  git -C "$dst" init -q
  git -C "$dst" add -A
  git -C "$dst" -c user.name=bench -c user.email=bench@local commit -q -m "bench: base state"
  # setuptools-scm 构建产物：测试需要 _pytest._version
  local vfile="$dst/src/_pytest/_version.py"
  if [ -d "$dst/src/_pytest" ] && [ ! -f "$vfile" ]; then
    cat > "$vfile" <<'VER'
# bench: 代替 setuptools-scm 生成
version = "9.9.9.dev0"
__version__ = version
version_tuple = (9, 9, 9, "dev0")
VER
  fi

  if [ -f "$patch" ]; then
    git -C "$dst" apply "$patch" || { echo "tests patch 应用失败: $patch" >&2; exit 1; }
    git -C "$dst" add -A
    git -C "$dst" -c user.name=bench -c user.email=bench@local commit -q -m "bench: apply failing tests"
  fi
  echo "$dst"
}
