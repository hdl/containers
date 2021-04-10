#!/usr/bin/env sh

set -e

cd $(dirname "$0")

git clone https://github.com/tgingold/ghdlsynth-beta
./ghdlsynth-beta/examples/icezum/test.sh

git clone https://github.com/antonblanchard/ghdl-yosys-blink
cd ghdl-yosys-blink
make vhdl_blink.bit
cd ..
