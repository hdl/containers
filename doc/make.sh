#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./gen_tool_table.py
asciidoctor \
  -r ./lib/GHAStatus-inline-macro.rb \
  -r asciidoctor-diagram \
  index.adoc
