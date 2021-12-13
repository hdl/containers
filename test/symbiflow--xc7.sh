#!/usr/bin/env sh

# Copyright 2020-2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

./symbiflow--xc7--toolchain.sh
./symbiflow--xc7--a50t.sh
./symbiflow--xc7--a100t.sh
# TODO: This is temporarily disabled because of space limits on GitHub Actions default runners
#./symbiflow--xc7--a200t.sh
./symbiflow--xc7--z010.sh

./_todo.sh
