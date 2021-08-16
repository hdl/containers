# Authors:
#   Unai Martinez-Corral
#
# Copyright 2018-2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

FROM ghdl/pkg:bullseye-mcode AS build-mcode

# TODO Build GHDL on $REGISTRY/build/build instead of picking ghdl/pkg:bullseye-mcode

#---

FROM scratch AS pkg-mcode

COPY --from=build-mcode / /ghdl/usr/local/

#---

FROM ghdl/pkg:bullseye-llvm-9 AS build-llvm

# TODO Build GHDL on $REGISTRY/build/build instead of picking ghdl/pkg:bullseye-mcode

#---

FROM scratch AS pkg-llvm

COPY --from=build-llvm / /ghdl/usr/local/

#--

FROM $REGISTRY/build/base AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-9 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#--

FROM base AS mcode

COPY --from=build-mcode / /usr/local/

#--

FROM base AS llvm

COPY --from=build-llvm / /usr/local/

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    gcc \
    libgnat-9 \
    libllvm9 \
    zlib1g-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists
