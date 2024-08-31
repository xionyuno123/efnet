import random
import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

class UartUser:
  data_width:int
  dataset:list[int]
  data_rdy:any
  data_in:any
  clock:Clock
  reset:any
  tx_busy:any

  def __init__(self,clock,reset,data_width,data_in,data_rdy,tx_busy):
    self.data_width = data_width
    self.data_rdy = data_rdy
    self.tx_busy = tx_busy
    self.data_in = data_in
    self.clock = clock
    self.reset = reset
    self.dataset = []

  def init_datasets(self,nums) -> list[int]:
    dataset = []
    max_value = pow(2,self.data_width) - 1
    for _ in range(nums):
      dataset.append(random.randint(0,max_value))
    self.dataset = dataset
    return dataset
  
  async def start(self):
    # wait synchronize reset signal
    while True:
      await RisingEdge(self.clock)
      if self.reset == 1:
        self.data_in.value = 0
        self.data_rdy.value = 0
        break

    for data in self.dataset:
      # prepare data
      await RisingEdge(self.clock)
      self.data_in.value = data
      # enable data ready
      await RisingEdge(self.clock)
      self.data_rdy.value = 1
      # wait data sent complete
      handshake = False
      while True:
        await RisingEdge(self.clock)
        if handshake:
          if self.tx_busy.value == 0:
            self.data_rdy.value = 0
            break
        else:
          if self.tx_busy.value == 1:
            handshake = True
    pass

def check_parity(data,parity) -> bool:
  global TEST_PARAM_PARITY
  one_counts = 0
  while True:
    if data == 0:
      break
    if data % 2 == 1:
      one_counts += 1
    data = data >> 1
  if TEST_PARAM_PARITY == 1:
    return ((one_counts % 2 == 0) and (parity == 1)) or ((one_counts % 2 == 1) and (parity == 0))
  else:
    return ((one_counts % 2 == 0) and (parity == 0)) or ((one_counts % 2 == 1) and (parity == 1))

async def uart_tx_data(clock,tx) -> int:
  global TEST_PARAM_WIDTH
  global TEST_PARAM_PARITY
  global TEST_PARAM_STOP_BITS
  # check start bit
  while True:
    await RisingEdge(clock)
    if tx.value == 0:
      break

  data = None
  for _ in range(TEST_PARAM_WIDTH):
    await RisingEdge(clock)
    if data is None:
      data = int(tx.value)
    else:
      data = (data << 1) + int(tx.value)
  
  if TEST_PARAM_PARITY > 0:
    await RisingEdge(clock)
    parity = tx.value
    # check parity
    assert check_parity(data,parity)

  for _ in range(TEST_PARAM_STOP_BITS):
    await RisingEdge(clock)
    assert tx.value == 1
  return data

async def _test_uart_tx(dut):
  global TEST_PARAM_WIDTH
  # 50 MHz clock
  clock = Clock(dut.clock,20,units="ns")
  cocotb.start_soon(clock.start())

  await RisingEdge(dut.clock)
  dut.reset.value = 0
  
  user = UartUser(dut.clock,dut.reset,TEST_PARAM_WIDTH,dut.io_data_in,dut.io_data_valid,dut.io_tx_busy)
  dataset = user.init_datasets(100)
  cocotb.start_soon(user.start())
  
  # enable reset signal
  await RisingEdge(dut.clock)
  dut.reset.value = 1
  await RisingEdge(dut.clock)
  dut.reset.value = 0
  
  # check tx
  for data in dataset:
    recv_data = await uart_tx_data(dut.clock,dut.io_tx)
    assert recv_data == data
  pass