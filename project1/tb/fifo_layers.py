
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from models.fifo_model import FifoModel


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
        self.model.reset()

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
