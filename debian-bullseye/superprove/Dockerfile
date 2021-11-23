# Authors:
#   Unai Martinez-Corral
#   Torsten Meissner
#
# Copyright 2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    binutils \
    cmake \
    ninja-build \
    patch \
    python-setuptools \
    python-wheel-common \
    python-dev-is-python2 \
    zlib1g-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/* \
 && curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | python

COPY rm-system.patch /tmp/rm-system.patch

RUN mkdir /tmp/superprove && cd /tmp/superprove \
 && git clone --recursive https://github.com/sterin/super-prove-build . \
 && patch -p1 < /tmp/rm-system.patch \
 && mkdir build && cd build \
 && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local -G Ninja .. \
 && ninja \
 && ninja package \
 && mkdir -p /opt/superprove/usr/local \
 && tar -C /opt/superprove/usr/local -xzf super_prove*.tar.gz --strip 1

COPY suprove /opt/superprove/usr/local/bin/suprove

#---

FROM scratch
COPY --from=build /opt/superprove /superprove
