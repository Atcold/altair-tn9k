SRC    ?= $(firstword $(wildcard rtl/$(TOP) ide/$(TOP)/src))
DEVICE  = GW1NR-LV9QN88PC6/I5
FAMILY  = GW1N-9C
DESIGNS = $(sort $(notdir $(wildcard rtl/*)) $(patsubst ide/%/src,%,$(wildcard ide/*/src)))

.DEFAULT_GOAL := help

# The design is the word after the command, make load led. Every word is also a goal, so
# each design is a target that does nothing.
TOP := $(firstword $(filter $(DESIGNS),$(MAKECMDGOALS)))
$(DESIGNS): ; @:

# A word that is neither a command nor a design is a mistyped design.
UNKNOWN = $(filter-out build load flash rtl list help $(DESIGNS),$(MAKECMDGOALS))
ifneq ($(UNKNOWN),)
  $(error No design called $(UNKNOWN): it is one of: $(DESIGNS))
endif

# Every command but help and list works on one design.
ifneq ($(filter-out help list $(DESIGNS),$(MAKECMDGOALS)),)
  ifeq ($(TOP),)
    $(error No design: add one, make <command> <design>, from: $(DESIGNS))
  endif
endif

build: build/$(TOP).fs

build/$(TOP).fs: $(SRC)/$(TOP).v $(SRC)/$(TOP).cst
	mkdir -p build
	yosys -q -p "read_verilog $<; synth_gowin -top $(TOP) -json build/$(TOP).json"
	nextpnr-himbaechel --json build/$(TOP).json --write build/$(TOP)-pnr.json \
	    --device $(DEVICE) --vopt family=$(FAMILY) --vopt cst=$(SRC)/$(TOP).cst
	gowin_pack -d $(FAMILY) -o $@ build/$(TOP)-pnr.json

load: build/$(TOP).fs
	openFPGALoader -b tangnano9k $<

flash: build/$(TOP).fs
	openFPGALoader -b tangnano9k -f $<

rtl: $(SRC)/$(TOP).v
	mkdir -p build docs/fig
	yosys -q -p "read_verilog $<; prep -top $(TOP); write_json build/$(TOP)-rtl.json"
	netlistsvg build/$(TOP)-rtl.json --skin diagrams/rtl-skin.svg -o docs/fig/$(TOP)-rtl.svg
	diagrams/rtl_colour.py build/$(TOP)-rtl.json docs/fig/$(TOP)-rtl.svg

list:
	@printf '%s\n' $(DESIGNS)

# Bold and cyan only on a terminal, so piped help stays plain text.
help:
	@if [ -t 1 ]; then b=$$(tput bold); c=$$(tput setaf 6); n=$$(tput sgr0); fi; \
	printf "$${b}<design>$${n}                  one of $${c}make list$${n}\n\n"; \
	printf "$${c}make build$${n} $${b}<design>$${n}       build the bitstream, build/<design>.fs\n"; \
	printf "$${c}make load$${n} $${b}<design>$${n}        load it into the FPGA's RAM: gone at power-off\n"; \
	printf "$${c}make flash$${n} $${b}<design>$${n}       write it to the onboard flash: runs at every power-up\n"; \
	printf "$${c}make rtl$${n} $${b}<design>$${n}         the RTL drawing, docs/fig/<design>-rtl.svg\n\n"; \
	printf "$${c}make list$${n}                 the designs\n"; \
	printf "$${c}make help$${n}                 this list; also plain make\n"

.PHONY: build load flash rtl list help
