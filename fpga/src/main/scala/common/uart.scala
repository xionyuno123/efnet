package  efnet.common

import chisel3._
import chisel3.util._
import efnet.utils

/** Uart IO interface
  *  
  * @enq: producer interface
  * @deq: consumer interface 
  *
  * @param w: data width
  * 
  * Using Decoupled(...) create a producer interface.
  * This produces the following ports:
  *   input    io_readyValid_ready 
  *   output   io_readyValid_valid
  *   output   io_readyValid_bits
  * 
  * Flipped will changes the direction of all ports:
  *   output   io_readyValid_ready
  *   input    io_readyValid_valid
  *   input    io_readyValid_bits
  */
class UartIO(w:Int) extends Bundle {
  val enq = Flipped(Decoupled(UInt(w.W)))
  val deq = Decoupled(UInt(w.W))
}

/** Uart Peripheral interface
  * 
  * @txd tx pin used to transmit data serially 
  * @rxd rx pin used to receive data serially
  */
class UartPeripheral extends Bundle {
  val txd = Output(Bool())
  val rxd = Input(Bool())
}

class Uart(
  sys_clock_freq:Int = 50_000_000,
  buad_rate:Int = 9600,
  data_width:Int = 8,
  stop_width:Int = 1,
  wait_time:Int = 0,
  parity_check: Int = 0,
) extends Module {
  val io = IO (new Bundle {
    val ctl = new UartIO(data_width)
    val pins = new UartPeripheral()
  })

  val rx = Module(new UartRx(data_width,stop_width,parity_check))
  val tx = Module(new UartTx(data_width,stop_width,parity_check,wait_time))
  val buad_rate_gen = Module(new BuadRateGenerator(sys_clock_freq,buad_rate))
  val ppl = Module(new PhaseLockedLoop())

  // connect ppl pins
  ppl.io.clock_in <> clock.asBool
  ppl.io.reset <> reset.asBool

  buad_rate_gen.clock <> ppl.io.clock_out.asClock
  buad_rate_gen.reset <> ppl.io.locked

  rx.clock <> buad_rate_gen.io.buad_clock_out.asClock
  rx.reset <> ppl.io.locked  
  tx.clock <> buad_rate_gen.io.buad_clock_out.asClock
  tx.reset <> ppl.io.locked

  // connect ctl and pins  
  io.ctl.enq <> tx.io.enq
  io.ctl.deq <> rx.io.deq
  io.pins.txd <> tx.io.txd
  io.pins.rxd <> rx.io.rxd
}

class BuadRateGenerator(sys_clock_freq:Int,buad_rate:Int) extends Module {
  val io = IO (new Bundle {
    val buad_clock_out = Output(Bool())
  })

  if (sys_clock_freq % buad_rate != 0) {
    utils.logger.warn("sys_clock_freq % buad_rate != 0")
  }

  val div = sys_clock_freq / buad_rate

  val clk_divider = Module(new ClockDivider(div))
  
  clock.asBool <> clk_divider.io.clock_in
  clk_divider.io.clock_out <> io.buad_clock_out
  clk_divider.io.reset <> reset
}

class UartTx(data_width:Int,stop_width:Int,parity_check:Int,wait_time:Int) extends Module {
  val io = IO( new Bundle {
    val enq = Flipped(Decoupled(UInt(data_width.W)))
    val txd = Output(Bool())
  })

  val parity_bits = if (parity_check == 0) {0} else {1}
  val frame_len = data_width + 1 + stop_width + parity_bits + wait_time
  val buf_width = 1 + data_width
  val buf_init_val = (1 << buf_width) - 1
  
  val idle = {
    var idle = List[UInt]()
    for (x <- 0 until wait_time + stop_width) {
      idle = idle.appended(x.U)
    }
    idle
  }

  val ready = (wait_time + stop_width).U

  val runnings = {
    var runnings = List[UInt]()
    for (x <- (wait_time + stop_width + 1) until frame_len) {
      runnings = runnings.appended(x.U)
    }
    runnings
  }

  val state = RegInit(idle.head)
  val buf = RegInit(buf_init_val.U(buf_width.W))
  val parity = if (parity_check == 0) {
    None
  } else {
    Some(RegInit(false.B))
  }

  parity match {
    case Some(p) => {
      p := buf(0) ^ buf(1)
    }
    case None => {}
  }

  switch (state) {
    is(idle) {
      when (state === idle.last) {
        buf := Cat(1.U,buf(buf_width - 1,1))
        state := state - 1.U
      }.elsewhen(state =/= idle.head) {
        state := state - 1.U
      }.elsewhen(io.enq.valid) {
        buf := Cat(io.enq.bits,0.U)
        state := runnings.last
      }
    }

    is(runnings) {
      buf := Cat(1.U,buf(buf_width - 1,1))
      state := state - 1.U
    }

    is(ready) {
      parity match {
        case None => {
          buf := Cat(1.U,buf(buf_width - 1,1))
        }
        case Some(p) => {
          if (parity_check == 1) {
            buf := Cat(buf(buf_width - 1,1),p.asUInt)
          } else {
            buf := Cat(buf(buf_width - 1,1),~p.asUInt)
          }
        }
      }
      state := idle.last
    }
  }

  io.txd := buf(0)
  io.enq.ready := (state < ready)
}

class UartRx(data_width:Int,stop_width:Int,parity_check:Int) extends Module {
  val io = IO (new Bundle {
    val deq = Decoupled(UInt(data_width.W))
    val rxd = Input(Bool())
  })

  val parity_bits = if (parity_check == 0) {0} else {1}
  val frame_len = data_width + 1 + stop_width + parity_bits
  val buf_width = 1 + data_width
  val buf_init_val = (1 << buf_width) - 1
 
  val idle = {
    var idle = List[UInt]()
    for (x <- 0 until stop_width) {
      idle = idle.appended(x.U)
    }
    idle
  }

  val ready = (stop_width).U
  val runnings = {
    var runnings = List[UInt]()
    for (x <- (stop_width + 1) until frame_len) {
      runnings = runnings.appended(x.U)
    }
    runnings
  }

  val state = RegInit(idle.head)
  val rx = RegNext(RegNext(io.rxd))
  val buf = RegInit(0.U(buf_width.W))
  val error = RegInit(false.B)
  val parity = if (parity_check == 0) {
    None
  }else{
    Some(RegInit(false.B))
  }

  parity match {
    case None => {}
    case Some(p) => {
      p := buf(0) ^ buf(1)
    }
  }

  switch (state) {
    is(idle) {
      when (!rx) {
        buf := 0.U // clear buffer
        error := false.B // reset error flag
        state := runnings.last
      }.elsewhen(state =/= idle.head) {
        state := state - 1.U
      }
    }

    is(runnings) {
      buf := Cat(buf(buf_width - 1,1),rx)
      state := state - 1.U
    }

    is(ready) {
      parity match {
        case None => {
          buf := Cat(buf(buf_width - 1,1),rx)
        }
        case Some(p) => {
          if (parity_check == 1) {
            error := p =/= rx.asBool
          } else {
            error := p === rx.asBool
          }
        }
      }
      state := state - 1.U
    }
  }

  io.deq.valid := (state < ready)
  io.deq.bits := buf(buf_width - 1,1)
}