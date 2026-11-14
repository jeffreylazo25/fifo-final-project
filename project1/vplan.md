# Project 1 Verification Plan: Synchronous FIFO

## Goal

Verify the synchronous first word fall through (FWFT) FIFO using directed and constrained-random tests.

The FIFO has WIDTH=8 and DEPTH=8. The reference specification is `dut/specs/fifo.md`.

The testbench checks reset behavior, reads, writes, status flags, data ordering, simultaneous operations, and boundary conditions.

## Requirements and Test Matrix

| ID | Requirement | Feature / Coverage Points | Test | Risk |
|---|---|---|---|---|
| VP-1 | Active low synchronous reset clears the FIFO on a clock edge | Reset at startup and while FIFO contains data | test_fifo | Incorrect reset can leave old data |
| VP-2 | Writes are accepted when wr_en=1 and FIFO is not full | Single and consecutive writes | test_fifo, test_crv | Data can be lost |
| VP-3 | Reads are accepted when rd_en=1 and FIFO is not empty | Single and consecutive reads | test_fifo, test_crv | Incorrect data can be returned |
| VP-4 | Writes while full are dropped | Full occupancy with write request | test_fifo, test_coverage | Stored data may be corrupted |
| VP-5 | Reads while empty are ignored | Empty occupancy with read request | test_fifo, test_coverage | Count may change incorrectly |
| VP-6 | Simultaneous read/write follows pre edge full and empty flags | Both enabled at empty, partial, and full occupancy | test_fifo, test_crv, test_coverage | Incorrect count or data |
| VP-7 | Full and empty flags correspond to occupancy | Count from 0 through 8 | test_fifo, test_crv, test_coverage | Wrong flags allow invalid operations |
| VP-8 | FIFO preserves data ordering | Multiple writes and reads, random interleaving | test_fifo, test_crv, test_coverage | Data can be returned out of order |
| VP-9 | FIFO works correctly after pointer wrap around | Repeated writes and reads beyond DEPTH | test_fifo, test_crv | Pointer errors can corrupt data |

## Testbench Environment

The testbench contains:

- Driver: applies read and write requests to the FIFO.
- Monitor: observes the FIFO outputs.
- Scoreboard: uses the professor provided `FifoModel` to predict expected behavior and compare results.
- Transaction generator: uses pyvsc to generate constrained random requests.
- Coverage collector: records occupancy categories and operation combinations.

The layered coverage testbench reuses the driver, monitor, and scoreboard from `fifo_layers.py`.

The scoreboard checks `count`, `full`, and `empty` after every tested clock cycle. It also checks `rd_data` whenever the FIFO is not empty.

## Functional Coverage

### Coverpoints

The coverage testbench implements two coverpoints:

1. Operation: idle, write, read, simultaneous read/write.
2. Occupancy category: empty, near empty, middle, near full, full.

The testbench also records the occupancy distribution across all nine FIFO count values, from 0 through 8.

Reset behavior and accepted or ignored operations are checked through the directed tests and reference-model scoreboard.

### Coverage Crosses

The coverage testbench implements one cross:

1. Occupancy category × operation.

This creates 20 combinations from the five occupancy categories and four operation types.

The coverage model samples the requested operation using the FIFO occupancy before the active clock edge.

### Coverage Target

The target is 100% of the defined reachable functional coverage bins.

The final coverage test reached:

- Operation coverage: 100%.
- Occupancy category coverage: 100%.
- Occupancy × operation coverage: 100%.

All 20 cross combinations were exercised.

## Constrained-Random Testing

The transaction generator uses pyvsc with fixed, reproducible seeds.

The constraints:

- Favor writes when the FIFO is near empty.
- Favor reads when the FIFO is near full.
- Generate simultaneous reads and writes.
- Exercise the full and empty boundaries.
- Generate different write data values.

Writes requested while full and reads requested while empty are allowed because the FIFO specification defines their behavior.

The constrained random regression was tested using seeds 1, 2, and 3.

Each seed generated 3,000 transactions, for a total of 9,000 transactions. All three runs passed the scoreboard checks and reached every occupancy level from 0 through 8.

## Coverage Closure

Coverage was measured using cocotb coverage.

The final coverage test ran 3,000 constrained random transactions using seed 1.

The operation, occupancy category, and cross coverage models each reached 100%.

Coverage progress was recorded in `evidence/coverage_progress.csv`, and the final coverage results were saved in `evidence/coverage.yml`.

The final run used biased constrained random stimulus to reach the full, empty, and near boundary conditions.

## Mutation Testing

The released FIFO mutant pool was tested using the project's mutation framework.

The final layered coverage testbench detected all eight released mutants.

The mutation score was:

**8/8 = 100%**

The mutation results were saved in `evidence/mutation_layered.log` and documented in `FINDINGS.md`.

Because no released mutants survived, the report discusses remaining verification risks instead of claiming that surviving mutants were observed.

Two residual fault classes are considered:

1. Parameter configurations other than WIDTH=8 and DEPTH=8.
2. Reset related faults that may not be covered by the limited reset sequences tested.

## Illegal and Undefined Behavior

The testbench checks simultaneous read/write at the empty boundary.

The specification states that the read is ignored and the write is accepted, resulting in occupancy 1.

At full occupancy, a simultaneous request accepts the read and drops the write.

These are defined boundary behaviors, not undefined operations.

The directed tests check both cases, and the coverage model records simultaneous requests at different occupancy categories.

## Reproducibility

The project includes:

- Icarus Verilog simulation.
- cocotb and pyvsc testing.
- Fixed random seeds 1, 2, and 3.
- A `run_regression.sh` script to repeat the constrained random tests.
- Saved regression logs in the `evidence` directory.
- Functional coverage results.
- Mutation-testing results.

The final report will include the simulator versions, commands, coverage results, mutation score, and remaining verification limitations.
