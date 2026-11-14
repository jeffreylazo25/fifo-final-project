
import cocotb
import vsc
from pathlib import Path
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_db
from fifo_layers import Driver, Monitor, Scoreboard

WIDTH = 8
DEPTH = 8
SEED = 1


# Transaction and constraints adapted from HW5.
@vsc.randobj
class FifoTxn:
    def __init__(self):
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(WIDTH)
        self.count = vsc.uint8_t(0)

    @vsc.constraint
    def fifo_constraints(self):
        with vsc.if_then(self.count <= 2):
            vsc.dist(self.wr_en, [vsc.weight(1, 4),
                                  vsc.weight(0, 1)])
        with vsc.else_if(self.count >= 6):
            vsc.dist(self.rd_en, [vsc.weight(1, 4),
                                  vsc.weight(0, 1)])
        with vsc.else_then:
            vsc.dist(self.wr_en, [vsc.weight(1, 3),
                                  vsc.weight(0, 1)])
            vsc.dist(self.rd_en, [vsc.weight(1, 3),
                                  vsc.weight(0, 1)])


# Operation helper adapted from HW6.
def op_bin(count, wr, rd):
    if wr and rd:
        return "simul"
    if wr:
        return "write"
    if rd:
        return "read"
    return "idle"


def occ_bin(count, wr, rd):
    if count == 0:
        return "empty"
    if count == 1:
        return "near_empty"
    if count == DEPTH - 1:
        return "near_full"
    if count == DEPTH:
        return "full"
    return "middle"


@CoverPoint("top.op", xf=op_bin,
            bins=["idle", "write", "read", "simul"])
def sample_op(count, wr, rd):
    pass


@CoverPoint("top.occ", xf=occ_bin,
            bins=["empty", "near_empty", "middle",
                  "near_full", "full"])
def sample_occ(count, wr, rd):
    pass


@CoverCross("top.occ_x_op", items=["top.occ", "top.op"])
def sample_cross(count, wr, rd):
    pass


def sample_coverage(count, wr, rd):
    sample_op(count, wr, rd)
    sample_occ(count, wr, rd)
    sample_cross(count, wr, rd)


@cocotb.test()
async def test_coverage(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    dut.rst_n.value = 0

    driver = Driver(dut)
    monitor = Monitor(dut)
    scoreboard = Scoreboard()

    for _ in range(3):
        await RisingEdge(dut.clk)

    await FallingEdge(dut.clk)
    scoreboard.check_reset(monitor.sample())
    dut.rst_n.value = 1

    txn = FifoTxn()
    txn.set_randstate(vsc.RandState.mkFromSeed(SEED))

    occupancy = [0] * (DEPTH + 1)
    simultaneous = 0

    evidence = Path("../evidence")
    evidence.mkdir(exist_ok=True)

    with open(evidence / "coverage_progress.csv", "w") as progress:
        progress.write("transactions,coverage\n")

        for i in range(3000):
            count = scoreboard.model.count
            occupancy[count] += 1

            txn.count = count
            txn.randomize()

            wr = int(txn.wr_en)
            rd = int(txn.rd_en)
            data = int(txn.wr_data)

            sample_coverage(count, wr, rd)

            if wr and rd:
                simultaneous += 1

            await driver.send(wr, rd, data)
            scoreboard.check(monitor.sample(), wr, rd, data)

            if (i + 1) % 100 == 0:
                cross = coverage_db["top.occ_x_op"]
                progress.write(
                    f"{i + 1},{cross.cover_percentage:.2f}\n"
                )

    coverage_db.export_to_yaml(
        str(evidence / "coverage.yml")
    )

    op = coverage_db["top.op"].cover_percentage
    occ = coverage_db["top.occ"].cover_percentage
    cross = coverage_db["top.occ_x_op"].cover_percentage

    dut._log.info(f"Seed: {SEED}")
    dut._log.info("Transactions: 3000")
    dut._log.info(f"Operation coverage: {op:.2f}%")
    dut._log.info(f"Occupancy coverage: {occ:.2f}%")
    dut._log.info(f"Cross coverage: {cross:.2f}%")
    dut._log.info(f"Occupancy distribution: {occupancy}")
    dut._log.info(f"Simultaneous requests: {simultaneous}")
    dut._log.info("Coverage test completed!")
