// Testbench for hello: a UART receiver on tx prints what it decodes, and busy's timing is
// measured, in cycles of sys_clk.
//
//   iverilog -g2012 -o build/hello_tb sim/hello_tb.v rtl/hello/hello.v
//   vvp -n build/hello_tb

`timescale 1ns / 1ps

module hello_tb;

localparam GAP  = 1000;  // cycles of rest: 37 µs instead of 100 ms
localparam BAUD = 234;

reg sys_clk = 0;
always #18.5 sys_clk = ~sys_clk;  // 27 MHz: a cycle every 37 ns

wire tx, tx_probe, busy;
hello #(.GAP(GAP)) dut (.sys_clk(sys_clk), .tx(tx), .tx_probe(tx_probe), .busy(busy));

integer cycle = 0;
always @(posedge sys_clk) cycle <= cycle + 1;

// The receiver: from a start bit's falling edge, half a bit to its middle, then one sample per
// bit, eight data bits lowest first, and the stop bit, which must be high.
integer k;
reg [7:0] c;
initial forever begin
    @(negedge tx);
    repeat (BAUD / 2) @(posedge sys_clk);
    for (k = 0; k < 8; k = k + 1) begin
        repeat (BAUD) @(posedge sys_clk);
        c[k] = tx;
    end
    repeat (BAUD) @(posedge sys_clk);
    if (tx !== 1) $write("[no stop bit]");
    if (c == 8'h0d) $write("\\r"); else if (c == 8'h0a) $write("\\n"); else $write("%s", c);
end

integer up, down, again;
initial begin
    $write("decoded: ");
    @(posedge busy) up = cycle;
    @(negedge busy) down = cycle;
    @(posedge busy) again = cycle;
    $display("");
    $display("busy high for %0d cycles", down - up);
    $display("busy low for %0d cycles, the rest", again - down);
    $finish;
end

endmodule
