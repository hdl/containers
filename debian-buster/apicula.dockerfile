# syntax=docker/dockerfile:1.2

# Authors:
#   Unai Martinez-Corral
#   Lucas Teske
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
ARG IMAGE="build:base"

#---

FROM $REGISTRY/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python3-dev \
    python3-setuptools \
    python3-wheel

RUN mkdir /opt/apicula /tmp/apicula \
 && curl -fsSL https://files.pythonhosted.org/packages/1a/d6/b3162f87ff114d639095fe7c0655080ee16caff9037d6629f738d8b28d92/Apycula-0.0.1a6.tar.gz | tar -xvzf - --strip-components=1 -C /opt/apicula \
 && cd /opt/apicula \
 && python3 setup.py bdist_wheel \
 && mv dist/*.whl /tmp/apicula/

#---

FROM scratch AS pkg
COPY --from=build /tmp/apicula /apicula

#---

# WORKAROUND: this is required because '--mount=' does not support ARGs
FROM $REGISTRY/pkg:apicula AS pkg-apicula

FROM $REGISTRY/$IMAGE

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python3-pip \
    python3-setuptools \
    python3-wheel

RUN --mount=type=cache,from=pkg-apicula,src=/apicula,target=/tmp/apicula/ \
 pip3 install -U /tmp/apicula/*.whl --progress-bar off \
 && rm -rf ~/.cache
