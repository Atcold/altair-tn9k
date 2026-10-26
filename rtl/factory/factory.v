// What the board runs out of the box: all six LEDs flashing together, held while S1 is pressed.
// Sipeed's factory bitstream can't be read back from the chip, so this stands in for it: write it
// to the flash to put the board back as it came.

module factory (
    input sys_clk,              // 27 MHz
    input s1,                   // S1: low while pressed
    output reg [5:0] led = 0    // low lights an LED: all on at power-up
);

localparam TICK = 13_500_000;   // 0.5 s at 27 MHz

reg [23:0] cnt = 0;

always @(posedge sys_clk)
    if (s1)                         // S1 not pressed (high): count, and flip every 0.5 s
        if (cnt == TICK - 1) begin
            cnt <= 0;
            led <= ~led;            // all six at once
        end else
            cnt <= cnt + 1'b1;
    // S1 pressed: nothing changes, so the LEDs hold their state

endmodule
