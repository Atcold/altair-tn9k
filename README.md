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
  panel/      panel_io_sr.v, panel_io_mcp.v, spi_master.v, debounce.v
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
docs/         write-ups in LaTeX; built into docs/build/, figures in docs/fig/
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

### FPGA tools

Gowin EDA (Education edition) for the vendor flow. For the open-source flow, the [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build/releases), a nightly `.tgz` of about 0.5 GB, 2 GB unpacked: `darwin-arm64` on Apple silicon, `darwin-x64` on Intel (`uname -m` prints `arm64` or `x86_64`). Download the latest with the GitHub CLI, into the current folder:

```sh
gh release download -R YosysHQ/oss-cad-suite-build -p 'oss-cad-suite-darwin-arm64-*.tgz'
```

then unpack it:

```sh
tar -xzf oss-cad-suite-darwin-arm64-*.tgz -C ~/Applications
```

and put it on the `PATH`, in `~/.bashrc`, last, so tools you already have (Homebrew’s `dot`, say) keep priority over the suite’s copies:

```sh
export PATH="$PATH:$HOME/Applications/oss-cad-suite/bin"
```

The suite runs Apicula’s `gowin_pack` on its own Python, which lacks three libraries it uses for speed, and warns about each. Install them into that Python, after every new download of the suite:

```sh
~/Applications/oss-cad-suite/bin/tabbypy3 -m pip install numpy msgspec fastcrc
```

`make rtl` also needs netlistsvg, from Homebrew:

```sh
brew install netlistsvg
```

Then, in a new shell, check the tools and that the Mac sees the board, plugged in over USB:

```sh
yosys -V
nextpnr-himbaechel --version
openFPGALoader --detect
```

`--detect` should name the `GW1N(R)-9C`. If it finds no cable, try another USB cable: some carry power only.
