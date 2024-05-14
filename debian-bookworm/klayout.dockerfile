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

ARG REGISTRY='gcr.io/hdl-containers/debian/bookworm'

#--

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgit2-dev \
    libqt5svg5-dev \
    libqt5xmlpatterns5-dev \
    python3-dev \
    qt5-qmake \
    qtmultimedia5-dev \
    qttools5-dev \
    ruby-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/KLayout/klayout.git /tmp/klayout \
 && mkdir -p /opt/klayout/usr/local/bin \
 && cd /tmp/klayout \
 && ./build.sh \
   -qmake 'qmake -spec linux-clang' \
   -bin /opt/klayout/usr/local/bin \
   -rpath /usr/local/lib \
   -ruby /usr/bin/ruby \
   -python /usr/bin/python3 \
   -option -j$(nproc) \
 && mkdir -p /opt/klayout/usr/local/lib \
 && cd /opt/klayout/usr/local/bin \
 && mv libklayout* db_plugins lay_plugins ../lib/

#---

FROM scratch AS pkg
COPY --from=build /opt/klayout /klayout

#---

FROM $REGISTRY/build/base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgit2-1.5 \
    libpulse-mainloop-glib0 \
    libpython3.11 \
    libqt5core5a \
    libqt5designer5 \
    libqt5gui5 \
    libqt5multimedia5 \
    libqt5multimediawidgets5 \
    libqt5printsupport5 \
    libqt5sql5 \
    libqt5svg5 \
    libqt5widgets5 \
    libqt5xml5 \
    libqt5xmlpatterns5 \
    libruby \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/klayout /
CMD ["klayout"]
