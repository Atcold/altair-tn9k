#!/usr/bin/env -S uv run
"""Circuit figure for the Stage 0c write-up: a pushbutton clocking the 74HC595's SRCLK.

fig_circuit() draws the button input twice, pull-down only and with a 100 nF capacitor across
the pull-down. Run as a script to write it as SVG into ../docs/fig/. The waveforms the two
inputs give are simulated in debounce.ipynb.
"""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

from schematic import FS, T, VDD, GND, canvas, finish


def _button_input(d, x, cap):
    """Button from 3V3 to the SRCLK node; 10 kΩ to ground, and the capacitor beside it if cap."""
    d.add(VDD().at((x, 0)).label("3V3"))
    d.add(elm.Button().down().at((x, 0)).label("SW", loc="bottom"))
    node = d.add(elm.Dot())
    d.add(elm.Resistor().down().label("R  10 kΩ", fontsize=FS))
    d.add(GND())
    d.add(elm.Line().at(node.center).right(2.2).color(T.CLOCK))
    if cap:
        tap = d.add(elm.Dot().color(T.CLOCK))
        d.add(elm.Capacitor().down().label("C  100 nF", loc="bottom", fontsize=FS))
        d.add(GND())
        d.add(elm.Line().at(tap.center).right(1.6).color(T.CLOCK))
    else:
        d.add(elm.Line().right(1.6).color(T.CLOCK))
    d.add(elm.Dot(open=True).fill("#ffffff00").label("SRCLK (pin 11)", loc="right", fontsize=FS))


def fig_circuit():
    fig = plt.figure(figsize=(7.5, 3.2))
    for k, (title, cap) in enumerate([("Pull-down only", False), ("Capacitor across the pull-down", True)]):
        ax = canvas(fig, [0.02 + 0.5 * k, 0.02, 0.46, 0.86])
        ax.set_title(title, fontsize=FS + 1, color=T.FG)
        d = schemdraw.Drawing(canvas=ax, show=False)
        _button_input(d, 0, cap)
        finish(d, ax)
    return fig


if __name__ == "__main__":
    matplotlib.use("Agg")
    out = Path(__file__).resolve().parent.parent / "docs" / "fig"
    out.mkdir(parents=True, exist_ok=True)
    fig = fig_circuit()
    fig.savefig(out / "debounce-circuit.svg", transparent=True)  # the page shows through, as in the KiCad exports
    plt.close(fig)
    print(out / "debounce-circuit.svg")
