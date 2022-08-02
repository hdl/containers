#!/usr/bin/env -S bash -l

# Copyright 2020-2022 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

set -e

cd $(dirname "$0")

./_env.sh

which ql_symbiflow
which symbiflow_analysis
which symbiflow_fasm2bels
which symbiflow_generate_constraints
which symbiflow_generate_bitstream
which symbiflow_pack
which symbiflow_place
which symbiflow_repack
which symbiflow_route
which symbiflow_synth
which symbiflow_write_bitheader
which symbiflow_write_binary
which symbiflow_write_fasm
which symbiflow_write_jlink
which symbiflow_write_openocd
which vpr_common

./_todo.sh
