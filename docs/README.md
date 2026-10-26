# Write-ups

One chapter per stage of the build, in LaTeX, sharing `chapter.sty`. The list of chapters is [`index.md`](index.md), generated from `index.tex`.

Run `./build.sh`, then start from `build/index.pdf`. It needs lualatex and latexmk (TeX Live), pandoc, rsvg-convert, kicad-cli, uv for the Python figure scripts and the notebook, and, for the RTL drawings, Yosys and netlistsvg, set up as in the repo’s README. The schematic PDFs it links to come from `../diagrams/build_pdfs.py`. The parts list is [`parts.md`](parts.md).

`data/` holds the numbers the chapters plot, written by the notebooks in `../diagrams/` (`debounce.dat` by `debounce.ipynb`). It is not committed: `build.sh` runs the notebook when the `.dat` is missing or older than it.
