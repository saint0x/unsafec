# BENCH

## Industry Baseline Highlights (OpenSSL + BLAKE3)

These are the headline results from the latest full benchmark run (`artifacts/bench_sota_vs_fzy.json`) for the 1 MiB workload.

### Single-thread (1 MiB)

| implementation | throughput (GB/s) | speedup vs OpenSSL SHA-256 | speedup vs BLAKE3 |
|---|---:|---:|---:|
| ours_c | 25.170 | 10.25x | 13.84x |
| ours_fzy | 25.067 | 10.21x | 13.78x |
| openssl_sha256 | 2.456 | 1.00x | 1.35x |
| blake3 | 1.819 | 0.74x | 1.00x |

### Parallel (1 MiB)

| implementation | throughput (GB/s) | speedup vs OpenSSL SHA-256 | speedup vs BLAKE3 |
|---|---:|---:|---:|
| ours_c | 24.282 | 10.56x | 14.35x |
| ours_fzy | 23.747 | 10.33x | 14.04x |
| openssl_sha256 | 2.298 | 1.00x | 1.36x |
| blake3 | 1.692 | 0.74x | 1.00x |

## Full Benchmark Output

The complete benchmark output is included below from `artifacts/bench_sota_vs_fzy.md`.

# SOTA Hash Benchmark vs fzy

- suite: `sota-hash-vs-fzy`
- host: `macOS-15.3.1-arm64-arm-64bit-Mach-O`
- cpu_count: `11`
- seed: `424242`
- crosscheck ours_c vs ours_fzy: `True`

## Availability

| algorithm | available | required | note |
|---|---:|---:|---|
| ours_c | true | true | available |
| ours_fzy | true | true | available |
| openssl_sha256 | true | true | python hashlib backend |
| xxh3_64 | true | false | available |
| blake3 | true | false | available |
| highwayhash | false | false | python highwayhash module not found |

## Results (single + parallel, all sizes)

| algorithm | mode | size | throughput mean (GB/s) | p95 (GB/s) | latency p50 (ns/hash) | latency p99 (ns/hash) |
|---|---|---:|---:|---:|---:|---:|
| ours_c | single | 64 | 0.105 | 0.108 | 565.95 | 573.90 |
| ours_c | parallel | 64 | 0.105 | 0.109 | 560.16 | 613.26 |
| ours_c | single | 256 | 0.406 | 0.413 | 585.78 | 600.08 |
| ours_c | parallel | 256 | 0.398 | 0.406 | 595.28 | 619.83 |
| ours_c | single | 1024 | 1.552 | 1.579 | 612.36 | 629.18 |
| ours_c | parallel | 1024 | 1.410 | 1.596 | 625.49 | 1373.93 |
| ours_c | single | 4096 | 5.135 | 5.287 | 742.42 | 764.81 |
| ours_c | parallel | 4096 | 5.520 | 5.627 | 690.33 | 717.14 |
| ours_c | single | 16384 | 12.933 | 13.151 | 1168.29 | 1237.71 |
| ours_c | parallel | 16384 | 13.599 | 14.016 | 1117.13 | 1173.23 |
| ours_c | single | 65536 | 20.309 | 20.480 | 3001.81 | 3070.31 |
| ours_c | parallel | 65536 | 20.506 | 21.371 | 2949.16 | 3127.12 |
| ours_c | single | 1048576 | 25.170 | 25.347 | 38688.19 | 39277.50 |
| ours_c | parallel | 1048576 | 24.282 | 25.647 | 39894.41 | 43385.41 |
| ours_fzy | single | 64 | 0.097 | 0.097 | 614.48 | 616.64 |
| ours_fzy | parallel | 64 | 0.093 | 0.098 | 647.09 | 689.20 |
| ours_fzy | single | 256 | 0.379 | 0.390 | 627.84 | 671.60 |
| ours_fzy | parallel | 256 | 0.344 | 0.364 | 690.97 | 750.61 |
| ours_fzy | single | 1024 | 1.437 | 1.450 | 661.89 | 675.21 |
| ours_fzy | parallel | 1024 | 1.403 | 1.441 | 679.73 | 710.96 |
| ours_fzy | single | 4096 | 4.853 | 4.909 | 784.67 | 799.67 |
| ours_fzy | parallel | 4096 | 4.537 | 4.746 | 841.53 | 876.37 |
| ours_fzy | single | 16384 | 12.327 | 12.505 | 1233.39 | 1286.03 |
| ours_fzy | parallel | 16384 | 12.715 | 13.236 | 1204.20 | 1239.73 |
| ours_fzy | single | 65536 | 19.938 | 20.075 | 3050.03 | 3166.84 |
| ours_fzy | parallel | 65536 | 19.738 | 20.613 | 3108.66 | 3258.52 |
| ours_fzy | single | 1048576 | 25.067 | 25.271 | 38983.11 | 39274.23 |
| ours_fzy | parallel | 1048576 | 23.747 | 25.211 | 40723.42 | 45828.72 |
| openssl_sha256 | single | 64 | 0.100 | 0.103 | 588.39 | 620.60 |
| openssl_sha256 | parallel | 64 | 0.093 | 0.095 | 643.93 | 671.29 |
| openssl_sha256 | single | 256 | 0.348 | 0.355 | 686.57 | 697.41 |
| openssl_sha256 | parallel | 256 | 0.331 | 0.343 | 725.23 | 743.11 |
| openssl_sha256 | single | 1024 | 0.974 | 0.983 | 979.09 | 993.46 |
| openssl_sha256 | parallel | 1024 | 0.956 | 0.998 | 1002.79 | 1051.23 |
| openssl_sha256 | single | 4096 | 1.784 | 1.792 | 2138.34 | 2151.23 |
| openssl_sha256 | parallel | 4096 | 1.662 | 1.748 | 2290.22 | 2496.25 |
| openssl_sha256 | single | 16384 | 2.256 | 2.264 | 6758.65 | 6806.40 |
| openssl_sha256 | parallel | 16384 | 2.064 | 2.219 | 7454.09 | 8141.64 |
| openssl_sha256 | single | 65536 | 2.415 | 2.429 | 25247.26 | 25458.43 |
| openssl_sha256 | parallel | 65536 | 2.234 | 2.423 | 27719.17 | 30721.53 |
| openssl_sha256 | single | 1048576 | 2.456 | 2.494 | 394678.17 | 427188.85 |
| openssl_sha256 | parallel | 1048576 | 2.298 | 2.474 | 430741.05 | 453718.42 |
| xxh3_64 | single | 64 | 0.064 | 0.065 | 924.05 | 942.79 |
| xxh3_64 | parallel | 64 | 0.063 | 0.064 | 951.55 | 984.23 |
| xxh3_64 | single | 256 | 0.251 | 0.255 | 940.27 | 976.40 |
| xxh3_64 | parallel | 256 | 0.245 | 0.267 | 947.48 | 1169.12 |
| xxh3_64 | single | 1024 | 0.963 | 0.988 | 993.95 | 1036.40 |
| xxh3_64 | parallel | 1024 | 0.980 | 1.005 | 972.80 | 1028.02 |
| xxh3_64 | single | 4096 | 3.612 | 3.736 | 1054.10 | 1102.02 |
| xxh3_64 | parallel | 4096 | 3.570 | 3.666 | 1066.59 | 1098.39 |
| xxh3_64 | single | 16384 | 11.450 | 11.670 | 1319.49 | 1400.22 |
| xxh3_64 | parallel | 16384 | 11.228 | 11.614 | 1346.02 | 1451.67 |
| xxh3_64 | single | 65536 | 24.008 | 24.308 | 2534.04 | 2591.40 |
| xxh3_64 | parallel | 65536 | 23.022 | 24.290 | 2650.79 | 2820.86 |
| xxh3_64 | single | 1048576 | 36.364 | 36.627 | 26907.58 | 27033.55 |
| xxh3_64 | parallel | 1048576 | 32.921 | 35.487 | 30143.91 | 30653.65 |
| blake3 | single | 64 | 0.088 | 0.089 | 674.80 | 679.68 |
| blake3 | parallel | 64 | 0.077 | 0.082 | 776.28 | 821.73 |
| blake3 | single | 256 | 0.278 | 0.280 | 859.89 | 864.93 |
| blake3 | parallel | 256 | 0.260 | 0.265 | 915.91 | 957.12 |
| blake3 | single | 1024 | 0.597 | 0.608 | 1586.18 | 1660.14 |
| blake3 | parallel | 1024 | 0.589 | 0.605 | 1616.95 | 1671.00 |
| blake3 | single | 4096 | 1.329 | 1.375 | 2884.88 | 2978.07 |
| blake3 | parallel | 4096 | 1.327 | 1.391 | 2833.32 | 3220.96 |
| blake3 | single | 16384 | 1.655 | 1.693 | 9138.66 | 9596.99 |
| blake3 | parallel | 16384 | 1.232 | 1.277 | 12370.94 | 12963.17 |
| blake3 | single | 65536 | 1.808 | 1.814 | 33762.50 | 33904.63 |
| blake3 | parallel | 65536 | 1.704 | 1.821 | 35547.71 | 39101.75 |
| blake3 | single | 1048576 | 1.819 | 1.829 | 537141.67 | 540018.92 |
| blake3 | parallel | 1048576 | 1.692 | 1.801 | 573050.41 | 639946.49 |
