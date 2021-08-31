# Authors:
#   Unai Martinez-Corral
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

ARG REGISTRY='gcr.io/hdl-containers/debian/buster'

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
    libx11-dev \
    libxft-dev \
    ninja-build \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/verilog-to-routing/vtr-verilog-to-routing.git /tmp/vtr \
 && cd /tmp/vtr \
 && make PREFIX=/usr/local -j $(nproc) \
 && make DESTDIR=/opt/vtr PREFIX=/usr/local install

# FIXME: This should not be required, but the PREFIX in the previous step seems not to be honored.
RUN cd /opt/vtr \
 && mkdir usr \
 && mv tmp/vtr/build usr/local \
 && rm -rf tmp

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
