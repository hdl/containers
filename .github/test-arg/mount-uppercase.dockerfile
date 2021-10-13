# syntax=docker/dockerfile:1.2

ARG REGISTRY='docker.io/hdlc'

FROM $REGISTRY/build:build AS build

ARG REGISTRY

RUN --mount=type=cache,from=$REGISTRY/pkg:icestorm,src=/icestorm/usr/local/share/icebox,target=/usr/local/share/icebox \
  ls -la /usr/local/share/icebox
