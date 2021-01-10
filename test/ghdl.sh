#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

./smoke-tests/ghdl.sh

ghdl --version
