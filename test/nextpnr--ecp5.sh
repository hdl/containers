#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

./smoke-tests/nextpnr-ecp5.sh

./todo.sh
