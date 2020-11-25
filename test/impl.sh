#!/usr/bin/env sh

set -e

cd $(dirname "$0")

echo "CC: $CC"
echo "CXX: $CXX"

./smoke-tests/ghdl.sh
./smoke-tests/nextpnr.sh
./smoke-tests/yosys.sh

ghdl --version
yosys --version
