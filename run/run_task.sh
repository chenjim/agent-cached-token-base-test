#!/usr/bin/env bash
# 用法: ./run/run_task.sh <opencode|pi|hermes> <werkzeug|pytest>
set -euo pipefail
source "$(dirname "$0")/common.sh"

CLIENT=${1:?client: opencode|pi|hermes}
PROJECT=${2:?project: werkzeug|pytest}

case "$PROJECT" in
  werkzeug) TEST_CMD="PYTHONPATH=\$PWD/src $ROOT/.venv/bin/python -m pytest tests/test_http.py tests/test_wrappers.py -q" ;;
  pytest)   TEST_CMD="PYTHONPATH=\$PWD/src $ROOT/.venv/bin/python -m pytest testing/test_junitxml.py -q" ;;
  *) echo "unknown project: $PROJECT" >&2; exit 1 ;;
esac

PROMPT=$(awk '/^## Prompt$/{f=1;next} f&&/^```/{n++;next} f&&n==1{print}' \
         "$ROOT/tasks/$PROJECT-task.md")

WORKDIR=$(prepare_workdir "$CLIENT" "$PROJECT")
START=$(date +%s)
echo "client=$CLIENT project=$PROJECT start=$START workdir=$WORKDIR"
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
esac

echo "--- 验收 ---"
EV="$ROOT/results/evidence/$CLIENT-$PROJECT"
mkdir -p "$EV"
eval "$TEST_CMD" 2>&1 | tee "$EV/pytest.txt" | tail -8
git -C "$WORKDIR" diff HEAD > "$EV/diff.patch"
git -C "$WORKDIR" status --porcelain > "$EV/git-status.txt"
echo "--- diff stat ---"
git -C "$WORKDIR" diff HEAD --stat | tail -10
echo "evidence: $EV"
echo "END start=$START end=$(date +%s) client=$CLIENT project=$PROJECT"
