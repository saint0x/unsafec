#include "hashkernels.h"

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
