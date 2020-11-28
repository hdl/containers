#!/usr/bin/env sh

set -e

cd $(dirname "$0")

./gen_tool_table.py
asciidoctor -r asciidoctor-diagram index.adoc
