#!/usr/bin/env -S uv run
"""Build the schematic PDFs into ../docs/."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no windows: render straight to files

import schematic
import chips
import first_byte
import panel_sr
import panel_mcp

parser = argparse.ArgumentParser(description="Build the schematic PDFs into ../docs/.")
theme = parser.add_mutually_exclusive_group()
theme.add_argument("--dark", dest="theme", action="store_const", const="dark",
                   help="dark theme instead of light")
theme.add_argument("--mono", dest="theme", action="store_const", const="mono",
                   help="black and white, for black-and-white printers or e-ink readers")
args = parser.parse_args()
args.theme = args.theme or "light"

out = Path(__file__).resolve().parent.parent / "docs"
out.mkdir(exist_ok=True)
suffix = "" if args.theme == "light" else f"-{args.theme}"

for name, sheets, title in [
    ("74hc595-74hc165-internals", chips.SHEETS,
     "74HC595 and 74HC165 at flip-flop level"),
    ("altair-first-byte-schematic", first_byte.SHEETS,
     "Altair 8800 replica, Tang Nano 9K: first byte, both backends"),
    ("altair-panel-sr-schematic", panel_sr.SHEETS,
     "Altair 8800 replica, Tang Nano 9K: panel schematic, shift registers"),
    ("altair-panel-mcp-schematic", panel_mcp.SHEETS,
     "Altair 8800 replica, Tang Nano 9K: panel schematic, SPI expanders"),
]:
    path = out / f"{name}{suffix}.pdf"
    schematic.save_pdf(path, sheets, title=title, theme=args.theme)
    print(path)
