
# FINDINGS — Project 1 FIFO Verification

## Score

| Pool | found | total | % |
|---|---:|---:|---:|
| released (practice) | 8 | 8 | 100.0% |
| hidden (reported at grading) | Not available | Not available | Not available |

**Command run:**

```bash
cd ~/fifo_final_project
export PYTHONPATH="$PWD/lib:$PWD/project1/tb:$PYTHONPATH"
python -m craft_mutate.mutate --tb project1/coverage --pool project1/coverage/mutants_released.yaml --sim icarus
```

The final mutation test detected all 8 released mutants. The clean FIFO passed before the mutants were tested.

The layered coverage testbench used a driver, monitor, and scoreboard with the professor-provided FIFO reference model. The scoreboard 
checked `count`, `full`, `empty`, and `rd_data` when valid.

## Survivors

No mutants survived in the released pool. All 8 were detected.

| Mutant | What it changes | Reachable by my stimulus? | Observable by my checks? | Why it survived |
|---|---|---|---|---|
| None | All released mutants detected | N/A | N/A | No released survivors |

## What I changed, and what it bought

| Change | Score before | Score after | Which survivors it caught |
|---|---:|---:|---|
| Added biased random transactions, occupancy and operation coverage, and scoreboard checks for FIFO outputs | Not measured | 8/8 (100%) | All 8 released mutants detected in the final run |
| Reused the driver, monitor, and scoreboard in the layered coverage testbench | 8/8 (100%) | 8/8 (100%) | No additional mutants; maintained the score |

The initial coverage starter had limited checking and coverage collection. The completed testbench checks the FIFO outputs and measures occupancy and operation combinations.

The final coverage test reached 100% operation coverage, 100% occupancy coverage, and 100% occupancy × operation cross coverage.

There was no measured mutation score before the initial improvements, so the exact improvement in mutant detection cannot be calculated.
The later layering change retained the 8/8 result.

## Residual risk

1. **Reset-related behavior:** The directed test now checks reset while the FIFO contains data, and it passed. However, the constrained random coverage test 
only applies reset at the beginning. Additional reset sequences, such as reset combined with pending read and write requests, could provide more confidence.

2. **Different FIFO parameter values:** The verification suite uses WIDTH=8 and DEPTH=8. Bugs that appear only with other supported widths or depths might remain undetected.

**If I had another day:** I would expand the reset tests to include simultaneous requests during reset and test additional FIFO parameter configurations.
 These tests could help detect bugs not represented in the released mutation pool.

## Evidence

- `evidence/mutation_layered.log` — final 8/8 mutation result.
- `evidence/coverage_final_layered.log` — final layered coverage test.
- `evidence/directed_final.log` — directed tests including occupied FIFO reset.
- `evidence/crv_seed1.log`, `crv_seed2.log`, `crv_seed3.log` — three seed constrained random regression.
- `evidence/coverage.yml` — functional coverage results.
- `evidence/coverage_progress.csv` — coverage progress over 3,000 transactions.
