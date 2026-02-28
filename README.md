# unsafe fzy <-> C Performance Lab

This project is an unsafe `fzy` + `C` interop benchmark lab focused on raw hashing throughput.

## Benchmark Highlights (1 MiB)

From the latest full run (`artifacts/bench_sota_vs_fzy.json`):

| implementation | single (GB/s) | parallel (GB/s) |
|---|---:|---:|
| ours_c | 25.170 | 24.282 |
| ours_fzy | 25.067 | 23.747 |
| openssl_sha256 | 2.456 | 2.298 |
| blake3 | 1.819 | 1.692 |
| xxh3_64 | 36.364 | 32.921 |

Industry baseline deltas:

- `ours_c` is `10.25x` faster than `openssl_sha256` (single, 1 MiB)
- `ours_c` is `13.84x` faster than `blake3` (single, 1 MiB)
- `ours_fzy` is `10.21x` faster than `openssl_sha256` (single, 1 MiB)
- `ours_fzy` is `13.78x` faster than `blake3` (single, 1 MiB)

Full benchmark tables: [BENCH.md](./BENCH.md)

## Run Benchmarks

Quick:

```bash
./scripts/bench_sota.sh --quick
```

Full:

```bash
./scripts/bench_sota.sh
```

Artifacts:

- `artifacts/bench_sota_vs_fzy.json`
- `artifacts/bench_sota_vs_fzy.md`

## fzy <-> C Interop Snippets

C ABI surface (`csrc/hashkernels.h`):

```c
int32_t hk_hash_buf(const uint8_t* ptr_borrowed, size_t len, int32_t seed);
```

fzy import of C function (`src/services/kernels.fzy`):

```fzy
ext unsafe c fn hk_hash_buf(ptr_borrowed: *u8, len: usize, seed: i32) -> i32;

pub fn c_hash_buf_kernel(ptr_borrowed: *u8, len: usize, seed: i32) -> i32 {
    unsafe {
        return hk_hash_buf(ptr_borrowed, len, seed);
    }
}
```

fzy export back to C ABI (`src/api/ffi.fzy`):

```fzy
#[ffi_panic(error)]
pubext c fn fz_hash_buf(ptr_borrowed: *u8, len: usize, seed: i32) -> i32 {
    return services.kernels.c_hash_buf_kernel(ptr_borrowed, len, seed);
}
```

Harness call path (`scripts/bench_sota_vs_fzy.py`):

```python
self._fzy.fz_hash_buf.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.c_int32]
self._fzy.fz_hash_buf.restype = ctypes.c_int32
```

## Optimization TLDR

- Hot path is implemented in C with arm64 hardware CRC intrinsics and multi-lane accumulation.
- `fzy` is used as the interop/control surface and export boundary, keeping unsafe isolated at explicit ABI points.
- Benchmark harness pre-allocates buffers per run and avoids per-iteration marshalling to reduce measurement noise.
- C build uses aggressive native flags (`-O3 -flto -mcpu=native -funroll-loops`) for peak kernel throughput.
