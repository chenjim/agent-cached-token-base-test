#!/usr/bin/env bash
# 公共变量与工作副本准备：每客户端独立副本，避免互相污染
set -euo pipefail

ROOT=/vol1/1000/Project/agent-cached-token-base-test
MODEL_ID=deepseek-v4.1-flash
MODEL=opencode-go/$MODEL_ID
LEVEL=${LEVEL:-max}

# 准备干净工作副本：work/<client>-<project>
prepare_workdir() {
  local client=$1 project=$2
  local src="$ROOT/projects/base/$project"
  local dst="$ROOT/work/$client-$project"
  [ -d "$src" ] || { echo "缺少基线仓库: $src" >&2; exit 1; }
  rm -rf "$dst"
  mkdir -p "$ROOT/work"
  cp -a "$src" "$dst"
  echo "$dst"
}
