#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

./smoke-tests/nextpnr-ice40.sh

./todo.sh
