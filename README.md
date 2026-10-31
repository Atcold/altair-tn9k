# altair-tn9k

A replica of the MITS Altair 8800 front panel driven by a Sipeed Tang Nano 9K FPGA, which implements the 8080 CPU, memory, I/O and panel logic.

## Panel interface

The 36 LEDs and 32 switch inputs reach the FPGA through shift registers, 5× 74HC595 out and 4× 74HC165 in, on 6 FPGA pins, behind one `panel_io` module (`led[35:0]`, `sw[31:0]`). 74 is the 7400 logic family, HC is high-speed CMOS, 595 is the 8-bit serial-in parallel-out register with output latch, and 165 the 8-bit parallel-in serial-out one.

## Layout

```
rtl/          vendor-neutral Verilog
  panel/      panel_io.v, debounce.v
  cpu/        8080 core
  altair/     memory map, 88-SIO, panel state machine
gowin/        Gowin primitives: PLL, PSRAM wrappers
sim/          Verilog testbenches
digital/      Digital circuits (.dig), test cases embedded
kicad/        schematics, one KiCad project per circuit
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

### Logic analyser

[Logic 2](https://www.saleae.com/downloads), Saleae's software, reads the HiLetgo analyser, a clone of Saleae's Logic:

```sh
brew install --cask saleae-logic
```

If Logic 2 doesn't see the analyser, [PulseView](https://sigrok.org/wiki/Downloads), from the sigrok project, with its `fx2lafw` driver, does.

### RTL drawings

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
