#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib", "schemdraw"]
# ///
"""Build the schematic PDFs into ../docs/.

    ./build_pdfs.py          # light theme
    ./build_pdfs.py --dark   # dark theme, files suffixed -dark
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no windows: render straight to files

import schematic
import panel_sr
import chips

parser = argparse.ArgumentParser(description="Build the schematic PDFs into ../docs/.")
parser.add_argument("--dark", action="store_true", help="dark theme instead of light")
args = parser.parse_args()

out = Path(__file__).resolve().parent.parent / "docs"
out.mkdir(exist_ok=True)
suffix = "-dark" if args.dark else ""

for name, sheets, title in [
    ("altair-panel-schematic", panel_sr.SHEETS, "Altair 8800 replica, Tang Nano 9K: panel schematic"),
    ("74hc595-74hc165-internals", chips.SHEETS, "74HC595 and 74HC165 at flip-flop level"),
]:
    path = out / f"{name}{suffix}.pdf"
    schematic.save_pdf(path, sheets, title=title, dark=args.dark)
    print(path)
