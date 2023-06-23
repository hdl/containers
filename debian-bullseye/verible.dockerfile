# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
#   Patrick Richer St-Onge
#     <pars@kaloom.com>
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

FROM $REGISTRY/build/build AS build

RUN apt-get update -qq \
    && apt-get -y install --no-install-recommends gpg \
    && curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > /usr/share/keyrings/bazel-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list \
    && apt-get update -qq \
    && apt-get -y install --no-install-recommends bazel \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/chipsalliance/verible /tmp/verible \
    && cd /tmp/verible \
    && bazel run -c opt //:install -- /opt/verible/usr/local/bin

#---

FROM scratch AS pkg
COPY --from=build /opt/verible /verible

#---

FROM $REGISTRY/build/base
COPY --from=build /opt/verible /
