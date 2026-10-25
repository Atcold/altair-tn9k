# diagrams

Schematic drawings of the front panel and of the two shift-register chips, made with [schemdraw](https://schemdraw.readthedocs.io) and matplotlib.

## Files

- `schematics.ipynb`: shows every sheet, one per cell, in the dark theme, in build order.
- `chips.py`: the 74HC595 and 74HC165 at flip-flop level, with their function tables and pinouts. Build them in Digital first.
- `first_byte.py`: the first breadboard, one byte each way on both backends sharing one DIP switch: schematic, FPGA pins, parts and test.
- `panel_sr.py`: panel sheets for the shift-register backend: block diagram, carrier and connector, LED chain, switch chain, bit maps.
- `panel_mcp.py`: panel sheets for the SPI-expander backend: block diagram, carrier and connector, output expander, input expander, bit maps and start-up writes.
- `debounce.py`: the Stage 0c circuit figure, a button clocking SRCLK without and with a capacitor. `../docs/build.sh` runs it and writes it as SVG to `../docs/fig/`.
- `debounce.ipynb`: simulates the SRCLK voltage for a bouncy press and release, without and with the capacitor, and counts the rising edges; writes `../docs/data/debounce.dat`, which the Stage 0c chapter plots with pgfplots. The `.dat` is not committed: run the notebook before the first build, and again after changing the model.
- `kicad_sheet.py`: exports a KiCad schematic as SVG, cropped to the drawing, for the write-ups in `../docs/`.
- `schematic.py`: shared helpers: A3 page and title block, net tags, IC and flip-flop shapes, tables, themes, PDF output.
- `build_pdfs.py`: writes the PDFs, in the light theme by default, dark or black and white on request.

## Editing

Each sheet is a function, such as `panel_sr.sheet_leds()`, that draws one A3 page and returns the figure. Change it in the `.py` file and re-run its cell; `autoreload` picks up the change without restarting the kernel.

Parts and wires are placed by coordinates, so after a change, look at the sheet for overlaps.

## Building the PDFs

```sh
./build_pdfs.py          # light theme, in colour
./build_pdfs.py --dark   # dark theme
./build_pdfs.py --mono   # black and white, for black-and-white printers or e-ink readers
```

Either command writes four PDFs to `../docs/build/`:

- `74hc595-74hc165-internals.pdf`: the three chip sheets
- `altair-first-byte-schematic.pdf`: the first breadboard, two sheets
- `altair-panel-sr-schematic.pdf`: the five panel sheets, shift-register backend
- `altair-panel-mcp-schematic.pdf`: the five panel sheets, SPI-expander backend

With `--dark` or `--mono`, the file names end in `-dark` or `-mono`.

Colours mark the kind of net: red supply, blue ground, amber clocks, green shift-register signals, purple SPI signals, teal shared switch lines; on the chip internals, green data path and pink control lines.

## Limits

These are drawings, not a netlist. Nothing checks that the wires drawn match the notes or the datasheets. The KiCad schematics in `kicad/` are the ones to trust for building.
