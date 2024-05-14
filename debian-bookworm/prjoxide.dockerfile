# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
#     <unai.martinezcorral@ehu.eus>
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

ARG REGISTRY='gcr.io/hdl-containers/debian/bookworm'

#--

FROM $REGISTRY/build/build AS build

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

RUN source "$HOME/.cargo/env" \
 && git clone --recurse-submodules https://github.com/gatecat/prjoxide /tmp/prjoxide \
 && cd /tmp/prjoxide/libprjoxide \
 && cargo install --path prjoxide --root /opt/prjoxide/usr/local

#---

FROM scratch AS pkg
COPY --from=build /opt/prjoxide /prjoxide

#---

FROM $REGISTRY/build/base
COPY --from=build /opt/prjoxide /
