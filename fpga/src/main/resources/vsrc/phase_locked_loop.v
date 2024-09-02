`timescale 1ns/1ps

module phase_locked_loop (
  output  clock_out,
  input   reset,
  output  locked,
  input   clock_in
);

clk_wiz_ppl_0 inst(
  .clock_out(clock_out),
  .reset(reset),
  .locked(locked),
  .clock_in(clock_in)
);

endmodule