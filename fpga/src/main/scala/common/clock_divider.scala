package efnet.common

import chisel3._
import chisel3.util._

class ClockDivider(
  div:Int = 2
) extends RawModule {
  require(div > 0, "div must be greater than 0")
  
  val io = IO (new Bundle {
    val clock_in = Input(Bool())
    val reset = Input(Bool())
    val clock_out = Output(Bool())
  })

  if (div == 1) {
    io.clock_out := io.clock_in
  } else if (div == 2) {
    // optimize delay register
    withClockAndReset(clock = io.clock_in.asClock, reset = io.reset) {
      val clk_out = RegInit(false.B)
      clk_out := ~io.clock_in
      io.clock_out := clk_out
    }
  } else if (div == 3) {
    // optimize adder logic 
    withClockAndReset(clock = io.clock_in.asClock, reset = io.reset) {
      val delay = RegInit(false.B)
      val clk_out = RegInit(false.B)
      when (clk_out === false.B) {
        clk_out := true.B
        delay := false.B
      }.elsewhen(delay) {
        delay := false.B
        clk_out := false.B
      }.otherwise(delay := true.B)
      io.clock_out := clk_out
    }
  } else {
    withClockAndReset(clock = io.clock_in.asClock, reset = io.reset) {
      val cnt = RegInit(div.U(log2Ceil(div).W))
      val clk_out = RegInit(false.B)
      when(cnt === (div).U) {
        clk_out := ~clk_out
        cnt := 1.U
      }.otherwise (cnt := cnt + 1.U)
    }
  }
}