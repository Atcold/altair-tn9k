"""Panel schematic sheets for the shift-register backend (5x 74HC595, 4x 74HC165).

Each sheet_* function returns one A3 figure. SHEETS lists them in PDF order.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import schemdraw
import schemdraw.elements as elm

from schematic import (FS, T, fill, page, canvas, finish, notes, table,
                       ic, tag, netlabel, toggle, supply, nc)

N = 5  # sheets in this set


# ================================================================ sheet 1
def sheet_block():
    fig, fr = page(1, N, "Block diagram", "Block diagram")
    ax = canvas(fig, [0.03, 0.12, 0.94, 0.80]); ax.set_xlim(0, 100); ax.set_ylim(0, 60)

    def box(x, y, w, h, txt, fc="#ffffff", fs=10):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc=fill(fc), ec=T.FG, lw=1.2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs)

    def arrow(x1, y1, x2, y2, txt=None, at=None, fs=8, ha="center"):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=T.FG))
        if txt:
            ax.text(*at, txt, ha=ha, va="center", fontsize=fs)

    def region(x, y, w, h, title):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4", fc="none",
                                    ec=T.MUTED, lw=1.5, ls="--"))
        ax.text(x + 1, y + h - 1.5, title, fontsize=11, weight="bold", color=T.MUTED)

    box(1, 28, 10, 8, "Laptop\n\nterminal +\nprogrammer", fc="#f2f2f2")
    arrow(11.3, 32, 17, 32)
    ax.text(6, 26.5, "USB-C: 5 V power,\nprogramming, serial", ha="center", va="top", fontsize=8)

    region(15, 12, 26, 37, "CARRIER BOARD")
    box(17, 21, 11, 21, "Tang Nano 9K\nGW1NR-9\n\n8080 core\nmemory\n88-SIO\npanel_io", fc="#e8f0fb")
    box(32, 33, 6, 6, "R1–R5\n33 Ω\nseries", fs=8)
    box(32, 21, 6, 7, "J1\n14-pin\nIDC", fs=9, fc="#fff6e0")
    arrow(28.3, 36, 32, 36, "5 outputs", (30.2, 37.3), fs=7)
    arrow(35, 32.7, 35, 28.3)
    arrow(28.3, 26.5, 31.7, 26.5, "3V3, GND", (30.0, 27.8), fs=7)
    arrow(31.7, 22.5, 28.3, 22.5, "SW_QH", (30.0, 21.2), fs=7)
    box(17, 14, 21, 4.5, "Header with spare FPGA pins:\nmicroSD, extra UART, analyser", fs=8, fc="#f7f7f7")

    ax.plot([38.4, 47.2], [24.5, 24.5], color=T.RIBBON, lw=6, alpha=0.5)
    ax.text(42.8, 21.8, "14-way\nribbon\n≈ 15 cm", fontsize=7.5, ha="center", va="top")

    region(46, 2, 53, 55, "PANEL BOARD (front-panel PCB, toggles and LEDs mounted on it)")
    box(47.5, 21, 5, 7, "J2\n14-pin\nIDC", fs=9, fc="#fff6e0")

    ax.text(56, 51, "LED chain: 5 × 74HC595, data flows U1 → U5", fontsize=10, weight="bold")
    xs = [56, 64.5, 73, 81.5, 90]
    groups = ["A0–A7", "A8–A15", "D0–D7", "Status ×8\nMEMR INP M1 OUT\nHLTA STACK WO INT",
              "INTE PROT\nWAIT HLDA\n(+4 spare)"]
    for i, (x, g) in enumerate(zip(xs, groups)):
        box(x, 42, 6.5, 6, f"U{i+1}\n74HC595", fc="#eaf7ea", fs=9)
        ax.add_patch(plt.Circle((x + 3.25, 39.6), 0.6, fc="#ff5050", ec=T.FG, lw=0.6))
        ax.text(x + 3.25, 38.2, g, ha="center", va="top", fontsize=7.5)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow(a + 6.8, 45, b - 0.3, 45, "QH'→SER", (((a + 6.8) + b) / 2, 46.2), fs=6.5)
    arrow(52.8, 26, 56, 43.5, "LED_SER", (52.2, 35), fs=8, ha="right")
    ax.text(77, 32, "LED_SRCLK, LED_RCLK shared by all five;  OE = GND,  MR = 3V3",
            fontsize=8, ha="center", style="italic")

    ax.text(56, 27, "Switch chain: 4 × 74HC165, data flows U9 → U6", fontsize=10, weight="bold")
    xs2 = [56, 66, 76, 86]
    groups2 = ["SA0–SA7\n(toggles)", "SA8–SA15\n(toggles)",
               "Control toggles, UP side\nSTOP, SINGLE STEP, EXAMINE,\nDEPOSIT, RESET, PROTECT,\nAUX1, AUX2",
               "Control toggles, DOWN side\nRUN, (spare), EXAM NEXT,\nDEP NEXT, CLR, UNPROTECT,\nAUX1, AUX2"]
    for i, (x, g) in enumerate(zip(xs2, groups2)):
        box(x, 17, 7, 6, f"U{i+6}\n74HC165", fc="#eaf0fb", fs=9)
        toggle(ax, x + 3.5, 14.4)
        ax.text(x + 3.5, 12.9, g, ha="center", va="top", fontsize=7.5)
    for a, b in zip(xs2[:-1], xs2[1:]):
        arrow(b - 0.3, 20, a + 7.3, 20, "QH→SER", (((a + 7.3) + b) / 2, 21.2), fs=6.5)
    ax.text(93.8, 20, "SER\n= GND", fontsize=7.5, va="center")
    arrow(55.7, 19, 52.8, 22.5, "SW_QH", (54.5, 17.3), fs=8)
    ax.text(72.5, 4.5, "SW_LOAD, SW_CLK shared by all four;  CLK INH = GND.  "
            "Every input: 10 kΩ pull-up to 3V3, switch to GND (closed reads 0).",
            fontsize=8, ha="center", style="italic")

    notes(fr, 0.03, 0.105, [
        "Six FPGA signals drive the whole panel: LED_SER, LED_SRCLK, LED_RCLK, SW_LOAD, SW_CLK (outputs) and SW_QH (input).",
        "Everything on the panel runs at 3.3 V from the Tang Nano's 3V3 pin. No 5 V anywhere on the panel.",
    ])
    return fig


# ================================================================ sheet 2
def sheet_carrier():
    fig, fr = page(2, N, "Carrier board and panel connector", "Carrier and connector")

    ax = canvas(fig, [0.03, 0.33, 0.48, 0.58])
    d = schemdraw.Drawing(canvas=ax, show=False)
    tn = d.add(ic([], [("3V3", "3V3", "V33"), ("LED_SER", "IO a", "ser"), ("LED_SRCLK", "IO b", "srclk"),
                       ("LED_RCLK", "IO c", "rclk"), ("SW_LOAD", "IO d", "load"), ("SW_CLK", "IO e", "clk"),
                       ("SW_QH", "IO f", "qh"), ("SPARE1", "IO g", "sp1"), ("SPARE2", "IO h", "sp2"),
                       ("GND", "GND", "G")],
                  None, None, (6, 12), "Tang Nano 9K  (on female headers)", loc="top"))
    d.add(elm.Line().at(tn.V33).right(1)); d.add(elm.Line().up(0.5)); d.add(elm.Vdd().label("3V3"))
    for a, net, r in [("ser", "LED_SER", "R1"), ("srclk", "LED_SRCLK", "R2"), ("rclk", "LED_RCLK", "R3"),
                      ("load", "SW_LOAD", "R4"), ("clk", "SW_CLK", "R5")]:
        d.add(elm.Line().at(getattr(tn, a)).right(1))
        d.add(elm.Resistor().right().length(3).label(f"{r}  33 Ω", fontsize=FS - 1))
        d.add(elm.Line().right(0.5)); tag(d, net)
    for a, net in [("qh", "SW_QH"), ("sp1", "SPARE1"), ("sp2", "SPARE2")]:
        d.add(elm.Line().at(getattr(tn, a)).right(4.5)); tag(d, net)
    d.add(elm.Line().at(tn.G).right(1)); d.add(elm.Ground())
    finish(d, ax)

    ax2 = canvas(fig, [0.55, 0.36, 0.20, 0.55])
    d = schemdraw.Drawing(canvas=ax2, show=False)
    nets = ["3V3", "GND", "LED_SER", "LED_SRCLK", "GND", "LED_RCLK", "SW_LOAD", "GND", "SW_CLK", "SW_QH",
            "GND", "SPARE1", "SPARE2", "3V3"]
    d.add(elm.Header(rows=14, cols=1, pinsright=[f"{i+1}   {n}" for i, n in enumerate(nets)],
                     pinfontsizeright=FS, pinspacing=0.8)
          .label("J1 (carrier) = J2 (panel)\n2×7 IDC, 2.54 mm\nshown in ribbon order", "top", ofst=0.4))
    finish(d, ax2, pad=0.4)

    ax3 = canvas(fig, [0.78, 0.55, 0.19, 0.30])
    d = schemdraw.Drawing(canvas=ax3, show=False)
    d.add(elm.Vdd().label("3V3"))
    top = d.add(elm.Line().down(0.6))
    d.add(elm.Capacitor().down().label("C1\n10 µF", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Line().at(top.end).right(2.5))
    d.add(elm.Capacitor().down().label("C2\n100 nF", loc="bottom"))
    d.add(elm.Ground())
    finish(d, ax3)
    fr.text(0.875, 0.53, "Bulk + HF decoupling at J1\n(and C3/C4, same values, at J2)",
            ha="center", va="top", fontsize=9)

    notes(fr, 0.03, 0.29, [
        "IO a–h: any free Tang Nano 9K header pins in a 3.3 V bank. Check the Sipeed pinout first; some banks are 1.8 V. The choice lives in the .cst file.",
        "R1–R5 (33 Ω series, close to the FPGA) tame ringing on the ribbon. On the breadboard, replace them with wires.",
        "Connector order puts a ground next to each clock conductor (LED_SRCLK at 4 next to GND at 5; SW_CLK at 9 next to GND at 8).",
        "SPARE1/SPARE2 run to free FPGA pins: future use, e.g. a buzzer, a third chain, or a logic-analyser trigger.",
        "Pins 1 and 14 both carry 3V3. Total panel current ≈ 50 mA with 1 kΩ LED resistors, ≈ 110 mA with 470 Ω.",
        "Also on the carrier: a header breaking out every other unused FPGA pin, and test points on all five outputs.",
    ], title="Notes")
    return fig


# ================================================================ sheet 3
def sheet_leds():
    fig, fr = page(3, N, "LED chain: 5 × 74HC595  (U1 shown; U2–U4 alike, U5 uses QA–QD only)", "LED chain")
    ax = canvas(fig, [0.02, 0.12, 0.57, 0.80])
    d = schemdraw.Drawing(canvas=ax, show=False)
    outs = [("QA", "15", "QA"), ("QB", "1", "QB"), ("QC", "2", "QC"), ("QD", "3", "QD"), ("QE", "4", "QE"),
            ("QF", "5", "QF"), ("QG", "6", "QG"), ("QH", "7", "QH"), ("QH'", "9", "QHS")]
    u = d.add(ic([("SER", "14", "SER"), ("SRCLK", "11", "SRCLK"), ("RCLK", "12", "RCLK"),
                  ("MR", "10", "MR", True), ("OE", "13", "OE", True)],
                 outs, ("VCC", "16"), ("GND", "8"), (4.5, 14), "U1\n74HC595"))
    netlabel(d, u.SER, "LED_SER (J2-3)", length=1.0)
    netlabel(d, u.SRCLK, "LED_SRCLK (J2-4)", length=1.0)
    netlabel(d, u.RCLK, "LED_RCLK (J2-6)", length=1.0)
    d.add(elm.Line().at(u.MR).left(1.2)); d.add(elm.Line().up(0.6)); d.add(elm.Vdd().label("3V3"))
    d.add(elm.Line().at(u.OE).left(1.2)); d.add(elm.Line().down(0.6)); d.add(elm.Ground())
    d.add(elm.Line().at(u.GND).down(0.4)); d.add(elm.Ground())
    supply(d, u.VCC)
    names = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"]
    ends = []
    for k, (n, num, a) in enumerate(outs[:-1]):
        d.add(elm.Line().at(getattr(u, a)).right(0.8))
        d.add(elm.Resistor().right().length(2.8).label(f"R{11+k}  1 kΩ", fontsize=FS - 1))
        led = d.add(elm.LED().right().length(2.6).label(f"LED{1+k}  {names[k]}", fontsize=FS - 1))
        ends.append(led.end)
    d.add(elm.Line().at(ends[0]).right(0.8))
    bus = d.add(elm.Line().down(ends[0].y - ends[-1].y))
    for e in ends[1:]:
        d.add(elm.Line().at(e).right(0.8)); d.add(elm.Dot().at((e.x + 0.8, e.y)))
    d.add(elm.Line().at(bus.end).down(0.5)); d.add(elm.Ground())
    netlabel(d, u.QHS, "to U2 SER (pin 14)", direction="right", length=6.6)
    finish(d, ax)

    table(fig, [0.61, 0.56, 0.36, 0.33], "Chain connections",
          ["Chip", "SER (14) from", "QH' (9) to", "LEDs on QA…QH"],
          [["U1", "J2-3  LED_SER", "U2 SER", "A0 … A7"],
           ["U2", "U1 QH'", "U3 SER", "A8 … A15"],
           ["U3", "U2 QH'", "U4 SER", "D0 … D7"],
           ["U4", "U3 QH'", "U5 SER", "MEMR INP M1 OUT HLTA STACK WO INT"],
           ["U5", "U4 QH'", "test point", "INTE PROT WAIT HLDA, QE–QH unused"]],
          [0.09, 0.22, 0.18, 0.51])
    notes(fr, 0.61, 0.52, [
        "Common to all five chips: SRCLK (11) = LED_SRCLK, RCLK (12) = LED_RCLK,",
        "OE (13) = GND, MR (10) = 3V3, VCC (16) = 3V3, GND (8) = GND,",
        "one 100 nF capacitor per chip, right at pin 16.",
        "",
        "LEDs active high: output → resistor → anode, cathode → GND.",
        "1 kΩ ≈ 1.3 mA per LED; 470 Ω ≈ 3 mA if brighter is wanted.",
        "Worst case per chip 8 × 3 mA = 24 mA, within the 74HC595 limit.",
        "Designators: U1 uses R11–R18 / LED1–LED8; U2 R21–R28 / LED9–LED16, etc.",
        "",
        "Shift order: the first bit clocked in ends on U5 QH, the last on U1 QA.",
        "HDL shifts led[39] first and led[0] last, then pulses RCLK once.",
        "Full update: 40 SRCLK pulses + 1 RCLK pulse, ≈ 4 µs at 10 MHz.",
    ], title="Notes")
    return fig


# ================================================================ sheet 4
def sheet_switches():
    fig, fr = page(4, N, "Switch chain: 4 × 74HC165  (U6 shown; U7 alike, U8 and U9 have the control toggles)", "Switch chain")
    ax = canvas(fig, [0.02, 0.12, 0.50, 0.80])
    d = schemdraw.Drawing(canvas=ax, show=False)
    ins = [("A", "11", "A"), ("B", "12", "B"), ("C", "13", "C"), ("D", "14", "D"), ("E", "3", "E"),
           ("F", "4", "F"), ("G", "5", "G"), ("H", "6", "H"), ("QH", "9", "QH"), ("/QH", "7", "QHN", True)]
    u = d.add(ic([("SH/LD", "1", "LD", True), ("CLK", "2", "CLK"), ("CLK INH", "15", "INH"), ("SER", "10", "SER")],
                 ins, ("VCC", "16"), ("GND", "8"), (4.5, 16), "U6\n74HC165"))
    netlabel(d, u.LD, "SW_LOAD (J2-7)", length=1.0)
    netlabel(d, u.CLK, "SW_CLK (J2-9)", length=1.0)
    d.add(elm.Line().at(u.INH).left(1.2)); d.add(elm.Line().down(0.4)); d.add(elm.Ground())
    netlabel(d, u.SER, "from U7 QH (pin 9)", length=1.0)
    d.add(elm.Line().at(u.GND).down(0.4)); d.add(elm.Ground())
    supply(d, u.VCC)
    ends = []
    for k, (n, num, a, *_) in enumerate(ins[:8]):
        p = getattr(u, a)
        d.add(elm.Line().at(p).right(1.6))
        node = d.add(elm.Dot())
        d.add(elm.Resistor().at(node.center).up().length(1.05).scale(0.7)
              .label(f"RN1-{k+2}", loc="bottom", fontsize=FS - 2))
        d.add(elm.Dot(open=True).label("3V3", "right", fontsize=FS - 2))
        sw = d.add(elm.Switch().at(node.center).right().length(2.6)
                   .label(f"SA{k}", fontsize=FS - 1, loc="bottom"))
        ends.append(sw.end)
    d.add(elm.Line().at(ends[0]).right(0.8))
    bus = d.add(elm.Line().down(ends[0].y - ends[-1].y))
    for e in ends[1:]:
        d.add(elm.Line().at(e).right(0.8)); d.add(elm.Dot().at((e.x + 0.8, e.y)))
    d.add(elm.Line().at(bus.end).down(0.5)); d.add(elm.Ground())
    netlabel(d, u.QH, "SW_QH (J2-10)", direction="right", length=6.2)
    nc(d, u.QHN)
    finish(d, ax)

    # momentary switch detail
    ax2 = canvas(fig, [0.55, 0.62, 0.20, 0.27])
    d = schemdraw.Drawing(canvas=ax2, show=False)
    sw = d.add(elm.SwitchSpdt2().right().scale(1.8))
    d.add(elm.Label().at((sw.a.x - 1.6, sw.a.y + 1.2))
          .label("S17  STOP/RUN\nmomentary (ON)-OFF-(ON)", fontsize=FS - 1))
    d.add(elm.Line().at(sw.a).left(0.6)); d.add(elm.Line().down(1.6)); d.add(elm.Ground())
    d.add(elm.Line().at(sw.b).up(0.6)); d.add(elm.Line().right(2.2)); tag(d, "U8 A  (STOP)")
    d.add(elm.Line().at(sw.c).down(0.6)); d.add(elm.Line().right(2.2)); tag(d, "U9 A  (RUN)")
    finish(d, ax2)
    fr.text(0.65, 0.60, "Control toggle wiring: common to GND, one side per chain input.\n"
            "Both inputs keep their own 10 kΩ pull-up (RN on U8/U9).\n"
            "Centre = both 1; held up = U8 bit 0; held down = U9 bit 0.",
            ha="center", va="top", fontsize=8.5)

    table(fig, [0.77, 0.62, 0.20, 0.27], "Chain connections",
          ["Chip", "SER (10)", "QH (9) to"],
          [["U6", "U7 QH", "J2-10 SW_QH"], ["U7", "U8 QH", "U6 SER"],
           ["U8", "U9 QH", "U7 SER"], ["U9", "GND", "U8 SER"]],
          [0.18, 0.37, 0.45], fs=8.5)

    notes(fr, 0.55, 0.50, [
        "Common to all four chips: SH/LD (1) = SW_LOAD, CLK (2) = SW_CLK, CLK INH (15) = GND,",
        "VCC (16) = 3V3, GND (8) = GND, /QH (7) unconnected, 100 nF at pin 16.",
        "",
        "Pull-ups: one Bourns 4609X-101-103LF per chip (RN1…RN4). 9-pin bussed SIP:",
        "pin 1 = common = 3V3, pins 2–9 = the eight 10 kΩ resistors to inputs A…H.",
        "",
        "Inputs: switch open = 1 (pulled up), closed to GND = 0. Invert in the HDL.",
        "Breadboard stages: an 8-way DIP switch replaces the eight toggles directly.",
        "",
        "Read cycle: pulse SW_LOAD low (parallel load), then 32 SW_CLK pulses.",
        "Before the first clock, SW_QH already shows U6 input H; data then arrives",
        "U6 H…A, U7 H…A, U8 H…A, U9 H…A. Sample SW_QH before each rising edge.",
        "Debounce in the HDL: sample at ~1 kHz, accept a change after ~5 stable reads.",
    ], title="Notes")
    return fig


# ================================================================ sheet 5
def sheet_maps():
    fig, fr = page(5, N, "Bit maps and breadboard subsets", "Bit maps, breadboard")
    led_rows = [
        ["U1", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"],
        ["U2", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15"],
        ["U3", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"],
        ["U4", "MEMR", "INP", "M1", "OUT", "HLTA", "STACK", "WO", "INT"],
        ["U5", "INTE", "PROT", "WAIT", "HLDA", "–", "–", "–", "–"]]
    table(fig, [0.03, 0.62, 0.45, 0.28], "LED map  (led[n]: n = 8 × chip index + output, U1 = 0)",
          ["Chip", "QA", "QB", "QC", "QD", "QE", "QF", "QG", "QH"], led_rows, [0.1] + [0.1125] * 8)
    sw_rows = [
        ["U6", "SA0", "SA1", "SA2", "SA3", "SA4", "SA5", "SA6", "SA7"],
        ["U7", "SA8", "SA9", "SA10", "SA11", "SA12", "SA13", "SA14", "SA15"],
        ["U8", "STOP", "SSTEP", "EXAM", "DEP", "RESET", "PROT", "AUX1↑", "AUX2↑"],
        ["U9", "RUN", "spare", "EX NXT", "DEP NXT", "CLR", "UNPROT", "AUX1↓", "AUX2↓"]]
    table(fig, [0.52, 0.62, 0.45, 0.28], "Switch map  (sw[n]: n = 8 × chip index + input, U6 = 0)",
          ["Chip", "A", "B", "C", "D", "E", "F", "G", "H"], sw_rows, [0.1] + [0.1125] * 8)

    bb_rows = [
        ["Stage 1", "U1 + LED1–LED8 + R11–R18", "LED_SER, LED_SRCLK, LED_RCLK", "Binary counter on 8 LEDs"],
        ["Stage 2", "+ U6 + RN1 + 8-way DIP switch", "+ SW_LOAD, SW_CLK, SW_QH", "DIP switches mirrored on LEDs"],
        ["Stage 3", "+ U2 (8 LEDs) + U7 + RN2 + 2nd DIP", "same six signals", "16 bits each way, PWM brightness"],
    ]
    table(fig, [0.03, 0.36, 0.94, 0.19],
          "Breadboard subsets  (same schematic, fewer chips; no J1/J2, wire FPGA pins directly)",
          ["", "Parts added", "FPGA signals used", "Goal"], bb_rows, [0.08, 0.32, 0.30, 0.30], fs=10)

    notes(fr, 0.03, 0.31, [
        "Breadboard rules:",
        "•  Rails from the Tang Nano 3V3 and GND pins only. 100 nF across pins 16/8 of every chip.",
        "•  Unused 74HC165 inputs on a partial chain still need pull-ups (the resistor network does it).",
        "•  On a chain that stops early, tie the last 74HC165's SER (10) to GND; leave the last 74HC595's QH' open.",
        "•  Keep the clock wires short; clip the logic analyser on LED_SRCLK, LED_RCLK, SW_CLK, SW_LOAD.",
        "",
        "Open items before the PCB: choose FPGA pins (3.3 V banks) and record them in the .cst; confirm LED resistor value by eye;",
        "pick the toggle part numbers and pitch, which set the panel width; decide the panel size (original ≈ 43 cm, scaled ≈ 25–30 cm).",
    ], size=10)
    return fig


SHEETS = [sheet_block, sheet_carrier, sheet_leds, sheet_switches, sheet_maps]
