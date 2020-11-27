#!/usr/bin/env sh

cd $(dirname "$0")

asciidoctor -r asciidoctor-diagram index.adoc
