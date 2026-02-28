#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

./scripts/build_c_kernels.sh

zsh -lc "source ~/.zshrc && fz check . --json" >/dev/null
zsh -lc "source ~/.zshrc && fz test . --det --strict-verify --record artifacts/fz.test.trace.fozzy --json" >/dev/null
zsh -lc "source ~/.zshrc && fz run . --det --strict-verify --record artifacts/fz.run.trace.fozzy --json" >/dev/null
zsh -lc "source ~/.zshrc && fz build . --release --lib -L ./cbuild -l hashkernels --json" >/dev/null

fozzy doctor --deep --scenario tests/hashbench.pass.fozzy.json --runs 5 --seed 42 --json >/dev/null
fozzy test --det --strict tests/hashbench.pass.fozzy.json --json >/dev/null
fozzy run tests/hashbench.pass.fozzy.json --det --record artifacts/hashbench.trace.fozzy --json >/dev/null
fozzy trace verify artifacts/hashbench.trace.fozzy --strict --json >/dev/null
fozzy replay artifacts/hashbench.trace.fozzy --json >/dev/null
fozzy ci artifacts/hashbench.trace.fozzy --json >/dev/null
fozzy run tests/hashbench.host.pass.fozzy.json --proc-backend host --fs-backend host --http-backend host --json >/dev/null

./.venv-bench/bin/python ./scripts/bench_sota_vs_fzy.py
