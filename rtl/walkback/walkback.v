// The walk backwards: one lit LED walks from QH to QA on a 74HC595, a step every half second.
// Shifting moves a bit only towards QH, so each tick writes the whole byte, then latches it.

module walkback (
    input sys_clk,          // 27 MHz
    output reg ser = 0,
    output reg srclk = 0,
    output reg rclk = 0
);

parameter  TICK = 13_500_000;  // 0.5 s at 27 MHz; the testbench shortens it
localparam STEP = 27;          // 1 µs

reg [23:0] t = 0;              // time into this tick
reg [4:0]  c = 0;              // time into this step
reg [4:0]  n = 0;              // which step: 0-15 shift the eight bits, 16-17 latch, then wait
reg [2:0]  p = 7;              // the lit LED: 7 is QH, 0 is QA

always @(posedge sys_clk) begin
    t <= (t == TICK - 1) ? 0 : t + 1;
    c <= (c == STEP - 1) ? 0 : c + 1;
    if (t == TICK - 1)
        n <= 0;
    else if (c == STEP - 1 && n != 18)
        n <= n + 1;

    if (c == 0)
        case (n)
            16:      begin srclk <= 0; rclk <= 1; end  // latch
            17:      begin rclk <= 0; p <= p - 1; end
            default: if (n < 16) begin
                if (n[0] == 0) begin                    // the next bit, QH's first
                    srclk <= 0;
                    ser <= (n[3:1] == 7 - p);
                end else
                    srclk <= 1;                         // shift
            end
        endcase
end

endmodule
