#!/bin/sh

set -e

cd $(dirname "$0")

./tree.pkg.sh

file /usr/local/lib/ghdl_yosys.so

./todo.sh
