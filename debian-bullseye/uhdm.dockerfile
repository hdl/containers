# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
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

FROM $REGISTRY/build/dev AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    pkg-config \
    python3 \
    python3-pip \
    python3-venv \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/alainmarcel/UHDM.git /tmp/UHDM \
 && cd /tmp/UHDM \
 && git submodule update --init --recursive \
 && pip3 install orderedmultidict \
 && make DESTDIR=/opt/uhdm install

#---

FROM scratch AS pkg

COPY --from=build /opt/uhdm /uhdm
