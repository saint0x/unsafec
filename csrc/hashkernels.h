#ifndef HASHKERNELS_H
#define HASHKERNELS_H

#include <stddef.h>
#include <stdint.h>

int32_t hk_mix32(int32_t input, int32_t seed);
int32_t hk_mix4(int32_t a, int32_t b, int32_t c, int32_t d, int32_t seed);
int32_t hk_stream(int32_t seed, int32_t rounds);
int32_t hk_hash_buf(const uint8_t* ptr_borrowed, size_t len, int32_t seed);

#endif
