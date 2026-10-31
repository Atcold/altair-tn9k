#!/usr/bin/env -S uv run
"""Give every constant in a Yosys netlist its own driver, so netlistsvg draws each next to its use.

    rtl_ties.py build/led-rtl.json

netlistsvg turns constant bits into constant nodes, but merges identical ones: every one-bit 1
in the design becomes one node, wired across the drawing to each place that uses it. Here each
run of constant bits on a cell's input, or on an output port, becomes a cell of its own, type
$tie, which the skin draws like netlistsvg's constants, labelled by its value attribute: in
binary up to 3 bits, as netlistsvg does, and in decimal above, as rtl_colour.py writes them.
The JSON is rewritten in place.
"""
import json
import sys
from pathlib import Path


def label(bits):
    """Value of a run of constant bits, which Yosys lists lowest first."""
    msb_first = "".join(reversed(bits))
    return msb_first if len(bits) <= 3 else str(int(msb_first, 2))


def tie(module, bits, fresh):
    """Replace the constant runs in bits with new nets, each driven by a new $tie cell."""
    out, run = [], []

    def flush():
        if run:
            nets = [next(fresh) for _ in run]
            name = f"$tie${len(module['cells'])}"
            module["cells"][name] = {
                "type": "$tie",
                "attributes": {"value": label(run)},
                "port_directions": {"Y": "output"},
                "connections": {"Y": nets},
            }
            out.extend(nets)
            run.clear()

    for b in bits:
        if b in ("0", "1"):
            run.append(b)
        else:
            flush()
            out.append(b)
    flush()
    return out


def main():
    path = Path(sys.argv[1])
    netlist = json.loads(path.read_text())
    for module in netlist["modules"].values():
        used = [b for c in module["cells"].values() for bits in c["connections"].values() for b in bits]
        used += [b for p in module["ports"].values() for b in p["bits"]]
        fresh = iter(range(max([b for b in used if isinstance(b, int)], default=1) + 1, 1 << 30))
        for cell in list(module["cells"].values()):
            dirs = cell["port_directions"]
            for port, bits in cell["connections"].items():
                if dirs[port] == "input":
                    cell["connections"][port] = tie(module, bits, fresh)
        for port in module["ports"].values():
            if port["direction"] == "output":
                port["bits"] = tie(module, port["bits"], fresh)
    path.write_text(json.dumps(netlist, indent=2))


if __name__ == "__main__":
    main()
