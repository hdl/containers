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

ARG REGISTRY='ghcr.io/hdl/debian/bullseye'
ARG IMAGE="sim"

#---

FROM $REGISTRY/$IMAGE AS build
ARG REGISTRY

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${makedepends[@]} \
 && pip3 install -U setuptools wheel \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/* \
 && build

#---

FROM scratch AS pkg
COPY --from=build /tmp/osvb/ /osvb/

#---

# WORKAROUND: '--mount=' does not support ARGs
FROM $REGISTRY/pkg/osvb AS pkg-osvb

FROM $REGISTRY/$IMAGE
ARG REGISTRY

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,from=pkg-osvb,src=/osvb/,target=/tmp/osvb/ \
  pip3 install -U /tmp/osvb/*.whl pytest --progress-bar off \
  && rm -rf ~/.cache \
  && mkdir /opt/osvb \
  && cp -vr /tmp/osvb/osvvmlibs/ /opt/osvb/osvvmlibs/
