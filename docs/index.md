# Altair 8800 replica on a Tang Nano 9K: Write-ups

One chapter per stage of the build: what to wire, why, and how to tell it works.

## Stages

Stage 0a: open-source toolchain blink  
Blink an onboard LED from one .v file through both Gowin EDA and the open-source flow.

Stage 0b: hello world on the logic analyser  
A Verilog UART sends ‘Hello world’, read back by the logic analyser’s decoder and by a serial terminal.

[Stage 0c: one 74HC595 by hand](build/595-by-hand.pdf)  
Three buttons stand in for the FPGA: shift a byte in bit by bit, then latch it onto eight LEDs.

## Schematics

- [The 74HC595 and 74HC165 at flip-flop level](build/74hc595-74hc165-internals.pdf)

- [First byte: both backends on one breadboard](build/altair-first-byte-schematic.pdf)

- [Panel, shift-register backend](build/altair-panel-sr-schematic.pdf)

- [Panel, SPI-expander backend](build/altair-panel-mcp-schematic.pdf)

The parts list for both backends is docs/parts.md in the repo.

*Generated from index.tex by build.sh, which also builds the PDFs into build/. Edit index.tex, not this file.*
