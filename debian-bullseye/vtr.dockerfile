# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
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

ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

#---

FROM $REGISTRY/build/dev as build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    bison \
    build-essential \
    cmake \
    flex \
    fontconfig \
    gperf \
    libcairo2-dev \
    libgtk-3-dev \
    libfontconfig1-dev \
    liblist-moreutils-perl \
    libreadline-dev \
    libx11-dev \
    libxft-dev \
    ninja-build \
    tcl-dev \
    wget \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/verilog-to-routing/vtr-verilog-to-routing.git /tmp/vtr \
 && mkdir -p /tmp/vtr/build \
 && cd /tmp/vtr/build \
 && cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="/usr/local" .. \
 && cmake --build ./ \
 && DESTDIR=/opt/vtr cmake --build ./ --target install

#---

FROM scratch AS pkg

COPY --from=build /opt/vtr /vtr

#---

FROM $REGISTRY/build/base

COPY --from=build /opt/vtr /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgtk-3-bin \
 && apt-get autoclean -y && apt-get clean -y && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

CMD ["vpr"]
