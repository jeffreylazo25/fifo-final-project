
TOPLEVEL_LANG ?= verilog
SIM ?= verilator

DUT ?= $(CURDIR)/../../dut/fifo.sv
VERILOG_SOURCES = $(DUT)
TOPLEVEL = fifo
MODULE = test_fifo

export PYTHONPATH := $(CURDIR)/../../lib:$(CURDIR)/../tb:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
