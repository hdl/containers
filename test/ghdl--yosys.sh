#!/usr/bin/env sh

set -e

cd $(dirname "$0")

echo "CC: $CC"
echo "CXX: $CXX"

ghdl --version
yosys --version
