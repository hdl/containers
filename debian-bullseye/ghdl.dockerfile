# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
#     <unai.martinezcorral@ehu.eus>
#   Niklaus Leuenberger
#     <niklaus.leuenb@gmail.com>
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

ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

#---

FROM $REGISTRY/build/build AS build-mcode

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    gcc gnat libz-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ghdl/ghdl /tmp/ghdl \
 && mkdir /tmp/ghdl/build \
 && cd /tmp/ghdl/build \
 && ../configure --prefix=/opt/ghdl \
 && make \
 && make install

#---

FROM scratch AS pkg-mcode

COPY --from=build-mcode /opt/ghdl /ghdl/usr/local/

#---

FROM ghdl/pkg:bullseye-llvm-11 AS build-llvm

# TODO Build GHDL on $REGISTRY/build/build instead of picking ghdl/pkg:bullseye-mcode

#---

FROM scratch AS pkg-llvm

COPY --from=build-llvm / /ghdl/usr/local/

#--

FROM $REGISTRY/build/base AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-9 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#--

FROM base AS mcode

COPY --from=build-mcode /opt/ghdl /usr/local/

#--

FROM base AS llvm

COPY --from=build-llvm / /usr/local/

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    gcc \
    libllvm11 \
    zlib1g-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists
