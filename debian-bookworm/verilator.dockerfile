# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021-2023 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

ARG REGISTRY='gcr.io/hdl-containers/debian/bookworm'
ARG IMAGE="build/base"

#---

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    autoconf \
    bison \
    flex \
    help2man \
    libfl-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/verilator/verilator \
 && cd verilator \
 && autoconf \
 && ./configure \
 && make -j$(nproc) \
 && make DESTDIR=/opt/verilator install \
 && git clone https://github.com/veripool/vcddiff \
 && make -C vcddiff CC=$CC \
 && cp -p vcddiff/vcddiff /opt/verilator/usr/local/bin/vcddiff

#---

FROM scratch AS pkg
COPY --from=build /opt/verilator /verilator

#---

FROM $REGISTRY/$IMAGE

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    clang \
    make \
    perl \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/verilator /
CMD ["verilator"]
