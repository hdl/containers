# Authors:
#   Sebastian Birke
#     <git@se-bi.de>
#   Anton Blanchard
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

ARG REGISTRY='ghcr.io/hdl/debian/bullseye'

#---

FROM $REGISTRY/build/base AS base
ARG REGISTRY

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#---

FROM $REGISTRY/build/dev AS build
ARG REGISTRY

ENV LDFLAGS="-Wl,--copy-dt-needed-entries"

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${makedepends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/* \
 && clone

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/icestorm AS pkg-icestorm

FROM $REGISTRY/build/nextpnr/build AS build-ice40
ARG REGISTRY
COPY --from=pkg-icestorm /icestorm/usr/local/share/icebox /usr/local/share/icebox

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build ice40

#---

FROM scratch AS pkg-ice40
COPY --from=build-ice40 /opt/nextpnr /nextpnr-ice40

#---

FROM $REGISTRY/build/nextpnr/base AS ice40
COPY --from=build-ice40 /opt/nextpnr /

#---

FROM ice40 AS icestorm
COPY --from=pkg-icestorm /icestorm /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/prjtrellis AS pkg-prjtrellis

FROM $REGISTRY/build/nextpnr/build AS build-ecp5
ARG REGISTRY
COPY --from=pkg-prjtrellis /prjtrellis /

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build ecp5

#---

FROM scratch AS pkg-ecp5
COPY --from=build-ecp5 /opt/nextpnr /nextpnr-ecp5

#---

FROM $REGISTRY/build/nextpnr/base AS ecp5
COPY --from=build-ecp5 /opt/nextpnr /

#---

FROM ecp5 AS prjtrellis
COPY --from=pkg-prjtrellis /prjtrellis /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/prjoxide AS pkg-prjoxide

FROM $REGISTRY/build/nextpnr/build AS build-nexus
ARG REGISTRY
COPY --from=pkg-prjoxide /prjoxide /

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build nexus

#---

FROM scratch AS pkg-nexus
COPY --from=build-nexus /opt/nextpnr /nextpnr-nexus

#---

FROM $REGISTRY/build/nextpnr/base AS nexus
COPY --from=build-nexus /opt/nextpnr /

#---

FROM nexus AS prjoxide
COPY --from=pkg-prjoxide /prjoxide /

#---

FROM $REGISTRY/build/nextpnr/build AS build-generic
ARG REGISTRY

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build generic

#---

FROM scratch AS pkg-generic
COPY --from=build-generic /opt/nextpnr /nextpnr-generic

#---

FROM $REGISTRY/build/nextpnr/base AS generic
COPY --from=build-generic /opt/nextpnr /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/nextpnr/ice40 AS pkg-nextpnr-ice40
FROM $REGISTRY/pkg/nextpnr/ecp5 AS pkg-nextpnr-ecp5
FROM $REGISTRY/pkg/nextpnr/nexus AS pkg-nextpnr-nexus

FROM $REGISTRY/build/nextpnr/base
COPY --from=build-generic /opt/nextpnr /
COPY --from=pkg-nextpnr-ice40 /nextpnr-ice40 /
COPY --from=pkg-nextpnr-ecp5 /nextpnr-ecp5 /
COPY --from=pkg-nextpnr-nexus /nextpnr-nexus /
