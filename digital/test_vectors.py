#!/usr/bin/env -S uv run
"""Test vectors for the 74HC595 and 74HC165 Digital circuits, from a behavioural model of each chip."""
from pathlib import Path


def test_vectors():
    """Digital test cases for both chips, from a behavioural model of each."""
    def row(v):
        return " ".join(str(x) for x in v)

    L = []
    # ---------------- 74HC595
    L += ["# ---------- 74HC595 ----------",
          "# Paste into a Test component in s2p-74HC595.dig. Rows run top to bottom;",
          "# a clock edge happens where a clock column goes from 0 to 1. X = don't care, Z = high impedance.",
          row(["~SRCLR", "SER", "SRCLK", "RCLK", "~OE", "QA", "QB", "QC", "QD", "QE", "QF", "QG", "QH", "QH'"])]
    s = dict(sr=[0] * 8, store=None, sck=0, rck=0)

    def s595(clr, ser, sck, rck, oe, note=None):
        if clr == 0:
            s["sr"] = [0] * 8
        elif sck and not s["sck"]:
            s["sr"] = [ser] + s["sr"][:7]
        if rck and not s["rck"]:
            s["store"] = s["sr"][:]
        s.update(sck=sck, rck=rck)
        out = ["Z"] * 8 if oe else (["X"] * 8 if s["store"] is None else s["store"][:])
        if note:
            L.append("# " + note)
        L.append(row([clr, ser, sck, rck, oe] + out + [s["sr"][7]]))

    s595(0, 0, 0, 0, 0, "clear the shift register (storage still unknown)")
    s595(0, 0, 0, 1, 0, "RCLK edge: copy the cleared register to the outputs")
    s595(1, 0, 0, 0, 0)
    for k, b in enumerate([1, 0, 1, 1, 0, 0, 0, 1]):
        s595(1, b, 0, 0, 0, "shift in 1,0,1,1,0,0,0,1; outputs must not change yet" if k == 0 else None)
        s595(1, b, 1, 0, 0)
    s595(1, 0, 0, 0, 0)
    s595(1, 0, 0, 1, 0, "RCLK edge: pattern appears at once (QA = last bit in, QH = first)")
    s595(1, 0, 0, 0, 0)
    s595(1, 0, 0, 0, 1, "~OE high: outputs float, QH' still driven")
    s595(1, 0, 0, 0, 0, "~OE low again")
    s595(0, 0, 0, 0, 0, "clear: QHp drops at once, outputs keep the old pattern")
    s595(1, 0, 0, 0, 0)
    s595(1, 0, 0, 1, 0, "RCLK edge: the cleared register reaches the outputs")
    s595(1, 0, 0, 0, 0)

    # ---------------- 74HC165
    L += ["", "# ---------- 74HC165 ----------",
          "# Paste into a Test component in p2s-74HC165.dig.",
          row(["SH/~LD", "CLK", "CLK_INH", "SER", "A", "B", "C", "D", "E", "F", "G", "H", "QH", "~QH"])]
    q = dict(st=None, clk=0, inh=0)

    def s165(ld, clk, inh, ser, ins, note=None):
        if ld == 0:
            q["st"] = ins[:]
        elif (clk | inh) and not (q["clk"] | q["inh"]):
            q["st"] = [ser] + q["st"][:7]
        q.update(clk=clk, inh=inh)
        if note:
            L.append("# " + note)
        L.append(row([ld, clk, inh, ser] + ins + [q["st"][7], 1 - q["st"][7]]))

    pat, other = [1, 1, 0, 1, 0, 0, 1, 0], [0, 0, 1, 1, 1, 0, 0, 1]
    s165(0, 0, 0, 0, pat, "parallel load A..H = 1,1,0,1,0,0,1,0: QH shows H straight away")
    s165(1, 0, 0, 0, other, "load released: changing the inputs now has no effect")
    for k in range(7):
        s165(1, 1, 0, 0, other, "seven clocks: QH shows G, F, E, D, C, B, A in turn" if k == 0 else None)
        s165(1, 0, 0, 0, other)
    s165(0, 0, 0, 0, pat, "reload, then shift 1s in through SER")
    s165(1, 0, 0, 1, pat)
    for k in range(8):
        s165(1, 1, 0, 1, pat); s165(1, 0, 0, 1, pat)
    s165(1, 1, 0, 0, pat, "raise CLK_INH while CLK is high, then pulse CLK: no shift")
    s165(1, 1, 1, 0, pat)
    s165(1, 0, 1, 0, pat)
    s165(1, 1, 1, 0, pat)
    s165(1, 0, 1, 0, pat)
    s165(1, 1, 1, 0, pat, "release CLK_INH while CLK is high")
    s165(1, 1, 0, 0, pat)
    s165(1, 0, 0, 0, pat)
    s165(1, 1, 0, 0, pat, "one normal clock: the 0 on SER enters stage A, QH still 1")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "74hc595-74hc165-tests.txt"
    out.write_text(test_vectors())
    print(out)
