# Authors:
#   Anton Blanchard
#   Sebastian Birke      <git@se-bi.de>
#   Unai Martinez-Corral
#
# Copyright 2019-2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

FROM hdlc/build:base AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libboost-all-dev \
    libomp5-7 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#---

FROM hdlc/build:dev AS build

ENV LDFLAGS "-Wl,--copy-dt-needed-entries"

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libeigen3-dev \
    libomp-dev \
 && git clone https://github.com/YosysHQ/nextpnr.git /tmp/nextpnr \
 && mkdir /tmp/nextpnr/build/

#---

FROM build AS build-ice40
COPY --from=hdlc/pkg:icestorm /icestorm/usr/local/share/icebox /usr/local/share/icebox

RUN cd /tmp/nextpnr/build \
 && cmake .. \
   -DARCH=ice40 \
   -DBUILD_GUI=OFF \
   -DBUILD_PYTHON=ON \
   -DUSE_OPENMP=ON \
 && make -j $(nproc) \
 && make DESTDIR=/opt/nextpnr install

#---

FROM base AS ice40
COPY --from=build-ice40 /opt/nextpnr /

#---

FROM ice40 AS icestorm
COPY --from=hdlc/pkg:icestorm /icestorm /

#---

FROM scratch AS pkg-ice40
COPY --from=build-ice40 /opt/nextpnr /nextpnr-ice40

#---

FROM build AS build-ecp5
COPY --from=hdlc/pkg:prjtrellis /prjtrellis /

RUN cd /tmp/nextpnr/build \
 && cmake .. \
   -DARCH=ecp5 \
   -DBUILD_GUI=OFF \
   -DBUILD_PYTHON=ON \
   -DUSE_OPENMP=ON \
 && make -j $(nproc) \
 && make DESTDIR=/opt/nextpnr install

#---

FROM base AS ecp5
COPY --from=build-ecp5 /opt/nextpnr /

#---

FROM ecp5 AS prjtrellis
COPY --from=hdlc/pkg:prjtrellis /prjtrellis /

#---

FROM scratch AS pkg-ecp5
COPY --from=build-ecp5 /opt/nextpnr /nextpnr-ecp5

#---

FROM build-ice40 AS build-generic
COPY --from=hdlc/pkg:prjtrellis /prjtrellis /

RUN cd /tmp/nextpnr/build \
 && cmake .. \
   -DARCH=generic \
   -DBUILD_GUI=OFF \
   -DBUILD_PYTHON=ON \
   -DUSE_OPENMP=ON \
 && make -j $(nproc) \
 && make DESTDIR=/opt/nextpnr install

#---

FROM base AS generic
COPY --from=build-generic /opt/nextpnr /

#---

FROM scratch AS pkg-generic
COPY --from=build-generic /opt/nextpnr /nextpnr-generic

#---

FROM base AS all
COPY --from=build-ice40 /opt/nextpnr /
COPY --from=build-ecp5 /opt/nextpnr /
COPY --from=build-generic /opt/nextpnr /
