# Authors:
#   Unai Martinez-Corral
#     <unai.martinezcorral@ehu.eus>
#
# Copyright Unai Martinez-Corral
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

ARG REGISTRY='ghcr.io/hdl/debian/trixie'

#--

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    gnat-14 \
    zlib1g-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

# NOTE: gnat-14 ships no unversioned 'gnatmake' alternative (unlike gnat-9/12)
RUN ln -s /usr/bin/gnatmake-14 /usr/bin/gnatmake

#---

FROM build AS build-mcode

RUN git clone https://github.com/ghdl/ghdl.git /tmp/ghdl \
 && mkdir /tmp/ghdl/build \
 && cd /tmp/ghdl/build \
 && ../configure --default-pic \
 && make GNATMAKE="gnatmake -j$(nproc)" \
 && make DESTDIR=/opt/ghdl install

#---

FROM scratch AS pkg-mcode

COPY --from=build-mcode /opt/ghdl /ghdl

#---

FROM build AS build-llvm

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libbacktrace-dev \
    llvm-19-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ghdl/ghdl.git /tmp/ghdl \
 && mkdir /tmp/ghdl/build \
 && cd /tmp/ghdl/build \
 && ../configure --default-pic --with-llvm-config=llvm-config-19 --with-backtrace-lib=$(dpkg -L libbacktrace-dev | grep libbacktrace.a) \
 && make GNATMAKE="gnatmake -j$(nproc)" \
 && make DESTDIR=/opt/ghdl install

#---

FROM scratch AS pkg-llvm

COPY --from=build-llvm /opt/ghdl /ghdl

#--

FROM $REGISTRY/build/base AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-14 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#--

FROM base AS mcode

COPY --from=build-mcode /opt/ghdl /

#--

FROM base AS llvm

COPY --from=build-llvm /opt/ghdl /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    gcc \
    libc-dev \
    libllvm19 \
    zlib1g-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
