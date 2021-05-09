# Authors:
#   Unai Martinez-Corral
#   Torsten Meissner
#
# Copyright 2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

ARG REGISTRY='ghcr.io/hdl/debian-buster'

#---

FROM $REGISTRY/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    binutils \
    cmake \
    autoconf \
    libgmp-dev \
    m4 \
    python3-toml \
    openjdk-11-jre-headless \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/pono && cd /tmp/pono \
 &&  curl -fsSL https://codeload.github.com/upscale-project/pono/tar.gz/master | tar xzf - --strip-components=1 \
 && ./contrib/setup-smt-switch.sh \
 && ./contrib/setup-bison.sh \
 && ./contrib/setup-flex.sh \
 && ./contrib/setup-btor2tools.sh \
 && ./configure.sh \
 && make -C build -j$(nproc) PREFIX=/usr/local/ \
 && mkdir -p /opt/pono/usr/local/bin /opt/pono/usr/local/lib \
 && cp build/pono /opt/pono/usr/local/bin/ \
 && cp build/libpono.so /opt/pono/usr/local/lib/

#---

FROM scratch
COPY --from=build /opt/pono /pono
