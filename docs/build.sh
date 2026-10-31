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

# The testbenches' printouts, data/walk_tb.txt and data/hello_tb.txt, which their chapters show.
mkdir -p ../build data
iverilog -g2012 -o ../build/walk_tb ../sim/walk_tb.v ../rtl/walk/walk.v ../rtl/walkback/walkback.v
vvp -n ../build/walk_tb | grep -v '\$finish' > data/walk_tb.txt
iverilog -g2012 -o ../build/hello_tb ../sim/hello_tb.v ../rtl/hello/hello.v
vvp -n ../build/hello_tb | grep -v '\$finish' > data/hello_tb.txt

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

# Send each chapter's PDF to the review folder named in .review-dir, a one-line file kept out of
# git, when there is one. build/sent/ holds the copy last sent: a PDF in the review folder that
# differs from it has changed there, so it may carry annotations, and is kept.
review=$(cat .review-dir 2>/dev/null || true)
if [ -n "$review" ]; then
    mkdir -p build/sent
    for tex in ${@:-*.tex}; do
        name=$(basename "$tex" .tex).pdf
        [ "$name" = index.pdf ] && continue
        if [ -f "$review/$name" ] && ! cmp -s "$review/$name" "build/sent/$name"; then
            echo "kept $review/$name: changed since it was sent, so it may carry annotations"
            continue
        fi
        cmp -s "build/$name" "$review/$name" || {
            cp "build/$name" "$review/$name" && cp "build/$name" "build/sent/$name" && echo "sent $name"
        }
    done
fi
