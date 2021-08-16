# Authors:
#   Unai Martinez-Corral
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

ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

#--

FROM $REGISTRY/build/dev AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    cmake \
    libftdi1-2 \
    libftdi1-dev \
    libhidapi-libusb0 \
    libhidapi-dev \
    libudev-dev \
    pkg-config \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --recurse-submodules https://github.com/trabucayre/openFPGALoader /tmp/openFPGALoader \
 && cd /tmp/openFPGALoader \
 && mkdir build \
 && cd build \
 && cmake ../ \
 && cmake --build . \
 && make DESTDIR=/opt/openFPGALoader install \
 && mkdir -p /opt/openFPGALoader/etc/udev/rules.d \
 && cp ../99-openfpgaloader.rules /opt/openFPGALoader/etc/udev/rules.d/

#---

FROM scratch AS pkg
COPY --from=build /opt/openFPGALoader /openfpgaloader

#---

FROM $REGISTRY/build/base
COPY --from=build /opt/openFPGALoader /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libftdi1-2 \
    libhidapi-libusb0 \
    udev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

# NOTE:
# The following commands should be executed when the container is used.
# See https://github.com/trabucayre/openFPGALoader#access-right
# $ udevadm control --reload-rules
# $ udevadm trigger
# $ usermod -a YourUserName -G plugdev
