package  efnet.common

import chisel3._
import chisel3.util._

object UartParamters {
  val data_width:Int = 8
  val stop_width:Int = 1
}

/** Uart IO interface
  *  
  * @enq: producer interface
  * @deq: consumer interface 
  *
  * @param width: data width
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
class UartIO() extends Bundle {
  val enq = Flipped(Decoupled(UInt(UartParamters.data_width.W)))
  val deq = Decoupled(UInt(UartParamters.data_width.W))
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

/**
  * 
  *
  * @param width
  * @param parity
  * 
  */
class Uart extends Module {
  val io = IO(new Bundle {
    val ctl = new UartIO() // enq producer interface, deq consumer interface
    val pins = new UartPeripheral
  })

  val tx = Module(new UartTx())
  val rx = Module(new UartRx())

  tx.io.txd <> io.pins.txd
  rx.io.rxd <> io.pins.rxd
  tx.io.enq <> io.ctl.enq  
  rx.io.deq <> io.ctl.deq
}

class UartTx extends Module {
  val io =IO(new Bundle {
      val txd = Output(Bool())
      val enq = Flipped(Decoupled(UInt(UartParamters.data_width.W))) 
    }
  )
  
  val frame_len = 1 + UartParamters.data_width + UartParamters.stop_width; 
  val buf_len = 1 + UartParamters.data_width
  val buf_init_val = 1 << buf_len - 1
  
  val idle :: runnings = Enum(frame_len + 1) 
  val state = RegInit(idle)
  val buf = RegInit(buf_init_val.U(buf_len.W))
  io.txd := buf(0)

  switch (state) {
    is(idle) {
      when (io.enq.valid) {
        buf := Cat(io.enq.bits,0.U)
        state := runnings.last
      }
    }

    is (runnings) {
      state := state - 1.U
      buf := Cat(1.U, buf(buf_len - 1,1))
    }
  }

  io.enq.ready := (state === idle)
}

class UartRx() extends Module {
  val io = IO(new Bundle {
    val rxd = Input(Bool())
    val deq = Decoupled(UInt(UartParamters.data_width.W))
  })

  val frame_len = 1 + UartParamters.data_width + UartParamters.stop_width; 
  val buf_len = 1 + UartParamters.data_width
  val buf_init_val = 0

  val idle :: stop :: runnings = Enum(frame_len + 1)
  val state = RegInit(idle)
  val buf = RegInit(buf_init_val.U(buf_len.W))
  val valid = RegInit(false.B)
  val rx = RegNext(RegNext(io.rxd))

  when (valid && io.deq.ready) {
    valid := false.B
  }

  switch (state) {
    is (idle) {
      when (rx === 0.U) {
        state := runnings.last
        valid := false.B
      }
    }

    is (runnings) {
      state := state - 1.U
      buf := Cat(rx, buf(buf_len - 1,1))
    }

    is(stop) {
      state := idle
      valid := true.B
    }
  }

  io.deq.valid := valid
  io.deq.bits := buf (buf_len - 2, 0)
}

class UartLoopback() extends Module {
  val io = IO((new UartIO()))
  val uart = Module(new Uart())

  uart.io.pins.rxd := uart.io.pins.txd

  io.enq <> uart.io.ctl.enq
  io.deq <> uart.io.ctl.deq
}