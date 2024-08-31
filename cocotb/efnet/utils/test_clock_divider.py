from pathlib import Path

import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

async def _test_clock_divider(dut):
  global TEST_PARAM_CNT
  # 50 MHz clock
  clock = Clock(dut.io_clock_in,20,units="ns")
  cocotb.start_soon(clock.start())
  
  # Enable Reset
  dut.io_reset = 0
  await RisingEdge(dut.io_clock_in)
  dut.io_reset = 1
  await RisingEdge(dut.io_clock_in)
  dut.io_reset = 0

  # Record the time
  if TEST_PARAM_CNT % 2 != 0:
    cocotb.log.error("TEST_PARAM_CNT must be even")
  if 50_000_000 % TEST_PARAM_CNT != 0:
    cocotb.log.error("50_000_000 must be divisible by TEST_PARAM_CNT")
  if TEST_PARAM_CNT > 50_000_000:
    cocotb.log.error("TEST_PARAM_CNT must be less than 50_000_000")

  target_freq = 50_000_000 / TEST_PARAM_CNT
  cycle_period = 1000_000_000 / target_freq
  
  await RisingEdge(dut.io_clock_out)
  start_time = cocotb.utils.get_sim_time(units="ns")
  
  for i in range(1000):
    await RisingEdge(dut.io_clock_out)
  end_time = cocotb.utils.get_sim_time(units="ns")
  period = end_time - start_time

  assert period == cycle_period * 1000, f"Expected {cycle_period * 1000}, got {period}"

  pass
