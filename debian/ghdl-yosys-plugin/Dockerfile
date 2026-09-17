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

#---

FROM $REGISTRY/yosys AS base
ARG REGISTRY

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/ghdl AS pkg-ghdl

FROM base AS plugin
ARG REGISTRY

COPY --from=pkg-ghdl /ghdl /

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build

#---

FROM $REGISTRY/pkg/ghdl AS pkg

COPY --from=plugin /usr/local/lib/ghdl_yosys.so /ghdl/usr/local/lib/ghdl_yosys.so

#---

FROM base

COPY --from=pkg /ghdl /

RUN yosys-config --exec mkdir -p --datdir/plugins \
 && yosys-config --exec ln -s /usr/local/lib/ghdl_yosys.so --datdir/plugins/ghdl.so
