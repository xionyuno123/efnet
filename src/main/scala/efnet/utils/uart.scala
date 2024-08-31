package efnet.utils

import chisel3._
import chisel3.util._
import ujson.False

/** UART RX
  *
  * @param width
  *   data width, from 5 to 8
  * @param parity
  *   0: no parity, 1: odd parity, 2: even parity
  * @param stop_bits
  *   number of stop bits, 1 or 2
  *
  * @io
  *   - clock: Baud rate clock, with one bit per symbol, common values include:
  *     9600,128000,etc
  *   - reset: reset signal, active high
  *   - data_in: user input data in parallel
  *   - data_valid: notify the UartTx module that the user data is ready to be
  *     sent (data_in is valid). It is important to note that UartTx utilizes a
  *     synchronous timing design, and the data_valid state should be maintained
  *     for at least one clock cycle.
  *   - tx: serial transmit signal for sending user data using the UART
  *     protocol.
  *   - tx_busy: notify the user module when user data has been transmitted,
  *     allowing the user to prepare the additional data. tx_busy is enabled
  *     before stop_bit is sent, so please select the appropriate stop_bits
  *     parameter.
  */
class UartTx(width: Int, parity: Int, stop_bits: Int) extends Module {
  require(width >= 5 && width <= 8, "Data width must between 5 and 8 inclusive")
  require(
    parity == 0 || parity == 1 || parity == 2,
    "The optional parity values are 0, 1 and 2, 0 for disable data parity, 1 for odd, and 2 for even"
  )
  require(stop_bits == 1 || stop_bits == 2, "The stop bit is either 1 or 2")

  val io = IO(new Bundle {
    val data_in = Input(UInt(width.W))
    val data_valid = Input(Bool())
    val tx = Output(Bool())
    val tx_busy = Output(Bool())
  })

  // UART data frame length
  val frame_len = width + 1 + parity + stop_bits

  // A data register used to store user input data
  val r_data_in = RegInit(0.U(width.W))
  val r_tx = RegInit(true.B)
  // A bit counter that tracks the number of data bits transmitted for the current frame.
  val r_bit_cnt = RegInit(0.U(log2Ceil(frame_len).W))
  val r_tx_busy = RegInit(false.B)
  val parity_gen = Module(new ParityGenerator(parity))

  // r_tx_busy transitions occur only at the beginning and end of a data frame.
  // The data frame starts when data_valid is valid and the r_bit_cnt counter
  // is 0. It ends when data_valid is valid and the r_bit_cnt counter reaches
  // frame_len - 2 (the last stop bit is ignored).
  when(io.data_valid && r_bit_cnt === 0.U) {
    r_tx_busy := true.B
  }.elsewhen(io.data_valid && r_bit_cnt === (frame_len - 2).U) {
    r_tx_busy := false.B
  }.otherwise({ r_tx_busy := r_tx_busy })

  // r_bit_cnt starts counting only when data_valid is valid; otherwise, it is
  // reset to 0. To prevent overflow, counting stops when r_bit_cnt reaches
  // frame_len - 1.
  when(io.data_valid && r_bit_cnt < (frame_len - 1).U) {
    r_bit_cnt := r_bit_cnt + 1.U
  }.elsewhen(io.data_valid) {
    r_bit_cnt := r_bit_cnt
  }.otherwise({ r_bit_cnt := 0.U })

  // Activate parity_gen.reset signal
  when(io.data_valid && r_bit_cnt === 0.U) {
    parity_gen.reset := true.B
  }.otherwise({ parity_gen.reset := false.B })
  parity_gen.clock := clock
  parity_gen.io.data := r_data_in(width - 1)

  when(io.data_valid && r_bit_cnt === 0.U) {
    r_data_in := io.data_in
    r_tx := false.B
  }.elsewhen(io.data_valid && r_bit_cnt <= (width).U) {
    r_tx := r_data_in(width - 1)
    r_data_in := Cat(r_data_in(width - 2, 0), 0.U)
  }.elsewhen(io.data_valid && (parity > 0).B && (r_bit_cnt <= (width + 1).U)) {
    r_tx := parity_gen.io.parity
  }.otherwise({ r_tx := true.B })

  io.tx := r_tx
  io.tx_busy := r_tx_busy
}

/** Parity bit generator
  *
  * The generator utilizes pipeline technology to compute the parity bit for the
  * input bit stream, requiring n + 2 clock cycles to process n bits of data.
  * Each individual data bit takes three clock cycles: one for writing the bit,
  * one for calculating the parity bit, and one for reading the parity bit.
  *
  * Additionally, the reset signal must be synchronized with the bit write
  * operation
  *
  * @param parity:
  *   0 disable, 1 odd parity, 2 even parity
  */
class ParityGenerator(parity: Int) extends Module {
  require(parity <= 2, "Parity must be 0, 1, or 2")
  val io = IO(new Bundle {
    val data = Input(Bool())
    val parity = Output(Bool())
  })

  if (parity == 0) {
    io.parity := false.B
  } else {
    val parity_reg = RegInit(false.B ^ io.data)
    parity_reg := io.data ^ parity_reg

    if (parity == 1) {
      io.parity := ~parity_reg
    } else {
      io.parity := parity_reg
    }
  }
}

/** UartRx Module
  *
  * @param width
  * @param parity
  * @param stop_bits
  * @param sample_factor:
  *
  * @io:
  *   - clock:
  *   - reset:
  *   - io_rx:
  *   - io_data_out:
  *   - io_data_rdy:
  */
class UartRx(width: Int, parity: Int, stop_bits: Int, sample_factor: Int)
    extends Module {
  require(width >= 5 && width <= 8, "Data width must between 5 and 8 inclusive")
  require(
    parity == 0 || parity == 1 || parity == 2,
    "The optional parity values are 0, 1 and 2, 0 for disable data parity, 1 for odd, and 2 for even"
  )
  require(stop_bits == 1 || stop_bits == 2, "The stop bit is either 1 or 2")

  val io = IO(new Bundle {
    val rx = Input(Bool())
    val data_out = Output(UInt(width.W))
    val data_rdy = Output(Bool())
  })
}
