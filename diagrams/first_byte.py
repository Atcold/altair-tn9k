"""First breadboard: one byte in, one byte out, on both backends at once.

Shift registers: one 74HC595 driving 8 LEDs, one 74HC165 reading 8 switches.
SPI expander: one MCP23S17, port A driving its own 8 LEDs, port B reading.
Both read the same 8-way DIP switch through the same pull-ups; each backend
has its own LEDs. Each sheet_* function returns one A3 figure; SHEETS lists
them in PDF order.
"""
import schemdraw
import schemdraw.elements as elm

from schematic import (FS, page, canvas, finish, notes, table,
                       ic, tag, netlabel, supply, nc, T, VDD, LED, to_gnd, ground_bus)

N = 2            # sheets in this set
TK = (0.32, 1.2, 1.0)  # tag sizing (width per character, end padding, height): this large drawing is scaled down
LP = 1.2          # lead length on the chips' left sides
PAD = 0.12        # vertical padding for the chips' left-side pins (fraction of the height)


def led_row(d, pin, r, led):
    d.add(elm.Line().at(pin).right(0.8))
    d.add(elm.Resistor().right().length(2.8).label(f"R{r}  1 kΩ", fontsize=FS - 1))
    return d.add(LED().right().length(2.6).label(f"LED{led}", fontsize=FS - 1)).end


# ================================================================ sheet 1
def sheet_breadboard():
    fig, fr = page(1, N, "First byte: both backends on one breadboard, sharing one DIP switch", "Breadboard")
    ax = canvas(fig, [0.02, 0.11, 0.96, 0.82])
    d = schemdraw.Drawing(canvas=ax, show=False)

    # ---- shift-register backend: U1 74HC595 with LED1-LED8
    outs = [("QA", "15", "QA"), ("QB", "1", "QB"), ("QC", "2", "QC"), ("QD", "3", "QD"), ("QE", "4", "QE"),
            ("QF", "5", "QF"), ("QG", "6", "QG"), ("QH", "7", "QH"), ("QH'", "9", "QHS")]
    u1 = d.add(ic([("SER", "14", "SER"), ("SRCLK", "11", "SRCLK"), ("RCLK", "12", "RCLK"),
                   ("MR", "10", "MR", True), ("OE", "13", "OE", True)],
                  outs, ("VCC", "16"), ("GND", "8"), (10, 16), "U1\n74HC595", lpad=PAD).right().at((0, 0)))
    netlabel(d, u1.SER, "LED_SER", length=LP, k=TK)
    netlabel(d, u1.SRCLK, "LED_SRCLK", length=LP, k=TK)
    netlabel(d, u1.RCLK, "LED_RCLK", length=LP, k=TK)
    d.add(elm.Line().at(u1.MR).left(LP).color(T.SUPPLY)); d.add(elm.Line().up(0.6).color(T.SUPPLY))
    d.add(VDD().label("3V3"))
    to_gnd(d, u1.OE, ("left", LP), ("down", 0.6))
    to_gnd(d, u1.GND, ("down", 0.4))
    supply(d, u1.VCC)
    nc(d, u1.QHS)
    ground_bus(d, [led_row(d, getattr(u1, a), 1 + k, 1 + k) for k, (n, num, a) in enumerate(outs[:8])])

    # ---- shift-register backend: U2 74HC165 reading SW0-SW7
    ins = [("A", "11", "A"), ("B", "12", "B"), ("C", "13", "C"), ("D", "14", "D"), ("E", "3", "E"),
           ("F", "4", "F"), ("G", "5", "G"), ("H", "6", "H"), ("QH", "9", "QH"), ("/QH", "7", "QHN", True)]
    u2 = d.add(ic([("SH/LD", "1", "LD", True), ("CLK", "2", "CLK"), ("CLK INH", "15", "INH"), ("SER", "10", "SER")],
                  ins, ("VCC", "16"), ("GND", "8"), (10, 17), "U2\n74HC165", lpad=PAD).right().at((0, -24)))
    netlabel(d, u2.LD, "SW_LOAD", length=LP, k=TK)
    netlabel(d, u2.CLK, "SW_CLK", length=LP, k=TK)
    to_gnd(d, u2.INH, ("left", LP), ("down", 0.4))
    to_gnd(d, u2.SER, ("left", LP), ("down", 0.4))
    to_gnd(d, u2.GND, ("down", 0.4))
    supply(d, u2.VCC)
    for k, (n, num, a) in enumerate(ins[:8]):
        netlabel(d, getattr(u2, a), f"SW{k}", direction="right", length=1.0, k=TK)
    netlabel(d, u2.QH, "SW_QH", direction="right", length=1.0, k=TK)
    nc(d, u2.QHN)

    # ---- shared DIP switch S1 with pull-ups RN1, in the middle:
    #      3V3 rail on the left, each line SWk = node between its resistor and its switch, GND rail on the right
    x0, y0, dy = 28.0, 0.0, 3.6
    ends = []
    for k in range(8):
        y = y0 - k * dy
        d.add(elm.Resistor().at((x0, y)).right().length(3.0).label("10 kΩ", fontsize=FS - 1))
        node = d.add(elm.Dot())
        d.add(elm.Line().at(node.center).down(0.6).color(T.SHARED))
        tag(d, f"SW{k}", "down")
        ends.append(d.add(elm.Switch().at(node.center).right().length(3.4)
                          .label(f"S1-{k + 1}", fontsize=FS - 1)).end)
        if k < 7:
            d.add(elm.Line().at((x0, y)).to((x0, y - dy)).color(T.SUPPLY))
            d.add(elm.Dot().at((x0, y)).color(T.SUPPLY))
    d.add(elm.Line().at((x0, y0)).up(0.8).color(T.SUPPLY)); d.add(VDD().label("3V3"))
    ground_bus(d, ends)
    d.add(elm.Label().at((x0 + 3.0, y0 + 2.6))
          .label("S1: 8-way DIP switch, shared\nRN1: 8 × 10 kΩ pull-ups (one SIP)", fontsize=FS))

    # ---- SPI backend: U3 MCP23S17, port A to LED9-LED16, port B to SW0-SW7
    left = [("CS", "11", "CS", True), ("SCK", "12", "SCK"), ("SI", "13", "SI"), ("SO", "14", "SO"),
            ("RESET", "18", "RST", True), ("A0", "15", "A0"), ("A1", "16", "A1"), ("A2", "17", "A2"),
            ("INTA", "20", "INTA"), ("INTB", "19", "INTB")]
    right = ([(f"GPA{i}", str(21 + i), f"GPA{i}") for i in range(8)] +
             [(f"GPB{i}", str(1 + i), f"GPB{i}") for i in range(8)])
    u3 = d.add(ic(left, right, ("VDD", "9"), ("VSS", "10"), (12, 30), "U3\nMCP23S17", lpad=PAD).right().at((52, -14)))
    netlabel(d, u3.CS, "SPI_CS_n", length=LP, k=TK)
    netlabel(d, u3.SCK, "SPI_SCK", length=LP, k=TK)
    netlabel(d, u3.SI, "SPI_MOSI", length=LP, k=TK)
    netlabel(d, u3.SO, "SPI_MISO", length=LP, k=TK)
    d.add(elm.Line().at(u3.RST).left(0.8))
    d.add(elm.Resistor().left().length(2.6).label("R17  10 kΩ", loc="bottom", fontsize=FS - 1))
    d.add(VDD().label("3V3"))
    for pin in ("A0", "A1", "A2"):
        to_gnd(d, getattr(u3, pin), ("left", LP))
    nc(d, u3.INTA, "left")
    nc(d, u3.INTB, "left")
    to_gnd(d, u3.VSS, ("down", 0.4))
    supply(d, u3.VDD)
    ground_bus(d, [led_row(d, getattr(u3, f"GPA{k}"), 9 + k, 9 + k) for k in range(8)])
    for k in range(8):
        netlabel(d, getattr(u3, f"GPB{k}"), f"SW{k}", direction="right", length=1.0, k=TK)

    finish(d, ax, pad=0.8)
    notes(fr, 0.03, 0.095, [
        "Shift registers (left): U1 writes, U2 reads.   SPI expander (right): U3 port A writes, port B reads.",
        "Tags with the same name are the same wire: SW0–SW7 run from S1 to both U2 and U3.",
    ])
    return fig


# ================================================================ sheet 2
def sheet_notes():
    fig, fr = page(2, N, "First byte: FPGA pins, parts and test", "Pins, parts, test")
    table(fig, [0.03, 0.55, 0.45, 0.36], "FPGA pins  (any free 3.3 V-bank header pins; record them in the .cst)",
          ["Signal", "Backend", "Direction", "Goes to"],
          [["LED_SER", "sr", "out", "U1 SER (14)"],
           ["LED_SRCLK", "sr", "out", "U1 SRCLK (11)"],
           ["LED_RCLK", "sr", "out", "U1 RCLK (12)"],
           ["SW_LOAD", "sr", "out", "U2 SH/LD (1)"],
           ["SW_CLK", "sr", "out", "U2 CLK (2)"],
           ["SW_QH", "sr", "in", "U2 QH (9)"],
           ["SPI_SCK", "mcp", "out", "U3 SCK (12)"],
           ["SPI_MOSI", "mcp", "out", "U3 SI (13)"],
           ["SPI_MISO", "mcp", "in", "U3 SO (14)"],
           ["SPI_CS_n", "mcp", "out", "U3 CS (11)"]],
          [0.28, 0.17, 0.2, 0.35])
    table(fig, [0.52, 0.55, 0.45, 0.36], "Parts on this breadboard",
          ["Ref", "Part", "Value / notes"],
          [["U1", "SN74HC595N", "LED shift register"],
           ["U2", "SN74HC165N", "switch shift register"],
           ["U3", "MCP23S17-E/SP", "SPI expander, address 000"],
           ["LED1–LED8", "5 mm LED", "on U1 QA–QH"],
           ["LED9–LED16", "5 mm LED", "on U3 GPA0–GPA7"],
           ["R1–R16", "resistor", "1 kΩ, one per LED"],
           ["RN1", "4609X-101-103LF", "8 × 10 kΩ, pin 1 to 3V3"],
           ["S1", "8-way DIP switch", "shared by U2 and U3"],
           ["R17", "resistor", "10 kΩ, U3 RESET pull-up"],
           ["C1–C3", "ceramic capacitor", "100 nF, one per chip"]],
          [0.24, 0.34, 0.42])

    notes(fr, 0.03, 0.50, [
        "Shift registers  (make PANEL=sr)",
        "•  Out: shift 8 bits into U1 on SRCLK, then one RCLK pulse to show them.",
        "•  In: pulse SW_LOAD low to load S1 into U2, then 8 SW_CLK pulses; QH gives H first.",
        "•  A closed switch reads 0.",
        "",
        "SPI expander  (make PANEL=mcp; mode 0, MSB first, opcodes 0x40 write, 0x41 read)",
        "•  Start-up: IODIRA (0x00) = 0x00, outputs; IODIRB (0x01) = 0xFF, inputs;",
        "   GPPUB (0x0D) = 0xFF, internal pull-ups (redundant while RN1 is fitted).",
        "•  Loop: read GPIOB (0x13), write the byte to OLATA (0x14).",
        "•  Nothing works until the start-up writes do, so it can't be split into out first, in later.",
        "•  A closed switch reads 0 here too.",
        "",
        "Done when: with PANEL=mcp, flipping a switch toggles the matching LED on U3,",
        "and PANEL=sr still drives U1's LEDs from the same switches.",
    ], size=10)
    notes(fr, 0.52, 0.50, [
        "Breadboard rules",
        "•  3V3 and GND from the Tang Nano only; no 5 V anywhere.",
        "•  100 nF across each chip's supply pins: 16/8 on U1 and U2, 9/10 on U3.",
        "•  LEDs are not shared: two outputs on one line would fight.",
        "•  U2 SER (10) and CLK INH (15) to GND; U1 QH' (9) left open.",
        "•  U3 RESET pulled up, A2–A0 to GND; never leave them floating.",
        "•  No series resistors needed with short breadboard wires.",
        "•  Keep clock wires short; clip the logic analyser on the clock,",
        "   latch and chip-select lines of the backend under test.",
    ], size=10)
    return fig


SHEETS = [sheet_breadboard, sheet_notes]
