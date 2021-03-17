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

FROM hdlc/yosys AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-8 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#---

FROM base AS plugin

COPY --from=hdlc/pkg:ghdl /ghdl /opt/ghdl

RUN mkdir /tmp/ghdl-yosys-plugin && cd /tmp/ghdl-yosys-plugin \
 && curl -fsSL https://codeload.github.com/ghdl/ghdl-yosys-plugin/tar.gz/master | tar xzf - --strip-components=1

RUN cp -vr /opt/ghdl/* / \
 && cd /tmp/ghdl-yosys-plugin \
 && make \
 && cp ghdl.so /opt/ghdl/usr/local/lib/ghdl_yosys.so

#---

FROM hdlc/pkg:ghdl AS pkg

COPY --from=plugin /opt/ghdl/usr/local/lib/ghdl_yosys.so /ghdl/usr/local/lib/ghdl_yosys.so

#---

FROM base

COPY --from=pkg /ghdl /

RUN yosys-config --exec mkdir -p --datdir/plugins \
 && yosys-config --exec ln -s /usr/local/lib/ghdl_yosys.so --datdir/plugins/ghdl.so
