#!/bin/sh
# Build each write-up into build/<chapter>.pdf.
#
#   ./build.sh                    # every chapter
#   ./build.sh 595-by-hand.tex    # just this one
#
# Figures are drawn first by the scripts in ../diagrams/, and the KiCad schematics exported,
# as SVG into fig/: the SVGs are for the web page, and rsvg-convert turns each into the PDF
# that LaTeX includes. Both fig/ and build/ are build output and stay out of git.

set -eu
cd "$(dirname "$0")"

# The bounce simulation's numbers, data/debounce.dat, which the 595-by-hand chapter plots:
# rerun the notebook when they are missing or older than it. Jupyter's messages go to a log,
# shown only if the notebook fails.
if [ ! data/debounce.dat -nt ../diagrams/debounce.ipynb ]; then
    mkdir -p build
    uv run jupyter nbconvert --to notebook --execute --stdout \
        ../diagrams/debounce.ipynb >/dev/null 2>build/debounce-notebook.log ||
        { cat build/debounce-notebook.log; exit 1; }
fi

../diagrams/debounce_circuit.py >/dev/null
../diagrams/kicad_sheet.py ../kicad/74HC595-manual-test/74HC595-manual-test.kicad_sch fig >/dev/null
make -s -C .. rtl led       # fig/led-rtl.svg, the RTL drawing of the running LEDs
make -s -C .. rtl factory   # fig/factory-rtl.svg, the factory program's stand-in
for svg in fig/*.svg; do
    rsvg-convert -f pdf -o "${svg%.svg}.pdf" "$svg"
done

latexmk -quiet "$@"

# index.md, the Markdown copy of the index, for GitHub. pandoc does not read chapter.sty, so
# \name is defined for it here, as plain text.
{ printf '\\newcommand{\\name}[1]{#1}\n'; cat index.tex; } |
    pandoc -f latex -t gfm --wrap=none --lua-filter=index-md.lua -o index.md
