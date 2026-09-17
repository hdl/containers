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

ARG REGISTRY='ghcr.io/hdl/debian/bullseye'
ARG IMAGE="build/base"

#---

FROM $REGISTRY/build/build AS build
ARG REGISTRY

ENV XYCE_OUTDIR=/usr/local/
ENV PATH="${PATH}:/tmp/xyce${XYCE_OUTDIR}bin"
ENV LIBRARY_PATH="${LIBRARY_PATH}:/tmp/xyce${XYCE_OUTDIR}lib"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/tmp/xyce${XYCE_OUTDIR}lib"
ENV CPATH="${CPATH}:/tmp/xyce${XYCE_OUTDIR}include"

WORKDIR /tmp/build/

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${makedepends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build

#---

FROM scratch AS pkg
COPY --from=build /tmp/xyce/ /xyce/

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/xyce AS pkg-xyce

FROM $REGISTRY/$IMAGE
ARG REGISTRY

COPY --from=pkg-xyce /xyce/ /

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
