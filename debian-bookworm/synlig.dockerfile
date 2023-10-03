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

ARG REGISTRY='gcr.io/hdl-containers/debian/bookworm'

#---

FROM $REGISTRY/yosys AS base


FROM base as build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    make \
    pkg-config \
    cmake \
    python3 \
    python3-pip \
    python3-venv \
    openjdk-17-jre-headless \
    tree \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3 install orderedmultidict

RUN git clone https://github.com/alainmarcel/Surelog.git /tmp/Surelog \
 && cd /tmp/Surelog \
 && git submodule update --init --recursive \
 && make install

#RUN git clone https://github.com/alainmarcel/UHDM.git /tmp/UHDM \
# && cd /tmp/UHDM \
# && git submodule update --init --recursive \
# && make install

RUN mkdir /tmp/synlig && cd /tmp/synlig \
 && curl -fsSL https://codeload.github.com/chipsalliance/synlig/tar.gz/main | tar xzf - --strip-components=1 \
 && make install \
 && tree out \
 && mkdir -p /opt/synlig/ \
 && cp build/systemverilog-plugin/systemverilog.so /opt/synlig/

#---

FROM scratch AS pkg
COPY --from=build /tmp/synlig/build/systemverilog-plugin/systemverilog.so /synlig/systemverilog.so

##---
#
#FROM $REGISTRY/pkg/ghdl AS pkg
#
#COPY --from=plugin /opt/ghdl/usr/local/lib/ghdl_yosys.so /ghdl/usr/local/lib/ghdl_yosys.so

#---

FROM base

COPY --from=pkg /synlig/systemverilog.so /tmp/synlig/systemverilog.so

RUN yosys-config --exec mkdir -p --datdir/plugins \
 && yosys-config --exec mv /tmp/synlig/systemverilog.so --datdir/plugins/systemverilog.so
