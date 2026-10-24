#!/usr/bin/env -S uv run
"""Export a KiCad schematic as an SVG cropped to the drawing, for the write-ups.

    ./kicad_sheet.py ../kicad/74HC595-manual-test/74HC595-manual-test.kicad_sch ../docs/fig

kicad-cli exports the whole page, mostly empty. The page is rendered to a bitmap with
rsvg-convert, the bounding box of everything drawn is found there, and the SVG's viewBox,
width and height are narrowed to it, plus a margin.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from matplotlib.image import imread

PX_PER_MM = 8
MARGIN = 3  # mm


def export(sch, out):
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(["kicad-cli", "sch", "export", "svg", "--exclude-drawing-sheet",
                    "--no-background-color", "--output", str(out), str(sch)],
                   check=True, capture_output=True)
    svg = out / f"{sch.stem}.svg"
    text = svg.read_text()
    x0, y0, w, h = map(float, re.search(r'viewBox="([^"]+)"', text).group(1).split())

    with tempfile.NamedTemporaryFile(suffix=".png") as png:
        subprocess.run(["rsvg-convert", "-f", "png", "-w", str(round(w * PX_PER_MM)),
                        "-o", png.name, str(svg)], check=True)
        alpha = imread(png.name)[..., 3]
    rows, cols = np.nonzero(alpha)
    s = w / alpha.shape[1]  # mm per pixel
    left, right = x0 + cols.min() * s - MARGIN, x0 + (cols.max() + 1) * s + MARGIN
    top, bottom = y0 + rows.min() * s - MARGIN, y0 + (rows.max() + 1) * s + MARGIN

    box = f"{left:.4f} {top:.4f} {right - left:.4f} {bottom - top:.4f}"
    text = re.sub(r'viewBox="[^"]+"', f'viewBox="{box}"', text, count=1)
    text = re.sub(r'width="[^"]+"', f'width="{right - left:.4f}mm"', text, count=1)
    text = re.sub(r'height="[^"]+"', f'height="{bottom - top:.4f}mm"', text, count=1)
    svg.write_text(text)
    return svg


if __name__ == "__main__":
    print(export(Path(sys.argv[1]), Path(sys.argv[2])))
