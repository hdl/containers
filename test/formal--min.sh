#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

./smoke-tests/ghdl.sh
./smoke-tests/symbiyosys.sh
./smoke-tests/yosys.sh
./smoke-tests/z3.sh

ghdl --version
yosys --version
