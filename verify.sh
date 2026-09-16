#!/bin/sh
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "=== hn-mcp-auth-status-boundary-lab verification ==="
echo "Running evaluator..."
python3 "$ROOT/evaluator.py"
echo "Running tests..."
python3 -m unittest tests/test_status_boundary.py -v
echo "Deterministic re-run check..."
python3 "$ROOT/evaluator.py"
echo "All local checks passed."
echo ""
echo "For public-clone verification, run from a fresh clone:"
echo "  git clone https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git /tmp/fresh-lab"
echo "  cd /tmp/fresh-lab && python3 evaluator.py && python3 -m unittest tests/test_status_boundary.py -v"
