
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from models.fifo_model import FifoModel


# Driver, Monitor, and Scoreboard are names chosen for this project.
# FifoModel is provided by the professor.

class Driver:
    def __init__(self, dut):
        self.dut = dut

    async def send(self, wr_en=0, rd_en=0, wr_data=0):
        await FallingEdge(self.dut.clk)

        self.dut.wr_en.value = wr_en
        self.dut.rd_en.value = rd_en
        self.dut.wr_data.value = wr_data

        await RisingEdge(self.dut.clk)
        await Timer(1, units="ns")


class Monitor:
    def __init__(self, dut):
        self.dut = dut

    def sample(self):
        return {
            "count": int(self.dut.count.value),
            "full": int(self.dut.full.value),
            "empty": int(self.dut.empty.value),
            "rd_data": int(self.dut.rd_data.value)
            if not int(self.dut.empty.value) else None
        }


class Scoreboard:
    def __init__(self):
        self.model = FifoModel(8, 8)
        self.cycle_num = 0

    def check_reset(self, actual):
        assert actual["count"] == 0
        assert actual["full"] == 0
        assert actual["empty"] == 1

    def check(self, actual, wr_en, rd_en, wr_data):
        self.model.step(wr_en, wr_data, rd_en)
        self.cycle_num += 1

        assert actual["count"] == self.model.count, \
            f"Cycle {self.cycle_num}: count mismatch"

        assert actual["full"] == int(self.model.full), \
            f"Cycle {self.cycle_num}: full mismatch"

        assert actual["empty"] == int(self.model.empty), \
            f"Cycle {self.cycle_num}: empty mismatch"

        if not self.model.empty:
            assert actual["rd_data"] == self.model.head, \
                f"Cycle {self.cycle_num}: rd_data mismatch"


@cocotb.test()
async def test_fifo(dut):
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
    scoreboard.model.reset()
    scoreboard.check_reset(monitor.sample())

    dut.rst_n.value = 1

    # VP-5: read while empty
    await driver.send(rd_en=1)
    scoreboard.check(monitor.sample(), 0, 1, 0)

    # VP-2 and VP-7: fill FIFO
    for i in range(8):
        await driver.send(wr_en=1, wr_data=0x40 + i)
        scoreboard.check(monitor.sample(), 1, 0, 0x40 + i)

    # VP-4: write while full
    await driver.send(wr_en=1, wr_data=0xFF)
    scoreboard.check(monitor.sample(), 1, 0, 0xFF)

    # VP-6: simultaneous read/write while full
    await driver.send(wr_en=1, rd_en=1, wr_data=0xAA)
    scoreboard.check(monitor.sample(), 1, 1, 0xAA)

    # VP-3 and VP-8: drain FIFO and check ordering
    for i in range(8):
        await driver.send(rd_en=1)
        scoreboard.check(monitor.sample(), 0, 1, 0)

    # VP-6: simultaneous read/write while empty
    await driver.send(wr_en=1, rd_en=1, wr_data=0x55)
    scoreboard.check(monitor.sample(), 1, 1, 0x55)

    # VP-9: repeated operations for pointer wrap-around
    for i in range(20):
        await driver.send(wr_en=1, wr_data=i)
        scoreboard.check(monitor.sample(), 1, 0, i)

        await driver.send(rd_en=1)
        scoreboard.check(monitor.sample(), 0, 1, 0)

    # VP-1: reset while FIFO contains data
    await driver.send(wr_en=1, wr_data=0xAA)
    scoreboard.check(monitor.sample(), 1, 0, 0xAA)

    await FallingEdge(dut.clk)
    dut.rst_n.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    scoreboard.model.reset()
    scoreboard.check_reset(monitor.sample())

    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    dut._log.info("All directed FIFO tests passed!")
