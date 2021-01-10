#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

./nextpnr--ice40.sh
./icestorm.sh
