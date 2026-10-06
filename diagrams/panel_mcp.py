"""Panel schematic sheets for the SPI-expander backend (5x MCP23S17).

All five expanders share one SPI bus and one chip select; hardware address
pins A2..A0 tell them apart. Each sheet_* function returns one A3 figure.
SHEETS lists them in PDF order.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import schemdraw
import schemdraw.elements as elm

from schematic import (FS, T, fill, page, canvas, finish, notes, table,
                       ic, tag, netlabel, toggle, supply, nc)

N = 5  # sheets in this set

# MCP23S17, SPDIP-28. Left pins top to bottom, right pins top to bottom.
MCP_LEFT = [("CS", "11", "CS", True), ("SCK", "12", "SCK"), ("SI", "13", "SI"), ("SO", "14", "SO"),
            ("RESET", "18", "RST", True), ("A0", "15", "A0"), ("A1", "16", "A1"), ("A2", "17", "A2"),
            ("INTA", "20", "INTA"), ("INTB", "19", "INTB")]
MCP_RIGHT = ([(f"GPA{i}", str(21 + i), f"GPA{i}") for i in range(8)] +
             [(f"GPB{i}", str(1 + i), f"GPB{i}") for i in range(8)])

# chip: (address A2 A1 A0, role)
CHIPS = {"U1": ("000", "LEDs A0–A15"), "U2": ("001", "LEDs D0–D7, MEMR INP M1 OUT HLTA STACK WO INT"),
         "U3": ("010", "LEDs INTE PROT WAIT HLDA"), "U4": ("011", "toggles SA0–SA15"),
         "U5": ("100", "control toggles")}


def mcp(d, ref):
    return d.add(ic(MCP_LEFT, MCP_RIGHT, ("VDD", "9"), ("VSS", "10"), (7, 24), f"{ref}\nMCP23S17"))


TK = (0.2, 1.0)  # tag sizing: the 16-row chips shrink the drawing, so tags need more room


def bus_and_power(d, u, address):
    """SPI bus tags, reset, address straps, unused interrupts, supply and decoupling."""
    netlabel(d, u.CS, "SPI_CS_n (J2-8)", length=1.0, k=TK)
    netlabel(d, u.SCK, "SPI_SCK (J2-3)", length=1.0, k=TK)
    netlabel(d, u.SI, "SPI_MOSI (J2-5)", length=1.0, k=TK)
    netlabel(d, u.SO, "SPI_MISO (J2-6)", length=1.0, k=TK)
    netlabel(d, u.RST, "RESET_n (R9 to 3V3)", length=1.0, k=TK)
    for pin, bit in zip(("A2", "A1", "A0"), address):
        d.add(elm.Line().at(getattr(u, pin)).left(1.2))
        d.add(elm.Vdd().label("3V3", fontsize=FS - 1) if bit == "1" else elm.Ground())
    nc(d, u.INTA)
    nc(d, u.INTB)
    d.add(elm.Line().at(u.VSS).down(0.4)); d.add(elm.Ground())
    supply(d, u.VDD)


def ground_bus(d, ends, dx=0.8):
    d.add(elm.Line().at(ends[0]).right(dx))
    bus = d.add(elm.Line().down(ends[0].y - ends[-1].y))
    for e in ends[1:]:
        d.add(elm.Line().at(e).right(dx)); d.add(elm.Dot().at((e.x + dx, e.y)))
    d.add(elm.Line().at(bus.end).down(0.5)); d.add(elm.Ground())


# ================================================================ sheet 1
def sheet_block():
    fig, fr = page(1, N, "Block diagram", "Block diagram")
    ax = canvas(fig, [0.03, 0.12, 0.94, 0.80]); ax.set_xlim(0, 100); ax.set_ylim(0, 60)

    def box(x, y, w, h, txt, fc="#ffffff", fs=10):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc=fill(fc), ec=T.FG,
                                    lw=1.2, zorder=2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, zorder=3)

    def arrow(x1, y1, x2, y2, txt=None, at=None, fs=8, ha="center"):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=T.FG))
        if txt:
            ax.text(*at, txt, ha=ha, va="center", fontsize=fs)

    def region(x, y, w, h, title):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4", fc="none",
                                    ec=T.MUTED, lw=1.5, ls="--"))
        ax.text(x + 1, y + h - 1.5, title, fontsize=11, weight="bold", color=T.MUTED)

    def wire(xs, ys):
        ax.plot(xs, ys, color=T.FG, lw=1.6, zorder=1)

    box(1, 28, 10, 8, "Laptop\n\nterminal +\nprogrammer", fc="#f2f2f2")
    arrow(11.3, 32, 17, 32)
    ax.text(6, 26.5, "USB-C: 5 V power,\nprogramming, serial", ha="center", va="top", fontsize=8)

    region(15, 12, 26, 37, "CARRIER BOARD")
    box(17, 21, 11, 21, "Tang Nano 9K\nGW1NR-9\n\n8080 core\nmemory\n88-SIO\nspi_master\npanel_io", fc="#e8f0fb")
    box(32, 33, 6, 6, "R1–R3\n33 Ω\nseries", fs=8)
    box(32, 21, 6, 7, "J1\n14-pin\nIDC", fs=9, fc="#fff6e0")
    arrow(28.3, 36, 32, 36, "3 outputs", (30.2, 37.3), fs=7)
    arrow(35, 32.7, 35, 28.3)
    arrow(28.3, 26.5, 31.7, 26.5, "3V3, GND", (30.0, 27.8), fs=7)
    arrow(31.7, 22.5, 28.3, 22.5, "MISO", (30.0, 21.2), fs=7)
    box(17, 14, 21, 4.5, "Header with spare FPGA pins:\nmicroSD, extra UART, analyser", fs=8, fc="#f7f7f7")

    ax.plot([38.4, 47.2], [24.5, 24.5], color=T.RIBBON, lw=6, alpha=0.5)
    ax.text(42.8, 21.8, "14-way\nribbon\n≈ 15 cm", fontsize=7.5, ha="center", va="top")

    region(46, 2, 53, 55, "PANEL BOARD (front-panel PCB, toggles and LEDs mounted on it)")
    box(47.5, 21, 5, 7, "J2\n14-pin\nIDC", fs=9, fc="#fff6e0")

    # one shared SPI bus
    wire([52.8, 55], [24.5, 24.5])
    wire([55, 55], [20, 45])
    wire([55, 88], [45, 45])
    wire([55, 75], [20, 20])
    ax.text(55.6, 32.5, "SPI bus: SCK, MOSI, MISO, CS_n,\nshared by all five expanders",
            fontsize=8, va="center", style="italic")

    ax.text(57, 51, "Outputs: 3 × MCP23S17, 36 LEDs", fontsize=10, weight="bold")
    outs = [("U1", "000", "GPA: A0–A7\nGPB: A8–A15"),
            ("U2", "001", "GPA: D0–D7\nGPB: MEMR INP M1 OUT\nHLTA STACK WO INT"),
            ("U3", "010", "GPA0–3: INTE PROT\nWAIT HLDA\n(12 pins spare)")]
    for i, (ref, addr, g) in enumerate(outs):
        x = 57 + 13 * i
        box(x, 42, 10, 6, f"{ref}  MCP23S17\naddress {addr}", fc="#eaf7ea", fs=9)
        ax.add_patch(plt.Circle((x + 5, 39.6), 0.6, fc="#ff5050", ec=T.FG, lw=0.6))
        ax.text(x + 5, 38.2, g, ha="center", va="top", fontsize=7.5)

    ax.text(57, 26.5, "Inputs: 2 × MCP23S17, 32 switch contacts", fontsize=10, weight="bold")
    ins = [("U4", "011", "GPA: SA0–SA7\nGPB: SA8–SA15\n(toggles)"),
           ("U5", "100", "GPA: control toggles, UP side\nGPB: control toggles, DOWN side")]
    for i, (ref, addr, g) in enumerate(ins):
        x = 57 + 13 * i
        box(x, 17, 10, 6, f"{ref}  MCP23S17\naddress {addr}", fc="#eaf0fb", fs=9)
        toggle(ax, x + 5, 14.4)
        ax.text(x + 5, 12.9, g, ha="center", va="top", fontsize=7.5)

    ax.text(72.5, 5.5, "Switches close to GND. The expanders' internal pull-ups replace the resistor networks,\n"
            "and their polarity register makes a closed switch read 1.",
            fontsize=8, ha="center", va="center", style="italic")

    notes(fr, 0.03, 0.105, [
        "Four FPGA signals drive the whole panel: SPI_SCK, SPI_MOSI, SPI_CS_n (outputs) and SPI_MISO (input).",
        "Everything on the panel runs at 3.3 V from the Tang Nano's 3V3 pin. No 5 V anywhere on the panel.",
    ])
    return fig


# ================================================================ sheet 2
def sheet_carrier():
    fig, fr = page(2, N, "Carrier board and panel connector", "Carrier and connector")

    ax = canvas(fig, [0.03, 0.33, 0.48, 0.58])
    d = schemdraw.Drawing(canvas=ax, show=False)
    tn = d.add(ic([], [("3V3", "3V3", "V33"), ("SPI_SCK", "IO a", "sck"), ("SPI_MOSI", "IO b", "mosi"),
                       ("SPI_CS_n", "IO c", "cs"), ("SPI_MISO", "IO d", "miso"),
                       ("SPARE1", "IO e", "sp1"), ("SPARE2", "IO f", "sp2"),
                       ("SPARE3", "IO g", "sp3"), ("SPARE4", "IO h", "sp4"), ("GND", "GND", "G")],
                  None, None, (6, 12), "Tang Nano 9K  (on female headers)", loc="top"))
    d.add(elm.Line().at(tn.V33).right(1)); d.add(elm.Line().up(0.5)); d.add(elm.Vdd().label("3V3"))
    for a, net, r in [("sck", "SPI_SCK", "R1"), ("mosi", "SPI_MOSI", "R2"), ("cs", "SPI_CS_n", "R3")]:
        d.add(elm.Line().at(getattr(tn, a)).right(1))
        d.add(elm.Resistor().right().length(3).label(f"{r}  33 Ω", fontsize=FS - 1))
        d.add(elm.Line().right(0.5)); tag(d, net)
    for a, net in [("miso", "SPI_MISO"), ("sp1", "SPARE1"), ("sp2", "SPARE2"),
                   ("sp3", "SPARE3"), ("sp4", "SPARE4")]:
        d.add(elm.Line().at(getattr(tn, a)).right(4.5)); tag(d, net)
    d.add(elm.Line().at(tn.G).right(1)); d.add(elm.Ground())
    finish(d, ax)

    ax2 = canvas(fig, [0.55, 0.36, 0.20, 0.55])
    d = schemdraw.Drawing(canvas=ax2, show=False)
    nets = ["3V3", "GND", "SPI_SCK", "GND", "SPI_MOSI", "SPI_MISO", "GND", "SPI_CS_n", "SPARE1", "SPARE2",
            "GND", "SPARE3", "SPARE4", "3V3"]
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
        "R1–R3 (33 Ω series, close to the FPGA) tame ringing on the ribbon. On the breadboard, replace them with wires.",
        "Connector order puts a ground next to the clock (SPI_SCK at 3, between GND at 2 and 4) and next to CS_n (GND at 7).",
        "SPARE1–SPARE4 run to free FPGA pins: e.g. a shared RESET_n or INT line for the expanders, a buzzer, or a logic-analyser trigger.",
        "Pins 1 and 14 both carry 3V3. Total panel current ≈ 50 mA with 1 kΩ LED resistors, ≈ 110 mA with 470 Ω.",
        "SPI runs up to 10 MHz (MCP23S17 maximum). Start at 1 MHz on the breadboard and on long ribbons.",
    ], title="Notes")
    return fig


# ================================================================ sheet 3
def sheet_outputs():
    fig, fr = page(3, N, "Output expander: MCP23S17 driving 16 LEDs  (U1 shown; U2 alike, U3 uses GPA0–3 only)",
                   "Output expanders")
    ax = canvas(fig, [0.02, 0.12, 0.57, 0.80])
    d = schemdraw.Drawing(canvas=ax, show=False)
    u = mcp(d, "U1")
    bus_and_power(d, u, CHIPS["U1"][0])
    ends = []
    for k in range(16):
        a = f"GPA{k}" if k < 8 else f"GPB{k - 8}"
        d.add(elm.Line().at(getattr(u, a)).right(0.8))
        d.add(elm.Resistor().right().length(2.8).label(f"R{11 + k}  1 kΩ", fontsize=FS - 1))
        led = d.add(elm.LED().right().length(2.6).label(f"LED{1 + k}  A{k}", fontsize=FS - 1))
        ends.append(led.end)
    ground_bus(d, ends)
    finish(d, ax)

    table(fig, [0.61, 0.62, 0.36, 0.27], "Addresses and SPI opcodes",
          ["Chip", "A2 A1 A0", "Write", "Read", "Drives / reads"],
          [[ref, " ".join(addr), f"0x{0x40 | int(addr, 2) << 1:02X}", f"0x{0x41 | int(addr, 2) << 1:02X}", role]
           for ref, (addr, role) in CHIPS.items()],
          [0.08, 0.13, 0.09, 0.09, 0.61], fs=8)
    notes(fr, 0.61, 0.58, [
        "Common to all five chips: CS (11) = SPI_CS_n, SCK (12) = SPI_SCK,",
        "SI (13) = SPI_MOSI, SO (14) = SPI_MISO, VDD (9) = 3V3, VSS (10) = GND,",
        "100 nF at pin 9. INTA (20) and INTB (19) unconnected.",
        "RESET (18): one 10 kΩ pull-up, R9, to 3V3 shared by all five.",
        "A2–A0 (17–15): tied to 3V3 or GND to set each chip's address.",
        "",
        "LEDs active high: GPx → resistor → anode, cathode → GND.",
        "1 kΩ ≈ 1.3 mA per LED; 470 Ω ≈ 3 mA. Worst case per chip 16 × 3 mA",
        "= 48 mA, within the 125 mA limit into VDD (25 mA per pin).",
        "Designators: U1 uses R11–R26 / LED1–LED16; U2 R31–R46 / LED17–LED32;",
        "U3 R51–R54 / LED33–LED36.",
        "",
        "Update: per chip, CS low, opcode, 0x14 (OLATA), GPA byte, GPB byte, CS high.",
        "32 clocks, 3.2 µs at 10 MHz; all three output chips ≈ 10 µs.",
    ], title="Notes")
    return fig


# ================================================================ sheet 4
def sheet_inputs():
    fig, fr = page(4, N, "Input expander: MCP23S17 reading 16 switches  (U4 shown; U5 has the control toggles)",
                   "Input expanders")
    ax = canvas(fig, [0.02, 0.12, 0.50, 0.80])
    d = schemdraw.Drawing(canvas=ax, show=False)
    u = mcp(d, "U4")
    bus_and_power(d, u, CHIPS["U4"][0])
    ends = []
    for k in range(16):
        a = f"GPA{k}" if k < 8 else f"GPB{k - 8}"
        d.add(elm.Line().at(getattr(u, a)).right(0.8))
        sw = d.add(elm.Switch().right().length(2.6).label(f"SA{k}", fontsize=FS - 1, loc="bottom"))
        ends.append(sw.end)
    ground_bus(d, ends)
    finish(d, ax)

    ax2 = canvas(fig, [0.55, 0.62, 0.20, 0.27])
    d = schemdraw.Drawing(canvas=ax2, show=False)
    sw = d.add(elm.SwitchSpdt2().right().scale(1.8))
    d.add(elm.Label().at((sw.a.x - 1.6, sw.a.y + 1.2))
          .label("S17  STOP/RUN\nmomentary (ON)-OFF-(ON)", fontsize=FS - 1))
    d.add(elm.Line().at(sw.a).left(0.6)); d.add(elm.Line().down(1.6)); d.add(elm.Ground())
    d.add(elm.Line().at(sw.b).up(0.6)); d.add(elm.Line().right(2.2)); tag(d, "U5 GPA0  (STOP)", k=TK)
    d.add(elm.Line().at(sw.c).down(0.6)); d.add(elm.Line().right(2.2)); tag(d, "U5 GPB0  (RUN)", k=TK)
    finish(d, ax2)
    fr.text(0.65, 0.60, "Control toggle wiring: common to GND, one side per expander input.\n"
            "UP side on U5 port A, DOWN side on the same bit of port B.\n"
            "Centre = both open; held up = GPA bit closed; held down = GPB bit closed.",
            ha="center", va="top", fontsize=8.5)

    table(fig, [0.77, 0.62, 0.20, 0.27], "Input chips",
          ["Chip", "Port A", "Port B"],
          [["U4", "SA0–SA7", "SA8–SA15"], ["U5", "UP side", "DOWN side"]],
          [0.2, 0.4, 0.4], fs=8.5)

    notes(fr, 0.55, 0.50, [
        "No external pull-ups: the MCP23S17's internal weak pull-ups (GPPU) hold every",
        "input high, so the switch only has to pull it to GND.",
        "",
        "Polarity: with IPOL = 0xFF the chip inverts each input bit, so a closed switch",
        "reads 1 and the HDL needs no inversion.",
        "",
        "Unused U3 pins are configured as outputs, so nothing on the panel floats.",
        "Breadboard stages: an 8-way DIP switch replaces eight toggles directly.",
        "",
        "Read: per chip, CS low, opcode (read), 0x12 (GPIOA), then clock out the GPA",
        "and GPB bytes on SO, CS high. 32 clocks, 3.2 µs at 10 MHz.",
        "Only the addressed chip drives SO, so all five can share SPI_MISO.",
        "Debounce in the HDL: sample at ~1 kHz, accept a change after ~5 stable reads.",
    ], title="Notes")
    return fig


# ================================================================ sheet 5
def sheet_maps():
    fig, fr = page(5, N, "Bit maps, start-up and breadboard subsets", "Bit maps, start-up")
    led_rows = [
        ["U1 GPA", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"],
        ["U1 GPB", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15"],
        ["U2 GPA", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"],
        ["U2 GPB", "MEMR", "INP", "M1", "OUT", "HLTA", "STACK", "WO", "INT"],
        ["U3 GPA", "INTE", "PROT", "WAIT", "HLDA", "–", "–", "–", "–"],
        ["U3 GPB", "–", "–", "–", "–", "–", "–", "–", "–"]]
    table(fig, [0.03, 0.62, 0.45, 0.28], "LED map  (led[n]: same order as the shift-register backend)",
          ["Port", "bit 0", "1", "2", "3", "4", "5", "6", "7"], led_rows, [0.12] + [0.11] * 8)
    sw_rows = [
        ["U4 GPA", "SA0", "SA1", "SA2", "SA3", "SA4", "SA5", "SA6", "SA7"],
        ["U4 GPB", "SA8", "SA9", "SA10", "SA11", "SA12", "SA13", "SA14", "SA15"],
        ["U5 GPA", "STOP", "SSTEP", "EXAM", "DEP", "RESET", "PROT", "AUX1↑", "AUX2↑"],
        ["U5 GPB", "RUN", "spare", "EX NXT", "DEP NXT", "CLR", "UNPROT", "AUX1↓", "AUX2↓"]]
    table(fig, [0.52, 0.62, 0.45, 0.28], "Switch map  (sw[n]: same order as the shift-register backend)",
          ["Port", "bit 0", "1", "2", "3", "4", "5", "6", "7"], sw_rows, [0.12] + [0.11] * 8)

    init_rows = [
        ["1", "0x40", "0x0A IOCON", "0x08", "HAEN = 1 in all five (until then, all answer to 000)"],
        ["2", "0x40, 0x42, 0x44", "0x00 IODIRA, IODIRB", "0x00, 0x00", "U1–U3: all 16 pins outputs"],
        ["3", "0x46, 0x48", "0x02 IPOLA, IPOLB", "0xFF, 0xFF", "U4, U5: closed switch reads 1"],
        ["4", "0x46, 0x48", "0x0C GPPUA, GPPUB", "0xFF, 0xFF", "U4, U5: internal pull-ups on"],
    ]
    table(fig, [0.03, 0.34, 0.62, 0.22], "Start-up writes  (BANK = 0, SEQOP = 0: the A and B registers follow each other)",
          ["Step", "Opcodes", "Register", "Data", "Effect"], init_rows, [0.06, 0.19, 0.20, 0.11, 0.44], fs=8.5)

    bb_rows = [
        ["Stage 1", "U1 + LED1–LED8 + R11–R18", "SCK, MOSI, CS_n", "Binary counter on 8 LEDs (GPA)"],
        ["Stage 2", "+ U4 + 8-way DIP switch on GPA", "+ MISO", "DIP switches mirrored on LEDs"],
        ["Stage 3", "+ 8 LEDs on U1 GPB + 2nd DIP on U4 GPB", "same four signals", "16 bits each way, PWM brightness"],
    ]
    table(fig, [0.03, 0.12, 0.62, 0.17], "Breadboard subsets  (no J1/J2, wire FPGA pins directly)",
          ["", "Parts added", "FPGA signals used", "Goal"], bb_rows, [0.09, 0.37, 0.20, 0.34], fs=8.5)

    notes(fr, 0.68, 0.56, [
        "Refresh loop:",
        "•  write OLATA/OLATB (0x14) of U1, U2, U3",
        "•  read GPIOA/GPIOB (0x12) of U4, U5",
        "≈ 16 µs per pass at 10 MHz, so 8-bit PWM on",
        "the LEDs still runs at a few hundred Hz.",
        "",
        "Step 1 relies on HAEN starting at 0. Some",
        "MCP23S17 silicon decodes A2 even then; also",
        "sending step 1 with opcode 0x48 covers U5",
        "either way (see the errata sheet).",
        "",
        "Breadboard rules:",
        "•  3V3 and GND from the Tang Nano only.",
        "•  100 nF at pin 9 of every expander.",
        "•  RESET_n pulled up; A2–A0 never left open.",
        "•  Clip the analyser on SCK, MOSI, MISO, CS_n.",
    ], size=10)
    return fig


SHEETS = [sheet_block, sheet_carrier, sheet_outputs, sheet_inputs, sheet_maps]
