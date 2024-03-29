# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
#     <unai.martinezcorral@ehu.eus>
#   Carlos Eduardo de Paula
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

ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

#---

FROM $REGISTRY/conda AS xc7-toolchain
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && env-and-toolchain xc7

#---

FROM $REGISTRY/conda/f4pga/xc7/toolchain AS a50t
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && get-arch-defs-package xc7a50t_test

#---

FROM $REGISTRY/conda/f4pga/xc7/toolchain AS a100t
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && get-arch-defs-package xc7a100t_test

#---

FROM $REGISTRY/conda/f4pga/xc7/toolchain AS a200t
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && get-arch-defs-package xc7a200t_test

#---

FROM $REGISTRY/conda/f4pga/xc7/toolchain AS z010
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && get-arch-defs-package xc7z010_test

#---

FROM $REGISTRY/conda/f4pga/xc7/toolchain AS z020
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && get-arch-defs-package xc7z020_test

#---

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/conda/f4pga/xc7/a50t AS xc7-a50t
FROM $REGISTRY/conda/f4pga/xc7/a100t AS xc7-a100t
# TODO: This is temporarily disabled because of space limits on GitHub Actions default runners
#FROM $REGISTRY/conda/f4pga/xc7/a200t AS xc7-a200t
FROM $REGISTRY/conda/f4pga/xc7/z010 AS xc7-z010
FROM $REGISTRY/conda/f4pga/xc7/z020 AS xc7-z020

FROM $REGISTRY/conda/f4pga/xc7/toolchain AS xc7

COPY --from=xc7-a50t /usr/local/share/f4pga/arch/xc7a50t_test /usr/local/share/f4pga/arch/xc7a50t_test
COPY --from=xc7-a100t /usr/local/share/f4pga/arch/xc7a100t_test /usr/local/share/f4pga/arch/xc7a100t_test
# TODO: This is temporarily disabled because of space limits on GitHub Actions default runners
#COPY --from=xc7-a200t /usr/local/share/f4pga/arch/xc7a200t_test /usr/local/share/f4pga/arch/xc7a200t_test
COPY --from=xc7-z010 /usr/local/share/f4pga/arch/xc7z010_test /usr/local/share/f4pga/arch/xc7z010_test
COPY --from=xc7-z020 /usr/local/share/f4pga/arch/xc7z020_test /usr/local/share/f4pga/arch/xc7z020_test

#---

FROM $REGISTRY/conda AS eos-s3
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && env-and-toolchain eos-s3
