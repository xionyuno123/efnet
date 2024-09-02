package efnet.common

import chisel3._
import chisel3.util.HasBlackBoxResource
import chisel3.util.HasBlackBoxPath

class PhaseLockedLoop() extends BlackBox with HasBlackBoxResource {
  val io = IO (new Bundle {
    val clock_in = Input(Bool())
    val clock_out = Output(Bool())
    val reset = Input(Bool())
    val locked = Output(Bool())
  })

  addResource("vsrc/phase_locked_loop.v")
}
