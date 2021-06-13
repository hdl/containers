# Authors:
#   Unai Martinez-Corral
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

ARG REGISTRY='gcr.io/hdl-containers/debian/buster'

#---

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    pkg-config

RUN mkdir /tmp/icestorm \
 && cd /tmp/icestorm \
 && curl -fsSL https://codeload.github.com/YosysHQ/icestorm/tar.gz/master | tar xzf - --strip-components=1 \
 && ICEPROG=0 make -j $(nproc) \
 && ICEPROG=0 make DESTDIR=/opt/icestorm install

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libftdi1-dev

RUN cd /tmp/icestorm/iceprog \
 && make -j $(nproc) \
 && make DESTDIR=/opt/iceprog install

#---

FROM scratch AS pkg
COPY --from=build /opt/iceprog /iceprog
COPY --from=build /opt/icestorm /icestorm

#---

FROM $REGISTRY/build/base
COPY --from=build /opt/icestorm /
