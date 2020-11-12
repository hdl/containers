FROM debian:buster-slim AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    ca-certificates \
    curl \
    make \
    python3 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

#---

FROM base AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    clang

ENV CC clang
ENV CXX clang++

#---

FROM build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    cmake \
    libboost-all-dev \
    python3-dev
