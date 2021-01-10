#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

ghdl --version
yosys --version
