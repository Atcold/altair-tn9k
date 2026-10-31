# Writing the chapters

How the write-ups in `docs/` explain things and give building instructions, learnt from review rounds on the e-ink drafts.

## Order and names

- `docs/roadmap.tex` is the order of work: parts (numbered, one new idea each) and their lessons (lettered, one chapter each), with what each lesson needs, whether it is built and whether it has been read. Update it when a lesson is built or read; it holds no ‘next’ line.
- `docs/index.tex` lists the finished write-ups and is the source of `docs/index.md`, the documentation page.
- Part and lesson numbers live only in those two files.
- Each lesson stands alone: it never refers to another lesson, before or after it, and repeats what it needs from one.
- Schematics of breadboards are drawn in KiCad by the reader, as part of the learning; a new chapter gets a skeleton of headings, not a drawing.
- `docs/assets/` holds files from the makers that the chapters need, agreed with the owner one by one and committed as they come (*e.g.* Sipeed's board drawing); a chapter crops them when it includes them. Build output, PDFs included, stays out of git.
- Paths and commands match the repo: `rtl/<design>/<design>.v` and `.cst`, `make <command> <design>`.

## Shape of a chapter

- It opens with a small TikZ block diagram: the parts and the signals between them, high level, so the reader sees what the chapter is about before reading it.
- It leads with what is new: the board or chip this stage adds, and its pins, first.
- Pins are drawn, not tabled, in one figure of two halves. Left, in TikZ, two boxes: the FPGA chip, titled by its name, `GW1NR-9`, with the design's port names inside and its pin numbers (the `.cst` ones) on its edge; and the Tang Nano 9K around it, with the 27 MHz crystal as a `crystal` pic and the header pins on its edge. Right, `\boardpins` from `chapter.sty`: Sipeed's drawing, small and upright with the USB-C at the top, the pins used circled and tagged. Header pins are named by row and position, L (left) or R (right), counted from the USB-C end, *e.g.* R23 for GND; the board's printed labels sit underneath and can't be read on a breadboard. Each wire's destination is outside, with that chip's own pin numbers, and the lines run straight where they can.
- Every pin a chapter uses is checked in the board's schematic, header connectors included: an FPGA pin that reaches no header cannot be wired or probed.
- The Verilog sits under *Register-transfer level design*, one block at a time, in the order of the file: each block is a listing (`\inputminted` with `firstline` and `lastline`) followed by its explanation, and each piece of notation is explained in the block where it first appears. The whole file lives in the repo, and the chapter names its path.

## Explaining

- Every sentence is a full English sentence, with a subject and a verb. No fragments, no label-and-colon openings (‘The FPGA’s job: send …’), and no chains of appositives or semicolons; split them into sentences.
- Lessons are for any reader: nothing about the owner's own setup (two Macs, tmux keys, hub names). Installing software lives in the repo's README; a lesson says ‘installed as in the README’.
- Build each idea in order, as a textbook does: what the thing is, then this design's parts and how they connect, with a figure, then the details. The owner's review questions are answered in chat; the lesson states things plainly and never argues with a doubt, ‘strictly’, ‘in fact’, or ‘X too’.
- A new concept comes with reading: the sections of the owner's books that teach it (section, title, printed pages), listed in the lesson under *Reading first*, before the diagrams and the code that use it. The books stay in that list and the bibliography: the lesson's own text speaks in its own voice, with no ‘as in …’ or section numbers.
- Prose reasons with concepts: ‘the FPGA’, ‘the logic analyser’. Wiring diagrams name the FPGA chip by its model, `GW1NR-9`; other parts go by what they do (‘USB-serial bridge’, ‘analyser’), with the model small where it helps (`BL702`). Anything more, such as which clone the analyser is, goes in the caption.
- Every signal abbreviation gets its full name at least once (`SER` serial input, `SRCLK` shift-register clock, `RCLK` register clock), as in the KiCad schematics. The names carry the meaning that lets the reader reason about which line moves when.
- Show the numbers behind a choice, so the reader can compare them and learn the rule: all the datasheet's voltage columns, then why one is picked. A conclusion alone (‘the safe bound’) explains nothing.
- Every number from a datasheet or schematic is cited: document, section, page, with the document in the bibliography. Claims about the board (regulator, USB power) are checked in its schematic and the part's datasheet, with the numbers.
- Timing: nanoseconds from the datasheet, then cycles of the 27 MHz system clock (`sys_clk`, 37 ns), with a timing diagram counted in cycles.
- Diagrams use solid lines only, thin and grey for outlines: dashed lines shimmer on e-ink. TikZ's default arrow tips and line width for wires and arrows; `thick` only for components (chips, boxes, the crystal).
- Tables: numbered rows, so the reader can point at one; units in the header, never in the cells; numbers right-aligned, one number per cell.
- Whatever was run to check a design (a simulation, a testbench, a measurement) goes into the repo and into the chapter, with its code and its output: it is part of the lesson.

## Verilog conventions

- `sys_clk` is the board's 27 MHz pin, named only at the top level and in the `.cst`. Inside every module the clock port is `clk`; the top level wires `sys_clk`, or a clock derived from it, into it.
- Active-low signals end in `_n` (`rst_n`, `cs_n`). Verilog names can't start with `~`, which is the NOT operator; Digital's `~` prefix and KiCad's `~{…}` are only how those tools draw the overline.
- A convention is explained in the chapter where the reader first meets it.

## Building instructions

- Describe the smallest change to what is already on the bench: move the wires that must move, leave the rest where it is, and say what is left in place.
- When a step leaves something in a new state (an input without its pull-down), state the consequence and what deals with it.

## Review rounds

- Changed or added material in a document the reader has already read gets a review hand, `\here[what changed]`. A new document has none: all of it is new.
- After a round, the hands in the part the reader has read are cleared; hands below the point where the reading stopped stay, since they are still unseen.
- Feedback is read from the annotated PDF: the highlighted text with each note’s typed content.
