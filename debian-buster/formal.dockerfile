# Authors:
#   Unai Martinez-Corral
#   Torsten Meissner
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

FROM hdlc/ghdl:yosys AS min

COPY --from=hdlc/pkg:z3 /z3 /
COPY --from=hdlc/pkg:symbiyosys /symbiyosys /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python3 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#---

FROM min AS latest

COPY --from=hdlc/pkg:yices2 /yices2 /
COPY --from=hdlc/pkg:boolector /boolector /
COPY --from=hdlc/pkg:cvc4 /cvc4 /

#---

FROM latest

COPY --from=hdlc/pkg:superprove /superprove /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python \
    libpython2.7 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
