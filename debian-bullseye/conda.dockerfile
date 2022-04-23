# Authors:
#   Unai Martinez-Corral
#   Carlos Eduardo de Paula
#
# Copyright 2019-2022 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

FROM $REGISTRY/build/base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    xz-utils \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

ENV PREFIX=/usr/local

RUN curl -fsSL "https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-$(arch | sed s/arm64/aarch64/ | sed s/amd64/x86_64/).sh" > conda_installer.sh \
 && chmod +x conda_installer.sh \
 && ./conda_installer.sh -u -b -p "$PREFIX" \
 && rm conda_installer.sh \
 && find "$PREFIX" -follow -type f -name '*.a' -delete \
 && find "$PREFIX" -follow -type f -name '*.js.map' -delete \
 && conda clean -afy \
 && echo 'source /usr/local/etc/profile.d/conda.sh' >> ~/.bashrc
