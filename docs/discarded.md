# Discarded ideas

Ideas that were once in the plan, kept here with the reason they were dropped. The rest of the repo describes only what is being built.

## SPI I/O expanders (MCP23S17) as a second panel backend

Dropped on 2026-10-31. The chips cost more than the whole shift-register parts order, and they teach nothing about the panel that the shift registers don't: the same outputs and inputs, behind an SPI master and a register-level init sequence that add work without adding to the project.

The plan was a second panel backend beside the shift registers, behind the same `panel_io` ports (`led[35:0]`, `sw[31:0]`), selected with `make PANEL=sr|mcp`.

- 5× MCP23S17 (16 GPIO each, 80 pins, 68 used), all on one CS, told apart by hardware address pins A2–A0.
- FPGA pins: SCK, MOSI, MISO, CS, so 4.
- Internal pull-ups (GPPU register) on the switch inputs, so no resistor networks. RESET (pin 18) pulled up to 3V3 through one 10 kΩ resistor shared by all five.
- Hardware addressing is off until IOCON.HAEN is set: at power-up all five chips answer to address 0, so the first IOCON write reaches them all at once.
- Unverified: some MCP23S17 silicon may decode A2 even before HAEN is set, so U5 (address 100) would miss that first write. Sending it to address 100 as well covers both cases; check Microchip’s errata sheet.
- Refresh: 3 LED writes + 2 switch reads ≈ 160 SPI bits ≈ 16 µs at 10 MHz.

Its breadboard stage, one byte over SPI, after reading switches with the 74HC165:

- One MCP23S17 next to the shift registers: port A to its own 8 LEDs, port B to the same DIP switch lines as the 165.
- Verilog SPI master (mode 0, MSB first), then the init sequence: IOCON (HAEN), IODIRA = 0x00 (outputs), IODIRB = 0xFF (inputs), GPPUB = 0xFF (pull-ups).
- Loop: read GPIOB, write it to OLATA, with the same debounce and mirror top level as the 165.
- Done when: with `PANEL=mcp`, flipping a switch toggles its LED, and `PANEL=sr` still drives the 595’s LEDs from the same switches.

Parts it needed: 5 MCP23S17-E/SP (DIP-28), 5 DIP-28 sockets, one 10 kΩ RESET pull-up, three 33 Ω series resistors on SCK, MOSI, and CS_n.

The drawings were `diagrams/panel_mcp.py` (five panel sheets) and the U3 half of `diagrams/first_byte.py`; both are in the repo’s history up to commit `08c265e`.
