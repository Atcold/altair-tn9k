"""Shared drawing helpers for the schematic notebooks.

Page frame and title block, net tags, IC and flip-flop shapes, notes, tables,
light and dark themes, and multi-page PDF output. Sheets are plain functions
that return a matplotlib figure, so a notebook cell shows one by calling it.
"""
import re
from types import SimpleNamespace

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.path import Path
import schemdraw
import schemdraw.elements as elm

P = elm.IcPin
PAGE = (16.54, 11.69)  # A3 landscape, inches
TITLE = "Altair 8800 replica, Tang Nano 9K"
REV = "Rev A   2026-10-05"
AUTHOR = "Alfredo Canziani"
FS = 9

# ---------------------------------------------------------------- themes
# Net colours: supply, ground, clocks, shift-register signals, SPI signals, the shared switch
# lines, chip-internal data and control, LEDs.
#   light: dark shades on white, for the PDFs
#   dark:  bright shades on dark grey, for the notebook
#   mono:  all black on white, block fills blank, for black-and-white printers
THEMES = {
    "light": dict(FG="black", BG="white", MUTED="#555555", HDR="#eeeeee", RIBBON="#a06000", FILL={},
                  SUPPLY="#c62828", GROUND="#1f4e79", CLOCK="#b36b00", SR="#2e7d32", MCP="#6a1b9a",
                  SHARED="#00838f", DATA="#4d7c0f", CONTROL="#ad1457", LED="#d32f2f"),
    "dark": dict(FG="#e6e6e6", BG="#1b1d21", MUTED="#9aa0a6", HDR="#33363c", RIBBON="#c88a2a",
                 FILL={"#f2f2f2": "#2a2d33", "#e8f0fb": "#1f3048", "#fff6e0": "#45391c",
                       "#f7f7f7": "#2a2d33", "#eaf7ea": "#1f3a26", "#eaf0fb": "#1f2c45",
                       "#ffffff": "#25282d"},
                 SUPPLY="#ff6b6b", GROUND="#8fa3bf", CLOCK="#ffc857", SR="#7bd88f", MCP="#c49bff",
                 SHARED="#5ccfe6", DATA="#9ece6a", CONTROL="#ff8fc6", LED="#ff5050"),
    "mono": dict(FG="black", BG="white", MUTED="#555555", HDR="#eeeeee", RIBBON="#777777",
                 FILL={c: "#ffffff" for c in ("#f2f2f2", "#e8f0fb", "#fff6e0", "#f7f7f7",
                                              "#eaf7ea", "#eaf0fb")},
                 SUPPLY="black", GROUND="black", CLOCK="black", SR="black", MCP="black",
                 SHARED="black", DATA="black", CONTROL="black", LED="black"),
}
T = SimpleNamespace(name="light")  # current theme; sheets read T.FG, T.MUTED, ...


def set_theme(name="light"):
    T.__dict__.update(THEMES[name])
    T.name = name
    plt.rcParams.update({"figure.facecolor": T.BG, "axes.facecolor": T.BG,
                         "savefig.facecolor": T.BG, "text.color": T.FG,
                         "patch.edgecolor": T.FG, "lines.color": T.FG})
    schemdraw.config(fontsize=FS, lw=1.1, color=T.FG, bgcolor=T.BG)


def fill(colour):
    """Light-theme fill colour, mapped to its dark counterpart when needed."""
    return T.FILL.get(colour, colour)


set_theme("light")


# ---------------------------------------------------------------- page
def page(n, of, heading, short):
    """A3 sheet with border, heading and title block. Returns (fig, frame axes)."""
    fig = plt.figure(figsize=PAGE)
    fr = fig.add_axes([0, 0, 1, 1]); fr.set_axis_off()
    fr.set_xlim(0, 1); fr.set_ylim(0, 1)
    fr.add_patch(plt.Rectangle((0.015, 0.02), 0.97, 0.96, fill=False, lw=1.5))
    x0, y0, w, h = 0.70, 0.02, 0.285, 0.085
    fr.add_patch(plt.Rectangle((x0, y0), w, h, fill=False, lw=1.2))
    fr.plot([x0, x0 + w], [y0 + h * 0.55] * 2, color=T.FG, lw=0.8)
    fr.text(x0 + 0.008, y0 + h * 0.75, TITLE, fontsize=12, weight="bold", va="center")
    fr.text(x0 + 0.008, y0 + h * 0.30, short, fontsize=11, va="center")
    fr.text(x0 + w - 0.008, y0 + h * 0.30, f"Sheet {n}/{of}   {REV}",
            fontsize=9, va="center", ha="right")
    fr.text(0.03, 0.955, heading, fontsize=17, weight="bold", va="top")
    return fig, fr


def canvas(fig, rect):
    ax = fig.add_axes(rect); ax.set_axis_off()
    return ax


def finish(d, ax, pad=0.6):
    """Draw a schemdraw Drawing into ax, fit the axes to it (tags included), then draw its tags."""
    d.draw(show=False)  # the figure is shown, or saved, by whoever asked for the sheet
    bb = d.get_bbox()
    x0, x1, y0, y1 = bb.xmin - pad, bb.xmax + pad, bb.ymin - pad, bb.ymax + pad
    # Tags are sized in points, so how much room they need depends on the drawing's scale:
    # widen the limits a few times until every tag fits.
    w_in = ax.get_position().width * ax.figure.get_figwidth()
    h_in = ax.get_position().height * ax.figure.get_figheight()
    for _ in range(3):
        units_per_pt = max((x1 - x0) / (w_in * 72), (y1 - y0) / (h_in * 72))  # equal aspect
        for p, text, direction, _c in getattr(d, "tags", []):
            reach = _tag_extent(text) * units_per_pt
            if direction == "left":
                x0 = min(x0, p.x - reach - pad)
            elif direction == "right":
                x1 = max(x1, p.x + reach + pad)
            else:
                y0 = min(y0, p.y - reach - pad)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal", adjustable="box")
    _draw_tags(d, ax)


def notes(fr, x, y, lines, size=10, title=None):
    if title:
        fr.text(x, y, title, fontsize=size + 1, weight="bold", va="top"); y -= 0.028
    for ln in lines:
        fr.text(x, y, ln, fontsize=size, va="top"); y -= 0.022 * (size / 10)
    return y


def table(fig, rect, title, cols, rows, widths, fs=9):
    ax = canvas(fig, rect); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0, 1.0, title, fontsize=11, weight="bold", va="top")
    t = ax.table(cellText=rows, colLabels=cols, colWidths=widths, loc="upper left",
                 bbox=[0, 0, 1, 0.90], cellLoc="left")
    t.auto_set_font_size(False); t.set_fontsize(fs)
    for (r, c), cell in t.get_celld().items():
        if r == 0:
            # math-mode text (overlined names) ignores weight, so make it bold math instead
            txt = cell.get_text()
            txt.set_text(txt.get_text().replace(r"\mathrm{", r"\mathbf{"))
            cell.set_text_props(weight="bold"); cell.set_facecolor(T.HDR)
        else:
            cell.set_facecolor(T.BG)
        cell.set_edgecolor(T.FG); cell.get_text().set_color(T.FG)


# ---------------------------------------------------------------- symbols
def OV(s):
    """Overlined text, for active-low pin names."""
    return r"$\overline{\mathrm{" + s + r"}}$"


def ic(pinsL, pinsR, top, bot, size, label, loc="center", lpad=None):
    """IC box. Side pins are (name, number, anchor[, invert]); top/bot are (name, number) or None.

    lpad: fraction of the height kept clear above and below the left-side pins, so a side with
    fewer pins doesn't run from corner to corner.
    """
    def mk(p, side, pos=None):
        inv = p[3] if len(p) > 3 else False
        return P(p[0], p[1], side=side, anchorname=p[2], invert=inv, pos=pos)
    if lpad is None:
        left = [mk(p, "L") for p in reversed(pinsL)]
    else:
        n = len(pinsL)
        step = (1 - 2 * lpad) / (n - 1)
        left = [mk(p, "L", 1 - lpad - i * step) for i, p in enumerate(pinsL)]  # top pin first
    pins = left + [mk(p, "R") for p in reversed(pinsR)]
    if top: pins.append(P(*top, side="T"))
    if bot: pins.append(P(*bot, side="B"))
    return elm.Ic(pins=pins, size=size).label(label, loc, fontsize=FS + 3,
                                              ofst=0.4 if loc == "top" else None)


def ff(pinsT=(), w=2.2, h=2.4, label="", qn=False):
    """Rising-edge D flip-flop: D and clock in, Q out (Q-bar too if qn); optional active-low pins on top."""
    L = FS
    # D and Q at mid-height: schemdraw centres a lone pin on a side, so this keeps D and Q level
    # (and the stage-to-stage links straight). With Q-bar drawn, Q and Q-bar spread apart instead,
    # so their output tags don't touch; only the last stage of a chain has Q-bar.
    pins = [P(">", side="L", anchorname="C", lblsize=L, pos=0.2),  # ">" draws the clock wedge
            P("D", side="L", anchorname="D", lblsize=L, pos=0.5),
            P("Q", side="R", anchorname="Q", lblsize=L, pos=0.75 if qn else 0.5)]
    if qn:
        pins.append(P(OV("Q"), side="R", anchorname="QN", lblsize=L, pos=0.25))
    tpos = [0.5] if len(pinsT) == 1 else [0.25, 0.75]
    for (name, anc), pp in zip(pinsT, tpos):
        pins.append(P(name, side="T", anchorname=anc, invert=True, lblsize=L - 1, pos=pp))
    return elm.Ic(pins=pins, size=(w, h)).right().label(label, "bottom", fontsize=FS - 1, ofst=0.25)


def toggle(ax, x, y):
    """Small toggle-switch glyph for block diagrams: a round bush with a lever."""
    ax.plot([x, x + 0.45], [y, y + 1.1], color=T.FG, lw=2.2, solid_capstyle="round", zorder=3)
    ax.add_patch(plt.Circle((x, y), 0.55, fc=fill("#c8c8c8"), ec=T.FG, lw=0.6, zorder=4))


def visible(text):
    """Tag text without its overline markup."""
    return re.sub(r"\$\\overline\{\\mathrm\{(.*?)\}\}\$", r"\1", text)


def net_colour(text):
    """Colour for a net, from its name: clocks first, then which backend it belongs to."""
    name = visible(text)
    if re.search(r"CLK|SCK", name):
        return T.CLOCK
    if re.match(r"S[WA]\d", name):  # switch lines
        return T.SHARED
    if re.match(r"(LED_|SW_)", name):
        return T.SR
    if name.startswith("SPI_"):
        return T.MCP
    if re.match(r"(SRCLR|OE|SH/LD|LOAD)", name):  # chip-internal control
        return T.CONTROL
    if re.match(r"(SER|Q[A-H]|[A-H] \(|shift |stage |from |to )", name):  # chip-internal data path
        return T.DATA
    return T.FG


def VDD():
    return elm.Vdd().color(T.SUPPLY)


def GND():
    return elm.Ground().color(T.GROUND)


def LED():
    return elm.LED().color(T.LED)


def to_gnd(d, at, *moves):
    """Ground lead from `at`, following moves such as ("left", 1.2), ("down", 0.6), then a ground symbol."""
    line = None
    for i, (direction, length) in enumerate(moves):
        seg = elm.Line().length(length).color(T.GROUND)
        seg = getattr(seg.at(at) if i == 0 else seg, direction)()
        line = d.add(seg)
    d.add(GND())
    return line


def ground_bus(d, ends, dx=0.8):
    """Common return: each end joins a vertical bus dx to the right, which goes to ground."""
    G = T.GROUND
    d.add(elm.Line().at(ends[0]).right(dx).color(G))
    bus = d.add(elm.Line().down(ends[0].y - ends[-1].y).color(G))
    for e in ends[1:]:
        d.add(elm.Line().at(e).right(dx).color(G)); d.add(elm.Dot().at((e.x + dx, e.y)).color(G))
    to_gnd(d, bus.end, ("down", 0.5))


TAG_FS = FS - 1   # tag text size, points
TAG_PAD = 0.35    # room around the text inside a tag, in multiples of the font size
TAG_TIP = 1.2     # how far a tag's point sticks out beyond its text box, same unit


def tag(d, text, direction="right", k=None):
    """Net-label tag at the drawing's current position (the end of the lead just drawn).

    The tag itself is a text box drawn by finish(), sized in points around the text, so tags are
    the same size on every sheet whatever the drawing's scale. direction is where the tag sits
    relative to the lead's end: "left", "right" or "down". k is accepted and ignored (old sizing).
    """
    if not hasattr(d, "tags"):
        d.tags = []
    d.tags.append((d.here, text, direction, net_colour(text)))


def _tag_extent(text):
    """Tag length in points, from the lead's end to the far side of the box (an estimate)."""
    return (0.62 * len(visible(text)) + 2 * TAG_PAD + TAG_TIP) * TAG_FS


def _tag_shape(point):
    """Box style for a tag: a box around the text with one pointed end, like schemdraw's Tag."""
    def style(x0, y0, w, h, mutation_size):
        pad = TAG_PAD * mutation_size
        x0, y0, w, h = x0 - pad, y0 - pad, w + 2 * pad, h + 2 * pad
        t = h / 2  # length of the point
        if point == "right":
            verts = [(x0, y0), (x0 + w, y0), (x0 + w + t, y0 + h / 2), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)]
        else:
            verts = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0 - t, y0 + h / 2), (x0, y0)]
        return Path(verts, closed=True)
    return style


def _draw_tags(d, ax):
    for p, text, direction, colour in getattr(d, "tags", []):
        off = TAG_TIP * TAG_FS  # the tag's point sits on the lead's end
        point, ha, va, xy_off, rot = {
            "left": ("right", "right", "center", (-off, 0), 0),   # tag left of the lead, pointing at it
            "right": ("left", "left", "center", (off, 0), 0),
            "down": ("right", "center", "top", (0, -off), 90),     # rotated: points up at the lead
        }[direction]
        ax.annotate(text, xy=(p.x, p.y), xytext=xy_off, textcoords="offset points",
                    ha=ha, va=va, rotation=rot, fontsize=TAG_FS, color=colour,
                    bbox=dict(boxstyle=_tag_shape(point), fc=T.BG, ec=colour, lw=0.9))


def netlabel(d, at, text, direction="left", length=1.2, k=(0.15, 0.9)):
    d.add(elm.Line().at(at).length(length).theta(180 if direction == "left" else 0).color(net_colour(text)))
    tag(d, text, direction, k)


def supply(d, pin, cap="C 100 nF"):
    """Supply pin up to 3V3, with the decoupling capacitor branching off at a node."""
    lower = d.add(elm.Line().at(pin).up(0.7).color(T.SUPPLY))
    d.add(elm.Dot().color(T.SUPPLY))
    d.add(elm.Line().up(0.7).color(T.SUPPLY)); d.add(VDD().label("3V3"))
    d.add(elm.Line().at(lower.end).left(1.2).color(T.SUPPLY))
    d.add(elm.Capacitor().left().length(1.8).label(cap, fontsize=FS - 1))
    d.add(GND())


def nc(d, pin, direction="right"):
    """No-connect mark on an unused pin: a short lead out from the pin, ending in an X."""
    # 1.0 visible, as long as a tag's lead, plus the X's half-width, since the X is centred on the end
    lead = d.add(elm.Line().at(pin).length(1.4).theta(180 if direction == "left" else 0))
    d.add(elm.NoConnect().at(lead.end).scale(1.6))


# ---------------------------------------------------------------- PDF
def save_pdf(path, sheets, title=TITLE, theme="light"):
    """Render sheet functions into one multi-page PDF, in the given theme."""
    previous = T.name
    set_theme(theme)
    try:
        with PdfPages(path) as pdf:
            info = pdf.infodict(); info["Title"] = title; info["Author"] = AUTHOR
            for draw in sheets:
                fig = draw()
                pdf.savefig(fig)
                plt.close(fig)
    finally:
        set_theme(previous)
