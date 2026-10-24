# Write-ups

One chapter per stage of the build, in LaTeX, sharing `chapter.sty`. The list of chapters is [`index.md`](index.md), generated from `index.tex`.

Run `./build.sh`, then start from `build/index.pdf`. It needs lualatex and latexmk (TeX Live), pandoc, rsvg-convert, kicad-cli, and uv for the Python figure scripts. The schematic PDFs it links to come from `../diagrams/build_pdfs.py`. The parts list is [`parts.md`](parts.md).

`data/` holds the numbers the chapters plot, written by the notebooks in `../diagrams/` (`debounce.dat` by `debounce.ipynb`). It is not committed: run the notebook before the first build.
