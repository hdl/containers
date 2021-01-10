#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./env.sh

python3 --version

curl --version
