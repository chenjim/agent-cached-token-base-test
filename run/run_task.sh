#!/usr/bin/env bash
# 用法: PROMPT='...' ./run/run_task.sh <opencode|pi|hermes> <werkzeug|pytest>
set -euo pipefail
source "$(dirname "$0")/common.sh"

CLIENT=${1:?client: opencode|pi|hermes}
PROJECT=${2:?project: werkzeug|pytest}
PROMPT=${PROMPT:?set PROMPT}

WORKDIR=$(prepare_workdir "$CLIENT" "$PROJECT")
echo "workdir: $WORKDIR"
cd "$WORKDIR"

case "$CLIENT" in
  opencode)
    opencode run --standalone --auto \
      --model "$MODEL#$LEVEL" --title "bench-$PROJECT" "$PROMPT"
    ;;
  pi)
    pi --provider opencode-go --model "$MODEL:$LEVEL" -p \
      --session-dir "$ROOT/results/pi-sessions" "$PROMPT"
    ;;
  hermes)
    hermes chat -Q --oneshot --yolo --provider opencode-go --model "$MODEL_ID" \
      --reasoning "$LEVEL" --in "$WORKDIR" -q "$PROMPT"
    ;;
  *) echo "unknown client: $CLIENT" >&2; exit 1 ;;
esac

echo "--- diff stat ---"
git -C "$WORKDIR" diff --stat | tail -5 || true
