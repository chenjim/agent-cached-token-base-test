#!/usr/bin/env bash
# baseline：三端各跑一次 hi，统一 reasoning=max
set -euo pipefail
source "$(dirname "$0")/common.sh"

WORKDIR=$(prepare_workdir opencode hi-baseline)
cd "$WORKDIR"

echo "=== opencode ==="
opencode run --standalone --auto --model "$MODEL#$LEVEL" --title hi-baseline "hi"
echo "=== pi ==="
pi --provider opencode-go --model "$MODEL:$LEVEL" -p \
  --session-dir "$ROOT/results/pi-sessions" "hi"
echo "=== hermes ==="
hermes chat -Q --oneshot --yolo --provider opencode-go --model "$MODEL_ID" \
  --reasoning "$LEVEL" --in "$WORKDIR" -q "hi"
