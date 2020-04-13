#!/usr/bin/env sh

set -e

. $(dirname $0)/utils.sh

cd $(dirname "$0")

#---

gstart "tgingold/ghdlsynth-beta"
git clone https://github.com/tgingold/ghdlsynth-beta
./ghdlsynth-beta/examples/icezum/test.sh
gend

#---

gstart "antonblanchard/ghdl-yosys-blink"
git clone https://github.com/antonblanchard/ghdl-yosys-blink
cd ghdl-yosys-blink
make vhdl_blink.bit
cd ..
gend
