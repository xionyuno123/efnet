package efnet.utils

import chisel3._
import chisel3.util.log2Ceil

/** clock divider
  *
  * @param cnt
  *   divisor
  */
class ClockDivider(cnt: Int) extends RawModule {
  val io = IO(new Bundle {
    // input clock
    val clock_in = Input(Clock())
    // reset for the above clock
    val reset = Input(Bool())
    // clock divided by cnt
    val clock_out = Output(Clock())
  })

  require(cnt % 2 == 0, "Must divide by an even factor")

  withClockAndReset(clock = io.clock_in, reset = io.reset) {
    val max: Int = cnt / 2;
    val counter = RegInit(0.U(log2Ceil(max).W))

    counter := counter + 1.U // the counter always increments

    // Every second cycle, toggle the new divided down clock
    val dividedDownClock = RegInit(false.B)

    when(counter === (max - 1).U) {
      dividedDownClock := ~dividedDownClock
      counter := 0.U
    }

    io.clock_out := dividedDownClock.asClock
  }
}
