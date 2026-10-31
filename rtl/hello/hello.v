// Hello world over a UART: the 13 characters of "Hello world\r\n" as 8N1 frames at 115200 baud,
// then 100 ms of rest, forever. busy is high for the whole message, as the analyser's trigger.
// A state machine in three parts, state register, next state logic, and output logic, then the
// counters and the frame that the states drive.

module hello (
    input  sys_clk,         // 27 MHz
    output tx,              // to the USB-serial bridge
    output tx_probe,        // the same, for CH0
    output busy             // high during the message, for CH1
);

parameter  GAP  = 2_700_000;                          // 100 ms; the testbench shortens it
localparam BAUD = 234;                                // 27 MHz / 115200 = 234.375
localparam N    = 13;                                 // characters
localparam [8*N-1:0] MSG = {"Hello world", 8'h0d, 8'h0a};  // \r\n: Verilog has no \r

localparam REST = 0, LOAD = 1, SEND = 2;              // the three states
reg [1:0] state = REST, nextstate;

// The counters and the frame.
reg [21:0] rest_count = 0;        // cycles into the rest
reg [8:0]  bit_count  = 0;        // cycles into this bit
reg [3:0]  bits_left  = 0;        // bits of this frame still to send
reg [3:0]  char_index = 0;        // the next character
reg [9:0]  frame      = 10'h3ff;  // bits to send, lowest first; all 1: the line rests

// counter outputs: the conditions on the controller's arrows, combinational logic
wire rest_done  = (rest_count == GAP - 1);
wire all_sent   = (char_index == N);
wire bit_done   = (bit_count == BAUD - 1);
wire frame_done = bit_done && (bits_left == 1);

// state register
always @(posedge sys_clk)
    state <= nextstate;

// next state logic
always @(*)
    case (state)
        REST:    nextstate = rest_done  ? LOAD : REST;
        LOAD:    nextstate = all_sent   ? REST : SEND;
        SEND:    nextstate = frame_done ? LOAD : SEND;
        default: nextstate = REST;
    endcase

// output logic
assign busy     = (state != REST);
assign tx       = frame[0];
assign tx_probe = frame[0];

// counters and frame: what each state does to them, at every clock edge
always @(posedge sys_clk)
    case (state)
        REST: begin                             // count the rest; the message starts at 0
            rest_count <= rest_done ? 0 : rest_count + 1;
            char_index <= 0;
        end
        LOAD:                                   // the next character's frame
            if (!all_sent) begin
                frame      <= {1'b1, MSG[8*(N-1-char_index) +: 8], 1'b0};  // stop, data, start
                bits_left  <= 10;
                bit_count  <= 0;
                char_index <= char_index + 1;
            end
        SEND:                                   // one bit every BAUD cycles
            if (bit_done) begin
                bit_count <= 0;
                frame     <= {1'b1, frame[9:1]};  // shift right; a 1 comes in at the top
                bits_left <= bits_left - 1;
            end else
                bit_count <= bit_count + 1;
        default: ;
    endcase

endmodule
