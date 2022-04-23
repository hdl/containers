# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021-2022 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/icestorm AS pkg-icestorm

FROM $REGISTRY/build/build AS build

COPY --from=pkg-icestorm /icestorm/usr/local/share/icebox /usr/local/share/icebox

RUN git clone https://github.com/YosysHQ/arachne-pnr.git /tmp/arachne-pnr \
 && cd /tmp/arachne-pnr \
 && make -j $(nproc) \
 && make DESTDIR=/opt/arachne-pnr install

#---

FROM scratch AS pkg
COPY --from=build /opt/arachne-pnr /arachne-pnr

#---

FROM $REGISTRY/build/base
COPY --from=build /opt/arachne-pnr /
