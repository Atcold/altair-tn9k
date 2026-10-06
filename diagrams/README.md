# diagrams

Schematic drawings of the front panel and of the two shift-register chips, made with [schemdraw](https://schemdraw.readthedocs.io) and matplotlib.

## Files

| File | Contents |
|---|---|
| `schematics.ipynb` | Shows every sheet, one per cell, in the dark theme |
| `panel_sr.py` | Panel sheets, shift-register backend: block diagram, carrier and connector, LED chain, switch chain, bit maps |
| `chips.py` | 74HC595 and 74HC165 at flip-flop level, their function tables and pinouts |
| `schematic.py` | Shared helpers: A3 page and title block, net tags, IC and flip-flop shapes, tables, themes, PDF output |
| `build_pdfs.py` | Writes the light-theme PDFs |

## Editing

Each sheet is a function, such as `panel_sr.sheet_leds()`, that draws one A3 page and returns the figure. Change it in the `.py` file and re-run its cell; `autoreload` picks up the change without restarting the kernel.

Parts and wires are placed by coordinates, so after a change, look at the sheet for overlaps.

## Building the PDFs

```sh
./build_pdfs.py          # light theme
./build_pdfs.py --dark   # dark theme
```

Either command writes two PDFs to `../docs/`:

- `altair-panel-schematic.pdf`: the five panel sheets
- `74hc595-74hc165-internals.pdf`: the three chip sheets

With `--dark`, the files end in `-dark` instead.

## Limits

These are drawings, not a netlist. Nothing checks that the wires drawn match the notes or the datasheets. The KiCad schematics in `kicad/` are the ones to trust for building.
