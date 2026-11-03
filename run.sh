#!/usr/bin/env bash
# NegationScope college demo — Python 3.10+, no external Python packages required.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if ! command -v python3 >/dev/null 2>&1; then
  echo 'Python 3.10+ is required. Install Python 3 and retry.' >&2
  exit 1
fi
PYTHON="${PYTHON:-python3}"
"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit('Python 3.10+ is required')
PY
export PYTHONPATH="$ROOT:$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
MODE="${1:-dashboard}"
case "$MODE" in
  dashboard|--dashboard)
    "$PYTHON" -c 'import numpy' 2>/dev/null || { echo 'NumPy required: python3 -m pip install numpy'; exit 1; }
    "$PYTHON" model/toy_vlm.py
    mkdir -p runs/college-demo
    echo 'Preparing deterministic synthetic dataset and fixture reports...'
    "$PYTHON" scripts/demo.py --out runs/college-demo
    echo "Starting dashboard at http://127.0.0.1:${PORT:-8765}"
    exec "$PYTHON" dashboard/server.py --port "${PORT:-8765}" ;;
  model|--model)
    "$PYTHON" model/toy_vlm.py ;;
  test|--test)
    "$PYTHON" -c 'import numpy' 2>/dev/null || { echo 'NumPy required: python3 -m pip install numpy'; exit 1; }
    "$PYTHON" -m unittest discover -s tests -p 'test_toy_vlm.py' -v
    "$PYTHON" -m unittest discover -s tests -p 'test_college_demo.py' -v
    "$PYTHON" -m negationscope.cli build --seeds data/scene_seeds.jsonl --out runs/college-demo/prompts.jsonl --seed 42
    "$PYTHON" -m negationscope.cli validate --dataset runs/college-demo/prompts.jsonl
    echo 'PASS: tests and real dataset build/validation completed.' ;;
  generate|--generate)
    mkdir -p runs/college-demo
    exec "$PYTHON" scripts/demo.py --out runs/college-demo ;;
  *) echo 'Usage: ./run.sh [dashboard|model|test|generate]' >&2; exit 2 ;;
esac
