# Authors:
#   Sebastian Birke <git@se-bi.de>
#   Unai Martinez-Corral
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

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/ghdl-yosys-plugin AS pkg-ghdl-yosys-plugin
FROM $REGISTRY/pkg/yosys AS pkg-yosys

FROM $REGISTRY/ghdl/yosys AS base

COPY --from=pkg-ghdl-yosys-plugin /ghdl /
COPY --from=pkg-yosys /yosys /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libboost-all-dev \
    libomp5-11 \
    make \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/nextpnr/ice40 AS pkg-nextpnr-ice40

FROM $REGISTRY/build/impl AS ice40
COPY --from=pkg-nextpnr-ice40 /nextpnr-ice40 /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/icestorm AS pkg-icestorm

FROM ice40 AS icestorm
COPY --from=pkg-icestorm /icestorm /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/nextpnr/ecp5 AS pkg-nextpnr-ecp5

FROM $REGISTRY/build/impl AS ecp5
COPY --from=pkg-nextpnr-ecp5 /nextpnr-ecp5 /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/prjtrellis AS pkg-prjtrellis

FROM ecp5 AS prjtrellis
COPY --from=pkg-prjtrellis /prjtrellis /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/nextpnr/nexus AS pkg-nextpnr-nexus

FROM $REGISTRY/build/impl AS nexus
COPY --from=pkg-nextpnr-nexus /nextpnr-nexus /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/prjoxide AS pkg-prjoxide

FROM nexus AS prjoxide
COPY --from=pkg-prjoxide /prjoxide /

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/nextpnr/generic AS pkg-nextpnr-generic

FROM $REGISTRY/build/impl AS generic
COPY --from=pkg-nextpnr-generic /nextpnr-generic /

#---

FROM $REGISTRY/build/impl AS pnr
COPY --from=pkg-nextpnr-nexus /nextpnr-nexus /
COPY --from=pkg-nextpnr-ecp5 /nextpnr-ecp5 /
COPY --from=pkg-nextpnr-ice40 /nextpnr-ice40 /
COPY --from=pkg-nextpnr-generic /nextpnr-generic /

#---

FROM pnr
COPY --from=pkg-icestorm /icestorm /
COPY --from=pkg-prjtrellis /prjtrellis /
COPY --from=pkg-prjoxide /prjoxide /
