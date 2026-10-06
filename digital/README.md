# digital

Circuits for [Digital](https://github.com/hneemann/Digital), Helmut Neemann's logic simulator: the 74HC595 and 74HC165 built from flip-flops and gates, each with its test cases embedded.

## Building the chips

1. Build each chip as its own circuit, `74HC595.dig` and `74HC165.dig`, with In/Out components labelled exactly as in the test vectors:
   - 595: `SER SRCLK RCLK SRCLR_n OE_n` → `QA … QH QHp`
   - 165: `SH_LD_n CLK CLK_INH SER A … H` → `QH QH_n`

   `_n` marks an active-low pin; `QHp` is QH'.
2. Flip-flops: Digital's D flip-flop, with asynchronous inputs enabled for the 595's shift register and all 165 stages. Its Set and Clr are active high, so invert them (a NOT gate, or the component's inverted-input option) to match the drawings in `diagrams/`.
3. Tri-state outputs of the 595: the Driver component, or its inverted-select variant driven by `OE_n` directly.
4. Add a Test component to each circuit, paste in the matching block of test vectors, and run the tests.
5. Once both pass, give each circuit the DIL shape in its settings and use it as a chip in a third circuit: chain two of each and drive LEDs and DIP switches, as on the breadboard.

## Test vectors

```sh
./test_vectors.py   # writes 74hc595-74hc165-tests.txt
```

They come from a behavioural model of each chip in `test_vectors.py`, not from the datasheets directly, so if a test fails, check the vector as well as the circuit.
