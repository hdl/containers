# Authors:
#   Unai Martinez-Corral
#   Carlos Eduardo de Paula
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

ARG REGISTRY='ghcr.io/hdl/debian-buster'

#---

FROM $REGISTRY/miniconda3

ENV INSTALL_DIR="/opt/symbiflow"
ENV FPGA_FAM="eos-s3"

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    build-essential \
    cmake \
    xz-utils \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /

RUN git clone https://github.com/SymbiFlow/symbiflow-examples

RUN cd symbiflow-examples \
 && conda env create -f ./${FPGA_FAM}/environment.yml

RUN mkdir -p ${INSTALL_DIR}/${FPGA_FAM}/install \
 && wget -qO- https://quicklogic-my.sharepoint.com/:u:/p/kkumar/EWuqtXJmalROpI2L5XeewMIBRYVCY8H4yc10nlli-Xq79g?download=1 | tar -xJ -C ${INSTALL_DIR}/${FPGA_FAM}/

ENV PATH="$INSTALL_DIR/$FPGA_FAM/install/bin:/opt/conda/envs/${FPGA_FAM}/bin/:${PATH}"

COPY ./docker-entrypoint.sh-symbiflow /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["bash"]
