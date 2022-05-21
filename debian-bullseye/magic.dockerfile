# Copyright 2021-2022 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

#--

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    csh \
    libcairo2-dev \
    libglu1-mesa-dev \
    libncurses-dev \
    libx11-dev \
    m4 \
    python3-dev \
    tcl \
    tcl-dev \
    tcl-expect \
    tcsh \
    tk-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/RTimothyEdwards/magic /tmp/magic \
 && mkdir -p /opt/magic/ \
 && cd /tmp/magic \
 && ./configure \
 && make -j$(nproc) \
 && make install \
 && make DESTDIR=/opt/magic install

#---

FROM scratch AS pkg
COPY --from=build /opt/magic /magic

#---

FROM $REGISTRY/build/base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libcairo2 \
    libglu1-mesa \
    libncurses6 \
    libx11-6 \
    tcl \
    tk \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/magic /
CMD ["magic"]
