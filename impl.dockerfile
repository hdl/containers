# Authors:
#   Unai Martinez-Corral
#   Sebastian Birke      <git@se-bi.de>
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

FROM hdlc/ghdl:yosys AS base

COPY --from=hdlc/pkg:ghdl-yosys-plugin /ghdl /
COPY --from=hdlc/pkg:yosys /yosys /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libboost-all-dev \
    libomp5-7 \
    make \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#---

FROM base AS ecp5

COPY --from=hdlc/pkg:nextpnr-ecp5 /nextpnr-ecp5 /

#---

FROM base AS ice40

COPY --from=hdlc/pkg:nextpnr-ice40 /nextpnr-ice40 /

#---

FROM base AS generic

COPY --from=hdlc/pkg:nextpnr-generic /nextpnr-generic /

#---

FROM ice40 AS icestorm

COPY --from=hdlc/pkg:icestorm /icestorm /

#---

FROM ecp5 AS prjtrellis

COPY --from=hdlc/pkg:prjtrellis /prjtrellis /

#---

FROM base AS pnr

COPY --from=hdlc/pkg:nextpnr-ecp5 /nextpnr-ecp5 /
COPY --from=hdlc/pkg:nextpnr-ice40 /nextpnr-ice40 /
COPY --from=hdlc/pkg:nextpnr-generic /nextpnr-generic /

#---

FROM pnr AS latest

COPY --from=hdlc/pkg:icestorm /icestorm /
COPY --from=hdlc/pkg:prjtrellis /prjtrellis /
