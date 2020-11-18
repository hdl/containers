#!/usr/bin/env sh

cd $(dirname "$0")

asciidoctor index.adoc
dot -Tsvg ../graph/graph.dot -o ./graph.svg
