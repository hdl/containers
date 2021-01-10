#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

./nextpnr--ecp5.sh
./prjtrellis.sh
