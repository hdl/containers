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

#---

FROM $REGISTRY/iverilog AS build

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} ${makedepends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} ${testdepends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && runtests

#---

FROM scratch AS pkg
COPY --from=build /opt/yosys /yosys

#---

FROM $REGISTRY/build/build

COPY --from=build /opt/yosys /

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

CMD ["yosys"]
