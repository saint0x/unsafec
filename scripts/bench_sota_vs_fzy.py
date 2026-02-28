#!/usr/bin/python3
from __future__ import annotations

import argparse
import concurrent.futures
import ctypes
import ctypes.util
import importlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"

DEFAULT_SIZES = [64, 256, 1024, 4096, 16384, 65536, 1048576]
DEFAULT_MODES = ["single", "parallel"]


def percentile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    pos = (len(s) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    t = pos - lo
    return s[lo] * (1.0 - t) + s[hi] * t


@dataclass
class RuntimePaths:
    c_lib: Path
    fzy_lib: Path


class Runtime:
    def __init__(self, paths: RuntimePaths) -> None:
        self.paths = paths
        self._c = None
        self._fzy = None
        self._fzy_init_done = False
        self._xxh = None
        self._blake3 = None
        self._highway = None

    def c_lib(self):
        if self._c is None:
            self._c = ctypes.CDLL(str(self.paths.c_lib))
            self._c.hk_hash_buf.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.c_int32]
            self._c.hk_hash_buf.restype = ctypes.c_int32
        return self._c

    def fzy_lib(self):
        if self._fzy is None:
            self._fzy = ctypes.CDLL(str(self.paths.fzy_lib))
            self._fzy.fz_hash_buf.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.c_int32]
            self._fzy.fz_hash_buf.restype = ctypes.c_int32
            self._fzy.fz_host_init.argtypes = []
            self._fzy.fz_host_init.restype = ctypes.c_int32
            self._fzy.fz_host_shutdown.argtypes = []
            self._fzy.fz_host_shutdown.restype = ctypes.c_int32
            self._fzy.fz_host_cleanup.argtypes = []
            self._fzy.fz_host_cleanup.restype = ctypes.c_int32
        return self._fzy

    def init_fzy_host(self) -> None:
        if self._fzy_init_done:
            return
        lib = self.fzy_lib()
        rc = int(lib.fz_host_init())
        if rc != 0:
            raise RuntimeError(f"fz_host_init failed rc={rc}")
        self._fzy_init_done = True

    def close_fzy_host(self) -> None:
        if not self._fzy_init_done or self._fzy is None:
            return
        _ = int(self._fzy.fz_host_shutdown())
        _ = int(self._fzy.fz_host_cleanup())
        self._fzy_init_done = False

    def xxh3(self):
        if self._xxh is not None:
            return self._xxh
        lib_name = ctypes.util.find_library("xxhash")
        if not lib_name:
            return None
        try:
            lib = ctypes.CDLL(lib_name)
        except OSError:
            return None
        try:
            func = lib.XXH3_64bits
        except AttributeError:
            return None
        func.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        func.restype = ctypes.c_uint64
        self._xxh = func
        return self._xxh

    def blake3(self):
        if self._blake3 is not None:
            return self._blake3
        try:
            mod = importlib.import_module("blake3")
        except Exception:
            return None
        self._blake3 = mod
        return self._blake3

    def highway(self):
        if self._highway is not None:
            return self._highway
        try:
            mod = importlib.import_module("highwayhash")
        except Exception:
            return None
        self._highway = mod
        return self._highway


@dataclass
class Algo:
    name: str
    required: bool
    available: bool
    reason: str


def discover_algorithms(rt: Runtime, strict_baselines: bool) -> List[Algo]:
    algos = [
        Algo("ours_c", True, True, "available"),
        Algo("ours_fzy", True, True, "available"),
        Algo("openssl_sha256", True, True, "python hashlib backend"),
    ]

    xxh = rt.xxh3()
    algos.append(Algo("xxh3_64", strict_baselines, xxh is not None, "libxxhash not found" if xxh is None else "available"))

    b3 = rt.blake3()
    algos.append(Algo("blake3", strict_baselines, b3 is not None, "python blake3 module not found" if b3 is None else "available"))

    hh = rt.highway()
    algos.append(Algo("highwayhash", False, hh is not None, "python highwayhash module not found" if hh is None else "available"))
    return algos


def hash_once_prepared(
    rt: Runtime,
    algo: str,
    buf: bytes,
    ptr_u8: ctypes.POINTER(ctypes.c_uint8),
    len_buf: int,
    seed: int,
) -> int:
    if algo == "ours_c":
        return int(rt.c_lib().hk_hash_buf(ptr_u8, len_buf, seed)) & 0xFFFFFFFF
    if algo == "ours_fzy":
        rt.init_fzy_host()
        return int(rt.fzy_lib().fz_hash_buf(ptr_u8, len_buf, seed)) & 0xFFFFFFFF
    if algo == "openssl_sha256":
        import hashlib

        d = hashlib.sha256(buf).digest()
        return int.from_bytes(d[:4], "little")
    if algo == "xxh3_64":
        fn = rt.xxh3()
        if fn is None:
            raise RuntimeError("xxh3 unavailable")
        out = int(fn(ctypes.cast(ptr_u8, ctypes.c_void_p), len_buf))
        return out & 0xFFFFFFFF
    if algo == "blake3":
        mod = rt.blake3()
        if mod is None:
            raise RuntimeError("blake3 unavailable")
        d = mod.blake3(buf).digest(length=4)
        return int.from_bytes(d, "little")
    if algo == "highwayhash":
        mod = rt.highway()
        if mod is None:
            raise RuntimeError("highwayhash unavailable")
        key = bytes([seed & 0xFF]) * 32
        out = mod.hash64(key, buf)
        return int(out) & 0xFFFFFFFF
    raise RuntimeError(f"unknown algo={algo}")


def run_iterations(rt: Runtime, algo: str, buf: bytes, iterations: int, seed: int) -> Tuple[int, int]:
    arr = (ctypes.c_uint8 * len(buf)).from_buffer_copy(buf)
    ptr_u8 = ctypes.cast(arr, ctypes.POINTER(ctypes.c_uint8))
    len_buf = len(buf)

    checksum = 0
    start = time.perf_counter_ns()
    for i in range(iterations):
        checksum ^= hash_once_prepared(rt, algo, buf, ptr_u8, len_buf, seed + i)
    elapsed = time.perf_counter_ns() - start
    return elapsed, checksum


def _worker(args: Tuple[str, bytes, int, int, str, str]) -> Tuple[int, int]:
    algo, buf, iterations, seed, c_path, fzy_path = args
    rt = Runtime(RuntimePaths(Path(c_path), Path(fzy_path)))
    try:
        return run_iterations(rt, algo, buf, iterations, seed)
    finally:
        rt.close_fzy_host()


def calibrate_iterations(rt: Runtime, algo: str, buf: bytes, seed: int, target_ms: float) -> int:
    probe = 128
    elapsed, _ = run_iterations(rt, algo, buf, probe, seed)
    per_iter = max(1.0, elapsed / float(probe))
    target_ns = target_ms * 1_000_000.0
    iters = int(target_ns / per_iter)
    return max(128, min(8_000_000, iters))


def bench_case(
    rt: Runtime,
    algo: str,
    buf: bytes,
    seed: int,
    warmups: int,
    measured_runs: int,
    target_ms: float,
    mode: str,
    workers: int,
) -> Dict[str, object]:
    iterations = calibrate_iterations(rt, algo, buf, seed, target_ms)
    per_run: List[Dict[str, float]] = []

    def run_one(run_seed: int) -> Tuple[int, int]:
        if mode == "single":
            return run_iterations(rt, algo, buf, iterations, run_seed)
        if mode == "parallel":
            chunk = max(1, iterations // workers)
            parts = [chunk] * workers
            parts[-1] += iterations - (chunk * workers)
            args = [
                (algo, buf, n, run_seed + idx * 7919, str(rt.paths.c_lib), str(rt.paths.fzy_lib))
                for idx, n in enumerate(parts)
            ]
            wall_start = time.perf_counter_ns()
            checksum = 0
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
                for elapsed_ns, csum in ex.map(_worker, args):
                    checksum ^= csum
            wall_elapsed = time.perf_counter_ns() - wall_start
            return wall_elapsed, checksum
        raise RuntimeError(f"unknown mode={mode}")

    for i in range(warmups):
        run_one(seed + i * 101)

    for i in range(measured_runs):
        elapsed_ns, checksum = run_one(seed + 10_000 + i * 101)
        total_bytes = float(len(buf) * iterations)
        gbps = (total_bytes / elapsed_ns) if elapsed_ns > 0 else 0.0
        gbps *= 1e9 / (1024.0 ** 3)
        ns_per_hash = elapsed_ns / float(iterations)
        per_run.append({
            "elapsed_ns": float(elapsed_ns),
            "checksum": float(checksum),
            "gbps": gbps,
            "ns_per_hash": ns_per_hash,
            "iterations": float(iterations),
        })

    latencies = [r["ns_per_hash"] for r in per_run]
    throughputs = [r["gbps"] for r in per_run]

    return {
        "mode": mode,
        "workers": workers if mode == "parallel" else 1,
        "size_bytes": len(buf),
        "iterations_per_run": iterations,
        "runs": measured_runs,
        "metrics": {
            "throughput_gbps": {
                "mean": statistics.fmean(throughputs),
                "p50": percentile(throughputs, 0.50),
                "p95": percentile(throughputs, 0.95),
                "p99": percentile(throughputs, 0.99),
            },
            "latency_ns_per_hash": {
                "mean": statistics.fmean(latencies),
                "p50": percentile(latencies, 0.50),
                "p95": percentile(latencies, 0.95),
                "p99": percentile(latencies, 0.99),
            },
        },
        "checksum_xor": int(sum(r["checksum"] for r in per_run)) & 0xFFFFFFFF,
    }


def run_cmd(cmd: List[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed rc={proc.returncode}: {' '.join(cmd)}")


def run_fz(cmd_args: List[str], cwd: Path) -> None:
    quoted = " ".join(cmd_args)
    proc = subprocess.run(
        ["zsh", "-lc", f"source ~/.zshrc && fz {quoted}"],
        cwd=str(cwd),
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"fz command failed rc={proc.returncode}: fz {quoted}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark our fzy hash path against SOTA baselines")
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--target-ms", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=max(2, (os.cpu_count() or 4) // 2))
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--strict-baselines", action="store_true")
    parser.add_argument("--out-json", default="artifacts/bench_sota_vs_fzy.json")
    parser.add_argument("--out-md", default="artifacts/bench_sota_vs_fzy.md")
    args = parser.parse_args()

    if args.quick:
        args.warmups = 1
        args.runs = 4
        args.target_ms = 60.0

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    run_cmd(["./scripts/build_c_kernels.sh"], ROOT)
    run_fz(["build", ".", "--release", "--lib", "-L", "./cbuild", "-l", "hashkernels", "--json"], ROOT)

    rt = Runtime(
        RuntimePaths(
            c_lib=ROOT / "cbuild" / "libhashkernels.dylib",
            fzy_lib=ROOT / ".fz" / "build" / "libmain.dylib",
        )
    )

    algos = discover_algorithms(rt, args.strict_baselines)
    unavailable_required = [a for a in algos if a.required and not a.available]
    if unavailable_required:
        print("missing required baselines:", file=sys.stderr)
        for a in unavailable_required:
            print(f"- {a.name}: {a.reason}", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)
    sizes = DEFAULT_SIZES if not args.quick else [64, 1024, 16384, 1048576]
    buffers = {n: rng.randbytes(n) for n in sizes}

    results: List[Dict[str, object]] = []
    errors: List[str] = []

    try:
        probe = buffers[sizes[1 if len(sizes) > 1 else 0]]
        probe_arr = (ctypes.c_uint8 * len(probe)).from_buffer_copy(probe)
        probe_ptr = ctypes.cast(probe_arr, ctypes.POINTER(ctypes.c_uint8))
        c_ref = hash_once_prepared(rt, "ours_c", probe, probe_ptr, len(probe), args.seed)
        fzy_ref = hash_once_prepared(rt, "ours_fzy", probe, probe_ptr, len(probe), args.seed)
        crosscheck_ok = c_ref == fzy_ref

        for algo in algos:
            if not algo.available:
                results.append({
                    "algo": algo.name,
                    "status": "skipped",
                    "reason": algo.reason,
                })
                continue

            algo_cases = []
            for size in sizes:
                buf = buffers[size]
                for mode in DEFAULT_MODES:
                    try:
                        case = bench_case(
                            rt=rt,
                            algo=algo.name,
                            buf=buf,
                            seed=args.seed,
                            warmups=args.warmups,
                            measured_runs=args.runs,
                            target_ms=args.target_ms,
                            mode=mode,
                            workers=args.workers,
                        )
                        algo_cases.append(case)
                    except Exception as exc:  # pragma: no cover
                        errors.append(f"algo={algo.name} size={size} mode={mode} error={exc}")

            results.append({
                "algo": algo.name,
                "status": "ok" if algo_cases else "error",
                "cases": algo_cases,
            })

        payload = {
            "suite": "sota-hash-vs-fzy",
            "generated_at_unix": int(time.time()),
            "host": {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": sys.version.split()[0],
                "cpu_count": os.cpu_count(),
            },
            "config": {
                "sizes": sizes,
                "modes": DEFAULT_MODES,
                "warmups": args.warmups,
                "runs": args.runs,
                "target_ms": args.target_ms,
                "workers": args.workers,
                "seed": args.seed,
                "strict_baselines": args.strict_baselines,
            },
            "availability": [a.__dict__ for a in algos],
            "crosscheck": {
                "ours_c_vs_ours_fzy_equal": crosscheck_ok,
                "ours_c_buffer_probe": c_ref,
                "ours_fzy_buffer_probe": fzy_ref,
            },
            "results": results,
            "errors": errors,
        }

        out_json = ROOT / args.out_json
        out_md = ROOT / args.out_md
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_md.parent.mkdir(parents=True, exist_ok=True)

        out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        lines = [
            "# SOTA Hash Benchmark vs fzy",
            "",
            f"- suite: `{payload['suite']}`",
            f"- host: `{payload['host']['platform']}`",
            f"- cpu_count: `{payload['host']['cpu_count']}`",
            f"- seed: `{args.seed}`",
            f"- crosscheck ours_c vs ours_fzy: `{crosscheck_ok}`",
            "",
            "## Availability",
            "",
            "| algorithm | available | required | note |",
            "|---|---:|---:|---|",
        ]
        for a in algos:
            lines.append(f"| {a.name} | {str(a.available).lower()} | {str(a.required).lower()} | {a.reason} |")

        lines.extend([
            "",
            "## Results (single + parallel, all sizes)",
            "",
            "| algorithm | mode | size | throughput mean (GB/s) | p95 (GB/s) | latency p50 (ns/hash) | latency p99 (ns/hash) |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])

        for row in results:
            if row.get("status") != "ok":
                continue
            for case in row.get("cases", []):
                m = case["metrics"]
                lines.append(
                    "| {algo} | {mode} | {size} | {tm:.3f} | {tp95:.3f} | {lp50:.2f} | {lp99:.2f} |".format(
                        algo=row["algo"],
                        mode=case["mode"],
                        size=case["size_bytes"],
                        tm=m["throughput_gbps"]["mean"],
                        tp95=m["throughput_gbps"]["p95"],
                        lp50=m["latency_ns_per_hash"]["p50"],
                        lp99=m["latency_ns_per_hash"]["p99"],
                    )
                )

        if errors:
            lines.extend(["", "## Errors", ""])
            lines.extend([f"- {e}" for e in errors])

        out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"wrote {out_json}")
        print(f"wrote {out_md}")

    finally:
        rt.close_fzy_host()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
