#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/csrc/hashkernels.c"
OUT_DIR="$ROOT/cbuild"
OBJ="$OUT_DIR/hashkernels.o"
LIB="$OUT_DIR/libhashkernels.a"
DYLIB="$OUT_DIR/libhashkernels.dylib"

mkdir -p "$OUT_DIR"

COMMON_FLAGS=(
  -O3
  -ffast-math
  -funroll-loops
  -fstrict-aliasing
  -flto
  -mcpu=native
  -DNDEBUG
)

cc "${COMMON_FLAGS[@]}" -std=c11 -fPIC -c "$SRC" -o "$OBJ"
ar rcs "$LIB" "$OBJ"
cc -dynamiclib "${COMMON_FLAGS[@]}" "$SRC" -o "$DYLIB"

echo "built: $LIB"
echo "built: $DYLIB"
