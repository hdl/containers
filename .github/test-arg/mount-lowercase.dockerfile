# syntax=docker/dockerfile:1.2

ARG registry='docker.io/hdlc'

FROM $registry/build:build AS build

ARG registry

RUN --mount=type=cache,from=$registry/pkg:icestorm,src=/icestorm/usr/local/share/icebox,target=/usr/local/share/icebox \
  ls -la /usr/local/share/icebox
