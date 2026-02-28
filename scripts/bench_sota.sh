#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

QUICK=""
if [[ "${1:-}" == "--quick" ]]; then
  QUICK="--quick"
fi

./scripts/build_c_kernels.sh
zsh -lc "source ~/.zshrc && fz build . --release --lib -L ./cbuild -l hashkernels --json" >/dev/null
./.venv-bench/bin/python ./scripts/bench_sota_vs_fzy.py $QUICK
