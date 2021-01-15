# syntax=docker/dockerfile:experimental
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

FROM hdlc/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends wget

RUN mkdir /opt/apicula \
 && wget https://files.pythonhosted.org/packages/1a/d6/b3162f87ff114d639095fe7c0655080ee16caff9037d6629f738d8b28d92/Apycula-0.0.1a6.tar.gz \
 && tar -xvf Apycula-0.0.1a6.tar.gz --strip-components=1 -C /opt/apicula \
 && ls -lah /opt/apicula

#---

FROM scratch AS pkg
COPY --from=build /opt/apicula /apicula

#---

FROM hdlc/build:base

RUN --mount=type=cache,from=build,src=/opt/apicula,target=/opt/apicula cd /opt/apicula \
 && python3 setup.py install \
 && rm -rf ~/.cache

