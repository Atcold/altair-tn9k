"""74HC595 and 74HC165 drawn at flip-flop level, plus their function tables and pinouts.

Each sheet_* function returns one A3 figure; SHEETS lists them in PDF order.
"""
import schemdraw
import schemdraw.elements as elm
import schemdraw.logic as logic

from schematic import FS, page, canvas, finish, notes, table, tag, ff, OV

N = 3            # sheets in this set
TK = (0.26, 1.0)  # tag sizing for these larger drawings


def bus(d, y, xa, xb, text):
    d.add(elm.Line().at((xa, y)).to((xb, y)))
    d.add(elm.Line().at((xa, y)).left(0.01)); tag(d, text, "left", TK)


# ================================================================ 74HC595
def sheet_595():
    fig, fr = page(1, N, "74HC595 at flip-flop level: 8-bit shift register + 8-bit storage register + tri-state outputs",
                   "74HC595 internals")
    ax = canvas(fig, [0.03, 0.27, 0.94, 0.65])
    d = schemdraw.Drawing(canvas=ax, show=False)
    PITCH, SOFF, SY, ROW = 10.8, 6.2, -6.5, 21.5
    names = "ABCDEFGH"
    outs = ["QA (15)", "QB (1)", "QC (2)", "QD (3)", "QE (4)", "QF (5)", "QG (6)", "QH (7)"]
    for r in range(2):
        Y = -r * ROW
        sh, st, tris = [], [], []
        for c in range(4):
            i = 4 * r + c
            x = c * PITCH
            sh.append(d.add(ff([(OV("CLR"), "CLR")], w=3.0, h=3.6, label=f"shift {names[i]}").at((x, Y))))
            st.append(d.add(ff(w=3.0, h=3.6, label=f"store {names[i]}").at((x + SOFF, Y + SY))))
        x0 = sh[0].D.x - 2.2
        d.add(elm.Line().at(sh[0].D).left(2.2))
        tag(d, "SER  (14)" if r == 0 else "from shift D, Q", "left", TK)
        for c in range(4):
            i = 4 * r + c
            q = sh[c].Q
            tapx = q.x + 0.6
            if c < 3:
                d.add(elm.Line().at(q).to(sh[c + 1].D))
            else:
                d.add(elm.Line().at(q).right(2.5)); tag(d, "QH'  (9)" if i == 7 else "to shift E, D", "right", TK)
            d.add(elm.Dot().at((tapx, q.y)))
            d.add(elm.Line().at((tapx, q.y)).to((tapx, st[c].D.y)))
            d.add(elm.Line().at((tapx, st[c].D.y)).to(st[c].D))
        yclr = sh[0].CLR.y + 0.9
        bus(d, yclr, x0, sh[3].CLR.x, OV("SRCLR") + "  (10)")
        for c, s_ in enumerate(sh):
            d.add(elm.Line().at(s_.CLR).to((s_.CLR.x, yclr)))
            if c < 3:
                d.add(elm.Dot().at((s_.CLR.x, yclr)))
        ysck = sh[0].C.y - 1.9
        bus(d, ysck, x0, sh[3].C.x - 0.5, "SRCLK  (11)")
        yrck = st[0].C.y - 1.9
        bus(d, yrck, x0, st[3].C.x - 0.5, "RCLK  (12)")
        for row, yb in ((sh, ysck), (st, yrck)):
            for c, f in enumerate(row):
                cx = f.C.x - 0.5
                d.add(elm.Line().at(f.C).to((cx, f.C.y)))
                d.add(elm.Line().at((cx, f.C.y)).to((cx, yb)))
                if c < 3:
                    d.add(elm.Dot().at((cx, yb)))
        ytri = yrck - 0.9
        for c, t in enumerate(st):
            i = 4 * r + c
            xb = t.Q.x + 0.8
            d.add(elm.Line().at(t.Q).to((xb, t.Q.y)))
            d.add(elm.Line().at((xb, t.Q.y)).to((xb, ytri)))
            tb = d.add(logic.Tristate().down().at((xb, ytri)))
            tris.append(tb)
            d.add(elm.Line().at(tb.end).down(0.6))
            d.add(elm.Label().label(outs[i], "left", fontsize=FS + 1))
        yoe = tris[0].end.y - 1.6
        for c, tb in enumerate(tris):
            d.add(elm.Line().at(tb.c).right(0.6))
            d.add(elm.Line().down(tb.c.y - yoe))
            if c < 3:
                d.add(elm.Dot().at((tb.c.x + 0.6, yoe)))
        if r == 0:
            d.add(elm.Line().at((x0 + 4.2, yoe)).to((tris[3].c.x + 0.6, yoe)))
            d.add(logic.Not().right().at((x0 + 0.6, yoe)).length(3.6))
            d.add(elm.Line().at((x0 + 0.6, yoe)).left(0.01)); tag(d, OV("OE") + "  (13)", "left", TK)
            d.add(elm.Label().at((x0 + 5.2, yoe + 0.35)).label("OE (internal)", fontsize=FS - 1))
        else:
            bus(d, yoe, x0, tris[3].c.x + 0.6, "OE (internal)")
    finish(d, ax, pad=0.5)

    notes(fr, 0.03, 0.245, [
        "Shift register: on each rising edge of SRCLK, SER enters stage A and every stage passes its bit to the next (A→B→…→H).",
        "Stage H also drives QH' (pin 9), the serial output used to chain the next 595. QH' is never tri-stated.",
        "Storage register: on each rising edge of RCLK, all eight shift-register bits are copied at once into the storage flip-flops,",
        "which is why the LEDs never show bits sliding past: outputs only change on RCLK.",
        f"{OV('SRCLR')} low clears the shift register only (asynchronously). The storage register keeps its value until the next RCLK.",
        f"{OV('OE')} high puts QA–QH in high impedance. On the panel it is tied to GND, so outputs are always driven.",
        "Drawn in two rows for legibility: identically named tags are the same wire. All flip-flops are rising-edge D-types (C = clock).",
    ], title="How it works", size=10)
    return fig


# ================================================================ 74HC165
def sheet_165():
    fig, fr = page(2, N, "74HC165 at flip-flop level: 8-bit shift register with asynchronous parallel load",
                   "74HC165 internals")
    ax = canvas(fig, [0.03, 0.27, 0.94, 0.65])
    d = schemdraw.Drawing(canvas=ax, show=False)
    PITCH, ROW = 9.5, 15.0
    names = "ABCDEFGH"
    pins_in = ["A (11)", "B (12)", "C (13)", "D (14)", "E (3)", "F (4)", "G (5)", "H (6)"]
    for r in range(2):
        Y = -r * ROW
        fs_ = []
        for c in range(4):
            i = 4 * r + c
            fs_.append(d.add(ff([(OV("PRE"), "PRE"), (OV("CLR"), "CLR")], w=5.0, h=3.6, label=f"stage {names[i]}")
                             .at((c * PITCH, Y))))
        x0 = fs_[0].D.x - 2.2
        d.add(elm.Line().at(fs_[0].D).left(2.2))
        tag(d, "SER  (10)" if r == 0 else "from stage D, Q", "left", TK)
        for c in range(3):
            d.add(elm.Line().at(fs_[c].Q).to(fs_[c + 1].D))
        if r == 0:
            d.add(elm.Line().at(fs_[3].Q).right(1.8)); tag(d, "to stage E, D", "right", TK)
        else:
            d.add(elm.Line().at(fs_[3].Q).right(1.8)); tag(d, "QH  (9)", "right", TK)
            d.add(elm.Line().at(fs_[3].QN).right(1.8)); tag(d, OV("QH") + "  (7)", "right", TK)

        gl = 1.85
        yload = fs_[0].PRE.y + 0.5 + gl + 1.4
        for c, f in enumerate(fs_):
            i = 4 * r + c
            pre, clr = f.PRE, f.CLR
            n1 = d.add(logic.Nand().down().anchor("out").at((pre.x, pre.y + 0.5)))
            d.add(elm.Line().at(n1.out).to(pre))
            n2 = d.add(logic.Nand().down().anchor("out").at((clr.x, clr.y + 0.5)))
            d.add(elm.Line().at(n2.out).to(clr))
            ydot = pre.y + 0.25
            xm = (pre.x + clr.x) / 2
            ytop = n2.in2.y + 0.5
            d.add(elm.Dot().at((pre.x, ydot)))
            d.add(elm.Line().at((pre.x, ydot)).to((xm, ydot)))
            d.add(elm.Line().at((xm, ydot)).to((xm, ytop)))
            d.add(elm.Line().at((xm, ytop)).to((n2.in2.x, ytop)))
            d.add(elm.Line().at((n2.in2.x, ytop)).to(n2.in2))
            for g in (n1, n2):
                d.add(elm.Line().at(g.in1).to((g.in1.x, yload)))
                if not (c == 3 and g is n2):
                    d.add(elm.Dot().at((g.in1.x, yload)))
            d.add(elm.Line().at(n1.in2).to((n1.in2.x, yload + 1.5)))
            d.add(elm.Label().at((n1.in2.x, yload + 1.5)).label(pins_in[i], "top", fontsize=FS + 1))
        xl_end = fs_[3].CLR.x + 0.25
        if r == 0:
            d.add(elm.Line().at((x0 + 3.6, yload)).to((xl_end, yload)))
            d.add(logic.Not().right().at((x0, yload)).length(3.6))
            d.add(elm.Line().at((x0, yload)).left(0.01)); tag(d, "SH/" + OV("LD") + "  (1)", "left", TK)
            d.add(elm.Label().at((x0 + 4.4, yload + 0.35)).label("LOAD", fontsize=FS - 1))
        else:
            bus(d, yload, x0, xl_end, "LOAD")

        yck = fs_[0].C.y - 2.0
        for c, f in enumerate(fs_):
            cx = f.C.x - 0.5
            d.add(elm.Line().at(f.C).to((cx, f.C.y)))
            d.add(elm.Line().at((cx, f.C.y)).to((cx, yck)))
            if c < 3:
                d.add(elm.Dot().at((cx, yck)))
        if r == 0:
            org = d.add(logic.Or().right().anchor("out").at((x0 + 1.4, yck)))
            d.add(elm.Line().at(org.out).to((fs_[3].C.x - 0.5, yck)))
            d.add(elm.Label().at((x0 + 2.4, yck + 0.35)).label("CLK (internal)", fontsize=FS - 1))
            d.add(elm.Line().at(org.in1).left(0.6)); d.add(elm.Line().up(0.6)); d.add(elm.Line().left(0.4))
            tag(d, "CLK  (2)", "left", TK)
            d.add(elm.Line().at(org.in2).left(0.6)); d.add(elm.Line().down(0.6)); d.add(elm.Line().left(0.4))
            tag(d, "CLK INH  (15)", "left", TK)
        else:
            bus(d, yck, x0, fs_[3].C.x - 0.5, "CLK (internal)")
    finish(d, ax, pad=0.5)

    notes(fr, 0.03, 0.245, [
        f"Parallel load: SH/{OV('LD')} low makes LOAD = 1. In each stage the two NANDs turn the input bit into an asynchronous preset or clear:",
        f"input 1  →  left NAND outputs 0  →  {OV('PRE')} active  →  Q = 1;   input 0  →  right NAND outputs 0  →  {OV('CLR')} active  →  Q = 0.",
        "The load is asynchronous and continuous: while SH/LD is low, Q follows the inputs and the clock is ignored.",
        "Shift: with SH/LD high both NANDs output 1 (inactive). Each rising edge of the internal clock moves SER into A and A…G into B…H.",
        "QH is stage H, so right after a load it already shows input H: the first bit is readable before any clock pulse.",
        "Internal clock = CLK OR CLK INH, so either input held high blocks the other. Change CLK INH only while CLK is high, or its edge acts as a clock.",
        "Drawn in two rows for legibility: identically named tags are the same wire. All flip-flops are rising-edge D-types (C = clock).",
    ], title="How it works", size=10)
    return fig


# ================================================================ tables
def sheet_tables():
    fig, fr = page(3, N, "Function tables and pinouts", "Function tables, pinouts")
    table(fig, [0.03, 0.62, 0.45, 0.28], "74HC595 function table  (↑ = rising edge)",
          ["SER", "SRCLK", OV("SRCLR"), "RCLK", OV("OE"), "Effect"],
          [["X", "X", "X", "X", "H", "QA–QH high impedance (QH' unaffected)"],
           ["X", "X", "L", "X", "X", "Shift register cleared"],
           ["L", "↑", "H", "X", "X", "Shift; stage A = 0"],
           ["H", "↑", "H", "X", "X", "Shift; stage A = 1"],
           ["X", "X", "X", "↑", "X", "Shift register copied to storage"],
           ["X", "X", "X", "X", "L", "Storage driven onto QA–QH"]],
          [0.07, 0.10, 0.10, 0.09, 0.08, 0.56])
    table(fig, [0.52, 0.62, 0.45, 0.28], "74HC165 function table",
          ["SH/" + OV("LD"), "CLK", "CLK INH", "Effect"],
          [["L", "X", "X", "Parallel load: A–H copied to stages (async)"],
           ["H", "L", "L", "Hold"],
           ["H", "↑", "L", "Shift; SER → A, …, G → H"],
           ["H", "X", "H", "Hold (clock inhibited)"],
           ["H", "L", "↑", "Shift (the two clock inputs are interchangeable)"],
           ["H", "H", "X", "Hold"]],
          [0.11, 0.09, 0.12, 0.68])

    table(fig, [0.03, 0.33, 0.45, 0.24], "DIP-16 pinouts (top view, pin 1 top left)",
          ["Pin", "74HC595", "Pin", "74HC595", "Pin", "74HC165", "Pin", "74HC165"],
          [["1", "QB", "16", "VCC", "1", "SH/" + OV("LD"), "16", "VCC"],
           ["2", "QC", "15", "QA", "2", "CLK", "15", "CLK INH"],
           ["3", "QD", "14", "SER", "3", "E", "14", "D"],
           ["4", "QE", "13", OV("OE"), "4", "F", "13", "C"],
           ["5", "QF", "12", "RCLK", "5", "G", "12", "B"],
           ["6", "QG", "11", "SRCLK", "6", "H", "11", "A"],
           ["7", "QH", "10", OV("SRCLR"), "7", OV("QH"), "10", "SER"],
           ["8", "GND", "9", "QH'", "8", "GND", "9", "QH"]],
          [0.08, 0.17, 0.08, 0.17, 0.08, 0.17, 0.08, 0.17], fs=8.5)

    notes(fr, 0.03, 0.28, [
        "Pin names with a bar are active low.",
        "Sources: TI SN74HC595 and SN74HC165 datasheets (logic diagrams and function tables).",
    ], size=9)
    return fig


SHEETS = [sheet_595, sheet_165, sheet_tables]
