# FozzyLang Unsafe Hash Lab

Competition-style Fzy + C micro-kernel exhibition focused on deterministic benchmarking.

## Build C kernels

```bash
./scripts/build_c_kernels.sh
```

## Fzy checks

```bash
fz check . --json
fz test . --det --strict-verify --record artifacts/fz.test.trace.fozzy --json
fz run . --det --strict-verify --record artifacts/fz.run.trace.fozzy --json
fz headers . --out include/hashlab.h --json
```

## Fozzy deterministic-first flow

```bash
fozzy doctor --deep --scenario tests/hashbench.pass.fozzy.json --runs 5 --seed 42 --json
fozzy test --det --strict tests/hashbench.pass.fozzy.json --json
fozzy run tests/hashbench.pass.fozzy.json --det --record artifacts/hashbench.trace.fozzy --json
fozzy trace verify artifacts/hashbench.trace.fozzy --strict --json
fozzy replay artifacts/hashbench.trace.fozzy --json
fozzy ci artifacts/hashbench.trace.fozzy --json
```

## Host-backed confidence

```bash
fozzy run tests/hashbench.host.pass.fozzy.json --proc-backend host --fs-backend host --http-backend host --json
```
