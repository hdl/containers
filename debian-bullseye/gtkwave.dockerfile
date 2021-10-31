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

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
 && apt-get -y install \
   build-essential \
   flex \
   gawk \
   gperf \
   libbz2-dev \
   libreadline-dev \
   libffi-dev \
   libgtk-3-dev \
   liblzma-dev \
   pkg-config \
   subversion \
   tcl-dev \
   tk-dev \
 && mkdir /tmp/gtkwave && cd /tmp/gtkwave \
 && svn checkout svn://svn.code.sf.net/p/gtkwave/code/gtkwave3-gtk3 ./ \
 && ./configure --with-tk=/usr/lib --enable-gtk3 \
 && make -j$(nproc) \
 && make DESTDIR=/opt/gtkwave check install

#---

FROM scratch AS pkg
COPY --from=build /opt/gtkwave /gtkwave

#---

FROM $REGISTRY/build/base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    graphviz \
    libgtk-3-bin \
    libtcl8.6 \
    libtk8.6 \
    xdot \
 && apt-get autoclean -y && apt-get clean -y && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/gtkwave /
CMD ["gtkwave"]
