#!/usr/bin/env sh

set -e

cd $(dirname "$0")

echo "CC: $CC"
echo "CXX: $CXX"

./smoke-tests/nextpnr-ice40.sh
