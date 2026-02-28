#include "hashkernels.h"
#include <string.h>

#if defined(__aarch64__)
#include <arm_acle.h>

static inline uint32_t rotl32_u32(uint32_t x, unsigned r) {
    return (x << r) | (x >> (32u - r));
}
#endif

static inline uint32_t mix32_u32(uint32_t input, uint32_t seed) {
    uint32_t x = input ^ seed;
    x = x * 1103515245u + 12345u;
    x = x ^ (x * 97u + 13u);
    x = x + (x * 31u);
    return x;
}

int32_t hk_mix32(int32_t input, int32_t seed) {
    return (int32_t)mix32_u32((uint32_t)input, (uint32_t)seed);
}

int32_t hk_mix4(int32_t a, int32_t b, int32_t c, int32_t d, int32_t seed) {
    uint32_t s = (uint32_t)seed;
    uint32_t acc = mix32_u32((uint32_t)a + 17u, s);
    acc ^= mix32_u32((uint32_t)b + 29u, s + 3u);
    acc ^= mix32_u32((uint32_t)c + 43u, s + 7u);
    acc ^= mix32_u32((uint32_t)d + 71u, s + 11u);
    acc = mix32_u32(acc, s + 19u);
    return (int32_t)acc;
}

int32_t hk_stream(int32_t seed, int32_t rounds) {
    uint32_t s = (uint32_t)seed;
    uint32_t acc = s ^ 0x7f4a7c15u;
    for (int32_t i = 0; i < rounds; i++) {
        uint32_t iu = (uint32_t)i;
        uint32_t a = iu + s;
        uint32_t b = iu * 3u + s;
        uint32_t c = iu * 5u + s;
        uint32_t d = iu * 7u + s;
        acc ^= (uint32_t)hk_mix4((int32_t)a, (int32_t)b, (int32_t)c, (int32_t)d, (int32_t)(s + iu));
    }
    return (int32_t)acc;
}

int32_t hk_hash_buf(const uint8_t* ptr_borrowed, size_t len, int32_t seed) {
    if (ptr_borrowed == NULL) {
        return 0;
    }

    uint32_t acc = 2166136261u ^ (uint32_t)seed;
    size_t i = 0;

#if defined(__aarch64__)
    // Full-byte scan with 4 independent CRC lanes to reduce dependency chains.
    uint32_t acc0 = acc ^ 0x9e3779b9u;
    uint32_t acc1 = acc ^ 0x85ebca6bu;
    uint32_t acc2 = acc ^ 0xc2b2ae35u;
    uint32_t acc3 = acc ^ 0x27d4eb2fu;

    for (; i + 32 <= len; i += 32) {
        uint64_t w0, w1, w2, w3;
        memcpy(&w0, ptr_borrowed + i + 0, 8);
        memcpy(&w1, ptr_borrowed + i + 8, 8);
        memcpy(&w2, ptr_borrowed + i + 16, 8);
        memcpy(&w3, ptr_borrowed + i + 24, 8);
        acc0 = __crc32cd(acc0, w0);
        acc1 = __crc32cd(acc1, w1);
        acc2 = __crc32cd(acc2, w2);
        acc3 = __crc32cd(acc3, w3);
    }

    acc ^= acc0;
    acc ^= rotl32_u32(acc1, 7u);
    acc ^= rotl32_u32(acc2, 13u);
    acc ^= rotl32_u32(acc3, 21u);

    for (; i + 8 <= len; i += 8) {
        uint64_t w;
        memcpy(&w, ptr_borrowed + i, 8);
        acc = __crc32cd(acc, w);
    }

    for (; i < len; i++) {
        acc = __crc32cb(acc, ptr_borrowed[i]);
    }
#else
    // Portable fallback: byte-mix scan.
    for (; i + 8 <= len; i += 8) {
        acc ^= ptr_borrowed[i + 0]; acc *= 16777619u;
        acc ^= ptr_borrowed[i + 1]; acc *= 16777619u;
        acc ^= ptr_borrowed[i + 2]; acc *= 16777619u;
        acc ^= ptr_borrowed[i + 3]; acc *= 16777619u;
        acc ^= ptr_borrowed[i + 4]; acc *= 16777619u;
        acc ^= ptr_borrowed[i + 5]; acc *= 16777619u;
        acc ^= ptr_borrowed[i + 6]; acc *= 16777619u;
        acc ^= ptr_borrowed[i + 7]; acc *= 16777619u;
    }

    for (; i < len; i++) {
        acc ^= ptr_borrowed[i];
        acc *= 16777619u;
    }
#endif

    acc ^= (uint32_t)len;
    acc = mix32_u32(acc, (uint32_t)seed + 0x9e3779b9u);
    return (int32_t)acc;
}
