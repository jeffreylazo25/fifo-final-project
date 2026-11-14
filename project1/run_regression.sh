
#!/bin/bash

set -e

cd "$(dirname "$0")"

mkdir -p evidence

for seed in 1 2 3
do
    echo "Running FIFO test with seed $seed"

    FIFO_SEED=$seed make -C crv SIM=icarus > "evidence/crv_seed${seed}.log" 2>&1

    echo "Seed $seed passed"
done

echo "All three FIFO regression tests passed!"
