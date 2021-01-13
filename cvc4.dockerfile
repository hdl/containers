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

FROM hdlc/build:build AS build

RUN mkdir /usr/share/man/man1 \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    cmake \
    openjdk-11-jre-headless \
    libgmp-dev \
    python3-toml \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/cvc4 && cd /tmp/cvc4 \
&& curl -fsSL https://codeload.github.com/CVC4/CVC4/tar.gz/master | tar xzf - --strip-components=1 \
&& ./contrib/get-antlr-3.4 \
&& ./contrib/get-cadical \
&& ./configure.sh --cadical \
&& cd build \
&& make -j$(nproc) \
&& make DESTDIR=/opt/cvc4 install

#---

FROM scratch
COPY --from=build /opt/cvc4 /cvc4
