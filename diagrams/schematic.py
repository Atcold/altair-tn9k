"""Shared drawing helpers for the schematic notebooks.

Page frame and title block, net tags, IC and flip-flop shapes, notes, tables,
light and dark themes, and multi-page PDF output. Sheets are plain functions
that return a matplotlib figure, so a notebook cell shows one by calling it.
"""
import re
from types import SimpleNamespace

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import schemdraw
import schemdraw.elements as elm

P = elm.IcPin
PAGE = (16.54, 11.69)  # A3 landscape, inches
TITLE = "Altair 8800 replica, Tang Nano 9K"
REV = "Rev A   2026-10-05"
AUTHOR = "Alfredo Canziani"
FS = 9

# ---------------------------------------------------------------- themes
LIGHT = dict(FG="k", BG="white", MUTED="#555", HDR="#eeeeee", RIBBON="#a06000", FILL={})
DARK = dict(FG="#e6e6e6", BG="#1b1d21", MUTED="#9aa0a6", HDR="#33363c", RIBBON="#c88a2a",
            FILL={"#f2f2f2": "#2a2d33", "#e8f0fb": "#1f3048", "#fff6e0": "#45391c",
                  "#f7f7f7": "#2a2d33", "#eaf7ea": "#1f3a26", "#eaf0fb": "#1f2c45",
                  "#ffffff": "#25282d"})
T = SimpleNamespace(dark=False)  # current theme; sheets read T.FG, T.MUTED, ...


def set_theme(dark=False):
    T.__dict__.update(DARK if dark else LIGHT)
    T.dark = dark
    plt.rcParams.update({"figure.facecolor": T.BG, "axes.facecolor": T.BG,
                         "savefig.facecolor": T.BG, "text.color": T.FG,
                         "patch.edgecolor": T.FG, "lines.color": T.FG})
    schemdraw.config(fontsize=FS, lw=1.1, color=T.FG, bgcolor=T.BG)


def fill(colour):
    """Light-theme fill colour, mapped to its dark counterpart when needed."""
    return T.FILL.get(colour, colour)


set_theme(False)


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
    """Draw a schemdraw Drawing into ax and fit the axes to it."""
    d.draw(show=False)  # the figure is shown, or saved, by whoever asked for the sheet
    bb = d.get_bbox()
    ax.set_xlim(bb.xmin - pad, bb.xmax + pad)
    ax.set_ylim(bb.ymin - pad, bb.ymax + pad)
    ax.set_aspect("equal", adjustable="box")


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
            cell.set_text_props(weight="bold"); cell.set_facecolor(T.HDR)
        else:
            cell.set_facecolor(T.BG)
        cell.set_edgecolor(T.FG); cell.get_text().set_color(T.FG)


# ---------------------------------------------------------------- symbols
def OV(s):
    """Overlined text, for active-low pin names."""
    return r"$\overline{\mathrm{" + s + r"}}$"


def ic(pinsL, pinsR, top, bot, size, label, loc="center"):
    """IC box. Side pins are (name, number, anchor[, invert]); top/bot are (name, number) or None."""
    def mk(p, side):
        inv = p[3] if len(p) > 3 else False
        return P(p[0], p[1], side=side, anchorname=p[2], invert=inv)
    pins = [mk(p, "L") for p in reversed(pinsL)] + [mk(p, "R") for p in reversed(pinsR)]
    if top: pins.append(P(*top, side="T"))
    if bot: pins.append(P(*bot, side="B"))
    return elm.Ic(pins=pins, size=size).label(label, loc, fontsize=FS + 3,
                                              ofst=0.4 if loc == "top" else None)


def ff(pinsT=(), w=2.2, h=2.4, label=""):
    """Rising-edge D flip-flop: D, C in; Q, Q-bar out; optional active-low pins on top."""
    L = FS
    pins = [P("C", side="L", anchorname="C", lblsize=L, pos=0.25),
            P("D", side="L", anchorname="D", lblsize=L, pos=0.62),
            P(OV("Q"), side="R", anchorname="QN", lblsize=L, pos=0.25),
            P("Q", side="R", anchorname="Q", lblsize=L, pos=0.62)]
    tpos = [0.5] if len(pinsT) == 1 else [0.25, 0.75]
    for (name, anc), pp in zip(pinsT, tpos):
        pins.append(P(name, side="T", anchorname=anc, invert=True, lblsize=L - 1, pos=pp))
    return elm.Ic(pins=pins, size=(w, h)).right().label(label, "bottom", fontsize=FS - 1, ofst=0.25)


def toggle(ax, x, y):
    """Small toggle-switch glyph for block diagrams: a round bush with a lever."""
    ax.plot([x, x + 0.45], [y, y + 1.1], color=T.FG, lw=2.2, solid_capstyle="round", zorder=3)
    ax.add_patch(plt.Circle((x, y), 0.55, fc=fill("#c8c8c8"), ec=T.FG, lw=0.6, zorder=4))


def tag(d, text, direction="right", k=(0.15, 0.9)):
    """Net-label tag sized to its text; k = (width per character, padding)."""
    visible = re.sub(r"\$\\overline\{\\mathrm\{(.*?)\}\}\$", r"\1", text)
    t = elm.Tag(width=k[0] * len(visible) + k[1]).label(text, fontsize=FS - 1)
    d.add(t.right() if direction == "right" else t.left())


def netlabel(d, at, text, direction="left", length=1.2, k=(0.15, 0.9)):
    d.add(elm.Line().at(at).length(length).theta(180 if direction == "left" else 0))
    tag(d, text, direction, k)


def supply(d, pin, cap="C 100 nF"):
    """Supply pin up to 3V3, with the decoupling capacitor branching off at a node."""
    lower = d.add(elm.Line().at(pin).up(0.7))
    d.add(elm.Dot())
    d.add(elm.Line().up(0.7)); d.add(elm.Vdd().label("3V3"))
    d.add(elm.Line().at(lower.end).left(1.2))
    d.add(elm.Capacitor().left().length(1.8).label(cap, fontsize=FS - 1))
    d.add(elm.Ground())


def nc(d, pin):
    """No-connect mark on an unused pin."""
    d.add(elm.NoConnect().at(pin).scale(0.55))


# ---------------------------------------------------------------- PDF
def save_pdf(path, sheets, title=TITLE, dark=False):
    """Render sheet functions into one multi-page PDF, in the given theme."""
    previous = T.dark
    set_theme(dark)
    try:
        with PdfPages(path) as pdf:
            info = pdf.infodict(); info["Title"] = title; info["Author"] = AUTHOR
            for draw in sheets:
                fig = draw()
                pdf.savefig(fig)
                plt.close(fig)
    finally:
        set_theme(previous)
