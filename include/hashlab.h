#ifndef FOZZY_FOZZYLANG_UNSAFE_LAB_H
#define FOZZY_FOZZYLANG_UNSAFE_LAB_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef int32_t (*fz_callback_i32_v0)(int32_t arg);
int32_t fz_host_init(void);
int32_t fz_host_shutdown(void);
int32_t fz_host_cleanup(void);
int32_t fz_host_register_callback_i32(int32_t slot, fz_callback_i32_v0 cb);
int32_t fz_host_invoke_callback_i32(int32_t slot, int32_t arg);

typedef uint64_t fz_async_handle_t;

typedef struct HashLane {
    int32_t a;
    int32_t b;
    int32_t c;
    int32_t d;
} HashLane;

typedef struct BenchConfig {
    int32_t seed;
    int32_t rounds;
    int32_t workers;
} BenchConfig;

typedef enum BenchMode {
    BenchMode_COnly = 0,
    BenchMode_FzyOnly = 1,
    BenchMode_Dual = 2,
} BenchMode;

int32_t fz_bench_dual(int32_t seed, int32_t rounds);
int32_t fz_bench_suite(int32_t seed);
int32_t fz_bench_async_async_start(int32_t seed, fz_async_handle_t* handle_out);
int32_t fz_bench_async_async_poll(fz_async_handle_t handle, int32_t* done_out);
int32_t fz_bench_async_async_await(fz_async_handle_t handle, int32_t* result_out);
int32_t fz_bench_async_async_drop(fz_async_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif
