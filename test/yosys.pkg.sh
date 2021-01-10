#!/bin/sh

set -e

cd $(dirname "$0")

./tree.pkg.sh

./todo.sh
