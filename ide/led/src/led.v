module led (
    input sys_clk,          // clock input - system clock signal
    input sys_rst_n,        // active-low reset input - resets module when pulled low
    output reg [5:0] led    // 6 LED output pins, defined as a 6-bit register
);

// 24-bit counter to create delay between LED rotations
reg [23:0] cnt;

// First always block: counter management
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        cnt <= 24'd0;                 // reset counter to 0 when reset is active (low)
    else if (cnt < 24'd13_499_999)    // count up to 13.5M to create a 0.5s delay at 27MHz
        cnt <= cnt + 1'b1;            // increment counter
    else
        cnt <= 24'd0;                 // reset counter when it reaches the maximum value
end

// Second always block: LED pattern control
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        led <= 6'b111110;                  // initialise LEDs to 111110
    else if (cnt == 24'd13_499_999)        // count up to 13.5M
        led[5:0] <= {led[4:0], led[5]};    // rotate LEDs to the left
    else
        led <= led;                        // maintain current LED state
end

endmodule
