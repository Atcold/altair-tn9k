// The walking bit: one lit LED walks from QA to QH on a 74HC595, a step every half second.
// Each tick puts the next bit on SER, shifts it in, and latches: a 1 on one tick in eight.

module walk (
    input sys_clk,          // 27 MHz
    output reg ser = 0,
    output reg srclk = 0,
    output reg rclk = 0
);

parameter  TICK = 13_500_000;  // 0.5 s at 27 MHz; the testbench shortens it
localparam STEP = 27;          // 1 µs

reg [23:0] t = 0;              // time into this tick
reg [2:0]  k = 0;              // which tick of eight: a 1 goes in on tick 0

always @(posedge sys_clk) begin
    t <= (t == TICK - 1) ? 0 : t + 1;
    case (t)
        0:        ser <= (k == 0);
        STEP:     srclk <= 1;                       // shift
        2 * STEP: begin srclk <= 0; rclk <= 1; end  // latch
        3 * STEP: begin rclk <= 0; k <= k + 1; end
    endcase
end

endmodule
