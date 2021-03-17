# Authors:
#   Unai Martinez-Corral
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

FROM centos:7 AS base

RUN yum install -y https://repo.ius.io/ius-release-el$(rpm -E '%{rhel}').rpm && yum install -y \
    curl \
    python36u \
    python36u-pip \
 && alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 60

#---

FROM base AS build

RUN yum install -y \
    clang \
    git \
    make

ENV CC clang
ENV CXX clang++

#---

FROM build

RUN yum install -y \
    cmake \
    libboost-all-dev \
    python3-dev
