#!/usr/bin/env -S uv run
"""Colour netlistsvg's RTL drawing by register, in the schematics' colours, and write constants in decimal.

    rtl_colour.py build/led-rtl.json docs/fig/led-rtl.svg

netlistsvg tags each shape with the cell it belongs to (class "cell_<name>") and each wire with
the bits it carries (class "net_<bit>,<bit>,..."), the names and bits of Yosys's JSON netlist.
So the colours come from the netlist: every register gets a colour, in the order the Verilog
declares it, and every cell takes the colour of the one register its output leads to (through
other cells, up to that register's D). A cell that leads to more than one, like a constant two
comparators share, stays black. Each wire takes the colour of the cell driving it. An input
takes the clock's colour if it reaches a register's clock, the reset's if a reset, and a third
otherwise. Constants stay black, boxes and wires: values, not signals. The SVG is rewritten
in place.
"""
import json
import re
import sys
from pathlib import Path

from schematic import T

# Registers take these in the order the Verilog declares them; the rest are black. Hues far
# apart, red against blue first, since thin lines at figure size blur close ones together.
REGISTERS = [T.LED, T.GROUND, T.SHARED, T.RIBBON]
CLOCK, RESET, INPUT = T.CLOCK, T.MCP, T.SHARED  # inputs: by what they drive
TINT = {T.LED: "#fdecea", T.GROUND: "#e8f0fb", T.SHARED: "#e0f4f6", T.RIBBON: "#f6ecdc",
        T.CLOCK: "#fff6e0", T.MCP: "#f3e8fb"}  # box fills
WIDTH = 1  # coloured lines, as the skin's black ones


def is_register(cell):
    """Any of Yosys's flip-flops: $dff, $adff (async reset), $dffe (enable), $sdff, ..."""
    return "dff" in cell["type"]


def declared(net):
    """Line of the Verilog where a net is declared, from Yosys's src attribute (file:line.col)."""
    m = re.search(r":(\d+)", net.get("attributes", {}).get("src", ""))
    return int(m.group(1)) if m else 0


def groups(module):
    """{cell or port name: colour}, and {bit: colour} for the wires."""
    cells, ports, names = module["cells"], module["ports"], module["netnames"]

    # Each register by the net on its Q, in the order of declaration.
    regs = [n for n, c in cells.items() if is_register(c)]
    q_net = {}
    for r in regs:
        q = cells[r]["connections"]["Q"]
        q_net[r] = next((n for n, net in names.items() if net["bits"] == q and not n.startswith("$")), r)
    order = sorted(regs, key=lambda r: declared(names.get(q_net[r], {})))

    def outputs(cell):
        dirs = cell["port_directions"]
        return [b for p, bits in cell["connections"].items() if dirs[p] == "output" for b in bits]

    def inputs(cell):
        dirs = cell["port_directions"]
        return {p: bits for p, bits in cell["connections"].items() if dirs[p] == "input"}

    readers = {}  # bit -> [(cell name, port)]
    for name, cell in cells.items():
        for port, bits in inputs(cell).items():
            for b in bits:
                readers.setdefault(b, []).append((name, port))

    colour = {r: REGISTERS[i] if i < len(REGISTERS) else T.FG for i, r in enumerate(order)}

    def reached(name, seen):
        """Colours of the registers whose D this cell's output leads to."""
        found = set()
        for b in outputs(cells[name]):
            for reader, port in readers.get(b, []):
                if is_register(cells[reader]):
                    if port == "D":
                        found.add(colour[reader])
                elif reader not in seen:
                    seen.add(reader)
                    found |= reached(reader, seen)
        return found

    for name, cell in cells.items():
        if not is_register(cell):
            r = reached(name, {name})
            colour[name] = r.pop() if len(r) == 1 else T.FG

    bit_colour = {}
    for name, cell in cells.items():
        for b in outputs(cell):
            bit_colour[b] = colour[name]

    def drives(bits):
        """Ports of the registers these bits reach directly."""
        return {p for b in bits for reader, p in readers.get(b, []) if is_register(cells[reader])}

    for name, port in ports.items():
        if port["direction"] == "input":
            to = drives(port["bits"])
            c = CLOCK if "CLK" in to else RESET if to & {"ARST", "SRST", "R"} else INPUT
            colour[name] = c
            for b in port["bits"]:
                bit_colour[b] = c
        else:
            colour[name] = bit_colour.get(port["bits"][0], T.FG)
    return colour, bit_colour


def recolour(svg, colour, bit_colour):
    def style(c, fill=False):
        tint = f";fill:{TINT[c]}" if fill and c in TINT else ""
        return f' style="stroke:{c};stroke-width:{WIDTH}{tint}"'

    def cell(m):
        name = m.group(3)
        c = colour.get(name)
        closed = m.group(2) in ("rect", "circle") or (m.group(2) == "path" and "Z" in m.group(0))
        return m.group(0) + (style(c, closed) if c and c != T.FG else "")

    def net(m):
        first = m.group(2).split(",")[0]
        c = bit_colour.get(int(first)) if first.isdigit() else None
        return m.group(0) + (style(c) if c and c != T.FG else "")

    svg = re.sub(r'(<(path|rect|line|circle|polygon)[^>]*?class="cell_([^"]+)")', cell, svg)
    svg = re.sub(r'(<line[^>]*?class="net_([^"]+)")', net, svg)

    def junction(m):  # the dot where a wire branches: filled, not stroked
        before, after, bits = m.groups()
        first = bits.split(",")[0]
        c = bit_colour.get(int(first)) if first.isdigit() else None
        return f"{before}fill:{c or '#000'}{after}"

    svg = re.sub(r'(<circle[^>]*?style=")fill:#000("[^>]*?class="net_([^"]+)")', junction, svg)
    # Constants in decimal: netlistsvg writes multi-bit ones in hex, 0x...
    return re.sub(r">0x([0-9a-fA-F]+)<", lambda m: f">{int(m.group(1), 16)}<", svg)


def main():
    netlist, svg_path = Path(sys.argv[1]), Path(sys.argv[2])
    module = next(iter(json.loads(netlist.read_text())["modules"].values()))
    colour, bit_colour = groups(module)
    svg_path.write_text(recolour(svg_path.read_text(), colour, bit_colour))


if __name__ == "__main__":
    main()
