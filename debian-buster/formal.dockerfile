# Authors:
#   Unai Martinez-Corral
#   Torsten Meissner
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

ARG REGISTRY='ghcr.io/hdl/debian-buster'

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg:z3 AS pkg-z3
FROM $REGISTRY/pkg:symbiyosys AS pkg-symbiyosys

FROM $REGISTRY/ghdl:yosys AS min

COPY --from=pkg-z3 /z3 /
COPY --from=pkg-symbiyosys /symbiyosys /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python3 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg:yices2 AS pkg-yices2
FROM $REGISTRY/pkg:boolector AS pkg-boolector
FROM $REGISTRY/pkg:cvc4 AS pkg-cvc4
FROM $REGISTRY/pkg:pono AS pkg-pono

FROM min AS latest

COPY --from=pkg-yices2 /yices2 /
COPY --from=pkg-boolector /boolector /
COPY --from=pkg-cvc4 /cvc4 /
COPY --from=pkg-pono /pono /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgmpxx4ldbl \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg:superprove AS pkg-superprove

FROM latest

COPY --from=pkg-superprove /superprove /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python \
    libpython2.7 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
