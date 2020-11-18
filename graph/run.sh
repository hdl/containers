#!/usr/bin/env sh

cd $(dirname "$0")

dot -Tsvg graph.dot -o graph.svg
