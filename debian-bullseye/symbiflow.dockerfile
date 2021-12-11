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

ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

#---

FROM $REGISTRY/conda AS xc7-base

RUN mkdir symbiflow-examples \
 && curl -fsSL https://codeload.github.com/SymbiFlow/symbiflow-examples/tar.gz/master | tar xzf - -C symbiflow-examples --strip-components=1 \
 && conda env create -f ./symbiflow-examples/xc7/environment.yml \
 && rm -rf symbiflow-examples

RUN curl -fsSL https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/459/20211116-000105/symbiflow-arch-defs-install-ef6fff3c.tar.xz | tar -xJC /usr/local

#---

FROM $REGISTRY/symbiflow/xc7/base AS xc7

RUN for PKG in xc7a50t_test xc7a100t_test xc7a200t_test xc7z010_test; do curl -fsSL https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/459/20211116-000105/symbiflow-arch-defs-${PKG}-ef6fff3c.tar.xz | tar -xJC /usr/local; done

#---

FROM $REGISTRY/symbiflow/xc7/base AS a50t

RUN curl -fsSL https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/459/20211116-000105/symbiflow-arch-defs-xc7a50t_test-ef6fff3c.tar.xz | tar -xJC /usr/local

#---

FROM $REGISTRY/symbiflow/xc7/base AS a100t

RUN curl -fsSL https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/459/20211116-000105/symbiflow-arch-defs-xc7a100t_test-ef6fff3c.tar.xz | tar -xJC /usr/local

#---

FROM $REGISTRY/symbiflow/xc7/base AS a200t

RUN curl -fsSL https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/459/20211116-000105/symbiflow-arch-defs-xc7a200t_test-ef6fff3c.tar.xz | tar -xJC /usr/local

#---

FROM $REGISTRY/symbiflow/xc7/base AS z010

RUN curl -fsSL https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/459/20211116-000105/symbiflow-arch-defs-xc7z010_test-ef6fff3c.tar.xz | tar -xJC /usr/local

#---

FROM $REGISTRY/conda AS eos-s3

RUN mkdir symbiflow-examples \
 && curl -fsSL https://codeload.github.com/SymbiFlow/symbiflow-examples/tar.gz/master | tar xzf - -C symbiflow-examples --strip-components=1 \
 && conda env create -f ./symbiflow-examples/eos-s3/environment.yml \
 && rm -rf symbiflow-examples

RUN curl -fsSL https://storage.googleapis.com/symbiflow-arch-defs-install/quicklogic-arch-defs-63c3d8f9.tar.gz | tar -xzC /usr/local --strip-components=1
