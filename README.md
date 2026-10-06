# altair-tn9k

A replica of the MITS Altair 8800 front panel driven by a Sipeed Tang Nano 9K FPGA, which implements the 8080 CPU, memory, I/O and panel logic.

## Panel backends

The 36 LEDs and 32 switch inputs reach the FPGA through one of two expanders. Both expose the same `panel_io` ports (`led[35:0]`, `sw[31:0]`), so the rest of the design is unaware of which one is wired.

| Backend | Expander | Chips | FPGA pins |
|---|---|---|---|
| `sr` | shift registers | 5× 74HC595 (out), 4× 74HC165 (in) | 6 |
| `mcp` | SPI I/O expanders | 5× MCP23S17 | 4 |

`sr` stands for shift register: 74 is the 7400 logic family, HC is high-speed CMOS, 595 is the 8-bit serial-in parallel-out register with output latch, and 165 the 8-bit parallel-in serial-out one. `mcp` is the prefix of Microchip’s part numbers (MCP23S17: 23 for the I/O-expander family, S for SPI, 17 for the 16-bit version).

Select one at build time with `make PANEL=sr` or `make PANEL=mcp`.

## Layout

```
rtl/          vendor-neutral Verilog
  panel/      panel_io_sr.v, panel_io_mcp.v, spi_master.v, debounce.v, pwm.v
  cpu/        8080 core
  altair/     memory map, 88-SIO, panel state machine
gowin/        Gowin primitives: PLL, PSRAM wrappers
constraints/  tangnano9k_sr.cst, tangnano9k_mcp.cst
sim/          Verilog testbenches
digital/      Digital circuits (.dig), test cases embedded
kicad/        schematics, one KiCad project per backend
  panel-sr/
  panel-mcp/
diagrams/     schemdraw notebooks
docs/         rendered figures and write-ups
ide/          Gowin EDA project
Makefile      open-source flow (Yosys, nextpnr-himbaechel, Apicula, openFPGALoader)
```

## Setup

Run once after cloning:

```sh
uv sync
uv tool install nbstripout
nbstripout --install --attributes .gitattributes
```
