// Testbench for both walks: each drives its own model of a 74HC595, and the LEDs are printed
// after every tick. It also measures the gaps the datasheet asks for, in cycles of sys_clk.
//
//   iverilog -g2012 -o build/walk_tb sim/walk_tb.v rtl/walk/walk.v rtl/walkback/walkback.v
//   vvp -n build/walk_tb

`timescale 1ns / 1ps

module walk_tb;

localparam TICK = 1000;  // cycles per tick: 37 µs instead of half a second

reg sys_clk = 0;
always #18.5 sys_clk = ~sys_clk;  // 27 MHz: a cycle every 37 ns

wire f_ser, f_srclk, f_rclk, b_ser, b_srclk, b_rclk;
walk     #(.TICK(TICK)) forward  (.sys_clk(sys_clk),
                                   .ser(f_ser), .srclk(f_srclk), .rclk(f_rclk));
walkback #(.TICK(TICK)) backward (.sys_clk(sys_clk),
                                   .ser(b_ser), .srclk(b_srclk), .rclk(b_rclk));

// The 595: SRCLK's rising edge shifts SER in at QA's end, RCLK's copies the shift register
// to the outputs. Bit 0 is QA. Both start with a made-up power-up pattern.
reg [7:0] f_shift = 8'b10100101, f_q = 8'b10100101;
reg [7:0] b_shift = 8'b00111100, b_q = 8'b00111100;
always @(posedge f_srclk) f_shift <= {f_shift[6:0], f_ser};
always @(posedge f_rclk)  f_q <= f_shift;
always @(posedge b_srclk) b_shift <= {b_shift[6:0], b_ser};
always @(posedge b_rclk)  b_q <= b_shift;

// The datasheet's minimums, checked on both walks: see gaps below.
integer cycle = 0;
always @(posedge sys_clk) cycle <= cycle + 1;
gaps f_gaps (.cycle(cycle), .ser(f_ser), .srclk(f_srclk), .rclk(f_rclk));
gaps b_gaps (.cycle(cycle), .ser(b_ser), .srclk(b_srclk), .rclk(b_rclk));

// QA to QH, left to right: * lit, . dark.
function [8 * 8 - 1:0] leds(input [7:0] q);
    integer i;
    for (i = 0; i < 8; i = i + 1) leds[8 * (7 - i) +: 8] = q[i] ? "*" : ".";
endfunction

integer tick;
initial begin
    $display("tick  forward   backward");
    $display("      QA....QH  QA....QH");
    $display("  -   %s  %s   (power-up)", leds(f_q), leds(b_q));
    for (tick = 0; tick < 16; tick = tick + 1) begin
        repeat (TICK) @(posedge sys_clk);
        $display("%3d   %s  %s", tick, leds(f_q), leds(b_q));
    end
    $display("%-26s%14s%15s%13s", "shortest gaps, in cycles",
             "SER to SRCLK", "SRCLK to RCLK", "high or low");
    $display("%-26s%14d%15d%13d", "  needed (rows 1-3)", 4, 3, 3);
    $display("%-26s%14d%15d%13d", "  forward", f_gaps.setup, f_gaps.latch, f_gaps.pulse);
    $display("%-26s%14d%15d%13d", "  backward", b_gaps.setup, b_gaps.latch, b_gaps.pulse);
    $finish;
end

endmodule

// The shortest of each gap the datasheet's table limits, in cycles: SER steady before SRCLK
// rises (row 1), SRCLK rising before RCLK rises (row 2), SRCLK or RCLK high, or low (row 3).
// Edges start out far in the past, so the first change of each line is not taken for a pulse.
module gaps (input integer cycle, input ser, input srclk, input rclk);

integer ser_set = -1000000, srclk_rose = -1000000, srclk_edge = -1000000, rclk_edge = -1000000;
integer setup = 1000000, latch = 1000000, pulse = 1000000;

always @(ser) ser_set = cycle;
always @(posedge srclk) begin
    if (cycle - ser_set < setup) setup = cycle - ser_set;
    srclk_rose = cycle;
end
always @(posedge rclk) if (cycle - srclk_rose < latch) latch = cycle - srclk_rose;
always @(srclk) if ($time > 0) begin
    if (cycle - srclk_edge < pulse) pulse = cycle - srclk_edge;
    srclk_edge = cycle;
end
always @(rclk) if ($time > 0) begin
    if (cycle - rclk_edge < pulse) pulse = cycle - rclk_edge;
    rclk_edge = cycle;
end

endmodule
