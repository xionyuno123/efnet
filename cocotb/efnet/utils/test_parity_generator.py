import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

class DataBit:
  data:str
  def __init__(self,data:str):
    self.data = data
  
  def next_bit(self) -> int | None:
    if len(self.data) == 0:
      return None
    data_bit = self.data[0]
    self.data = self.data[1:]
    return int(data_bit)

async def _test_parity_generator(dut):
  global TEST_PARAM_PARITY
  if TEST_PARAM_PARITY == 0:
    return
  # 50 MHz
  clock = Clock(dut.clock,20,units="ns")
  cocotb.start_soon(clock.start())

  # idle 
  await RisingEdge(dut.clock)
  dut.reset.value = 0
  await RisingEdge(dut.clock)
  dut.reset.value = 0

  data = "01"
  parity = await compute_parity(data,dut)
  assert check_parity(data,parity)
  data = "10"
  parity = await compute_parity(data,dut)
  assert check_parity(data,parity)
  data = "0"
  parity = await compute_parity(data,dut)
  assert check_parity(data,parity)
  data = "1"
  parity = await compute_parity(data,dut)
  data = "11"
  parity = await compute_parity(data,dut)
  assert check_parity(data,parity)
  data = "00"
  parity = await compute_parity(data,dut)
  assert check_parity(data,parity)

  # idle clock
  await RisingEdge(dut.clock)
  dut.reset.value = 0



async def compute_parity(data:str,dut) -> int | None:
  bitdata = DataBit(data)
  num_bits = 0
  parity = None
  while True:
    bit = bitdata.next_bit()
    if bit is None:
      break
    assert bit == 0 or bit == 1, "Internal error"
    if num_bits == 0:
      # enable reset signal
      await RisingEdge(dut.clock)
      dut.reset.value = 1
      dut.io_data.value = bit
    elif num_bits == 1:
      # disable reset signal
      await RisingEdge(dut.clock)
      dut.reset.value = 0
      dut.io_data.value = bit
    else:
      await RisingEdge(dut.clock)
      dut.io_data.value = bit
    num_bits += 1
       
  # wait two clock cycle and read parity
  if num_bits == 1:
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    dut.io_data.value = 0
    await RisingEdge(dut.clock)
    parity = int(dut.io_parity.value)
  if num_bits > 1:
    await RisingEdge(dut.clock)
    dut.io_data.value = 0
    dut.reset.value = 0
    await RisingEdge(dut.clock)
    dut.io_data.value = 0
    dut.reset.value = 0
    parity = int(dut.io_parity.value)
  
  return parity


def check_parity(data:str,parity:int) -> bool:
  global TEST_PARAM_PARITY
  bitdata = DataBit(data)
  one_counts = 0
  while True:
    bit = bitdata.next_bit()
    if bit is None:
      break
    if bit == 1:
      one_counts += 1
  
  if TEST_PARAM_PARITY == 1:
    # odd parity
    return (one_counts % 2 == 1 and parity == 0) or (one_counts % 2 == 0 and parity == 1)
  if TEST_PARAM_PARITY == 2:
    # even parity
    return (one_counts % 2 == 1 and parity == 1) or (one_counts % 2 == 0 and parity == 0)
  if TEST_PARAM_PARITY == 0:
    return True

  