#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)/.."
BINARY="$ROOT_DIR/Mcmf/mcmf"
REFPY="$ROOT_DIR/Mcmf/mcmf_ref.py"
OUTDIR="$ROOT_DIR/Mcmf/correctness_tests"
mkdir -p "$OUTDIR"

# Test parameters (adjustable)
NUM_TESTS=50
N_MIN=20
N_MAX=200
AVG_DEG=3    # average degree
CAP_MAX=10
COST_MAX=10

echo "Compiling C binary..."
gcc -std=c11 -O2 "$ROOT_DIR/Mcmf/mcmf.c" -o "$BINARY"
echo "Using reference python: $REFPY"
echo "Running $NUM_TESTS random tests (N in [$N_MIN,$N_MAX])..."

FAILED=0
for i in $(seq 1 $NUM_TESTS); do
  # randomize size
  N=$(shuf -i ${N_MIN}-${N_MAX} -n 1)
  M=$(( N * AVG_DEG ))
  INP="$OUTDIR/test_${i}_n${N}_m${M}.in"
  OUT_C="$OUTDIR/test_${i}_n${N}_m${M}.c.out"
  OUT_P="$OUTDIR/test_${i}_n${N}_m${M}.py.out"

  # generate random graph
  python3 - <<PY > "$INP"
import random
N=$N
M=$M
print(N, M)
edges = set()
while len(edges) < M:
    u = random.randrange(0, N)
    v = random.randrange(0, N)
    if u==v: continue
    edges.add((u,v))
for (u,v) in list(edges)[:M]:
    cap = random.randint(1, $CAP_MAX)
    cost = random.randint(0, $COST_MAX)
    print(u, v, cap, cost)
print(0, N-1)
PY

  # run C and python reference
  "$BINARY" < "$INP" > "$OUT_C"
  python3 "$REFPY" < "$INP" > "$OUT_P"

  read -r fc cc < "$OUT_C" || fc=""; cc="${cc:-}"
  read -r fp cp < "$OUT_P" || fp=""; cp="${cp:-}"

  if [ "$fc" != "$fp" ] || [ "$cc" != "$cp" ]; then
    echo "[FAIL] test $i N=$N M=$M -> C:($fc,$cc) REF:($fp,$cp)"
    FAILED=$((FAILED+1))
    # keep failing input for debugging
    cp "$INP" "$OUTDIR/fail_test_${i}_n${N}_m${M}.in"
  else
    echo "[OK]   test $i N=$N M=$M -> ($fc,$cc)"
  fi
done

echo "Done. Failed tests: $FAILED / $NUM_TESTS"
if [ $FAILED -gt 0 ]; then
  echo "Failing cases saved in $OUTDIR (files starting with fail_)"
fi
