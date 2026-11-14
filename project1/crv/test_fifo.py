
"""Constrained-random FIFO testbench using pyvsc."""

import cocotb
import random
import os
import vsc
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from models.fifo_model import FifoModel

WIDTH = 8
DEPTH = 8
MASK = (1 << WIDTH) - 1


# FifoTxn and fifo_constraints are from the professor's HW5 starter.
@vsc.randobj
class FifoTxn:
    def __init__(self, width=WIDTH):
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(width)
        self.count = vsc.uint8_t(0)

    @vsc.constraint
    def fifo_constraints(self):
        with vsc.if_then(self.count <= 2):
            vsc.dist(self.wr_en, [vsc.weight(1, 4), vsc.weight(0, 1)])
        with vsc.else_if(self.count >= 6):
            vsc.dist(self.rd_en, [vsc.weight(1, 4), vsc.weight(0, 1)])
        with vsc.else_then:
            vsc.dist(self.wr_en, [vsc.weight(1, 3), vsc.weight(0, 1)])
            vsc.dist(self.rd_en, [vsc.weight(1, 3), vsc.weight(0, 1)])


@cocotb.test()
async def test_crv(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    model = FifoModel(WIDTH, DEPTH)

    # Reset
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    dut.rst_n.value = 0

    for _ in range(3):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1
    model.reset()
    await FallingEdge(dut.clk)

    # Random seed
    seed = int(os.getenv("FIFO_SEED", "1"))
    random.seed(seed)

    txn = FifoTxn()
    txn.set_randstate(vsc.RandState.mkFromSeed(seed))

    dut._log.info(f"Random seed: {seed}")

    seen_counts = set()
    simultaneous_count = 0

    for _ in range(3000):
        txn.count = model.count
        seen_counts.add(model.count)

        txn.randomize()

        wr = int(txn.wr_en)
        rd = int(txn.rd_en)
        data = int(txn.wr_data)

        if wr == 1 and rd == 1 and 0 < model.count < DEPTH:
            simultaneous_count += 1

        dut.wr_en.value = wr
        dut.rd_en.value = rd
        dut.wr_data.value = data

        model.step(wr, data, rd)

        await RisingEdge(dut.clk)
        await Timer(1, units="ns")

        assert int(dut.count.value) == model.count, \
            f"count {int(dut.count.value)} != model {model.count}"

        assert int(dut.full.value) == int(model.full), \
            "full mismatch"

        assert int(dut.empty.value) == int(model.empty), \
            "empty mismatch"

        if not model.empty:
            assert int(dut.rd_data.value) == model.head, \
                "rd_data mismatch"

        await FallingEdge(dut.clk)

    seen_counts.add(model.count)

    dut._log.info(f"Occupancy levels reached: {sorted(seen_counts)}")
    assert seen_counts == set(range(DEPTH + 1)), \
        "Not all occupancy levels reached"

    dut._log.info(f"Simultaneous read/write cycles: {simultaneous_count}")
    assert simultaneous_count > 0, \
        "No simultaneous read/write cycles reached"

    dut._log.info("Constrained-random FIFO test passed!")
