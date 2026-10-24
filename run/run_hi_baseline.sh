#!/usr/bin/env bash
# baseline：三端各跑一次 hi，统一 reasoning=max
# 目的：量化客户端固定开销（system prompt / 工具 schema / 记忆注入）
set -euo pipefail
source "$(dirname "$0")/common.sh"

# 空目录即可，不依赖 projects/base
WORKDIR="$ROOT/work/hi-baseline"
rm -rf "$WORKDIR"; mkdir -p "$WORKDIR"
EV="$ROOT/results/evidence/hi-baseline"
mkdir -p "$EV"
cd "$WORKDIR"
START=$(date +%s)
echo "start=$START" > "$EV/meta.txt"

echo "=== opencode ==="
opencode run --standalone --format json --model "$MODEL#$LEVEL" "hi" > "$EV/opencode.json" 2>&1
tail -c 300 "$EV/opencode.json"

echo "=== pi ==="
pi --provider opencode-go --model "$MODEL:$LEVEL" -p \
  --session-dir "$ROOT/results/pi-sessions" "hi"

echo "=== hermes ==="
hermes chat -Q --oneshot --yolo --provider opencode-go --model "$MODEL_ID" \
  --reasoning "$LEVEL" --in "$WORKDIR" -q "hi"

echo "end=$(date +%s)" >> "$EV/meta.txt"
cat "$EV/meta.txt"
