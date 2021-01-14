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
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends python3-setuptools python3-pip

RUN mkdir /tmp/apicula \
 && cd /tmp/apicula \
 && pip3 install apycula --target /tmp/apicula

#---

FROM scratch AS pkg
COPY --from=build /tmp/apicula /apicula

#---

FROM hdlc/build:base
RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends python3-setuptools python3-pip \
 && pip3 install apycula
