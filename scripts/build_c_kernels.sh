#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/csrc/hashkernels.c"
OUT_DIR="$ROOT/cbuild"
OBJ="$OUT_DIR/hashkernels.o"
LIB="$OUT_DIR/libhashkernels.a"
DYLIB="$OUT_DIR/libhashkernels.dylib"

mkdir -p "$OUT_DIR"

cc -O3 -march=native -std=c11 -fPIC -c "$SRC" -o "$OBJ"
ar rcs "$LIB" "$OBJ"
cc -dynamiclib -O3 -march=native "$SRC" -o "$DYLIB"

echo "built: $LIB"
echo "built: $DYLIB"
