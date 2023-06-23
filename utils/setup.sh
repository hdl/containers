#!/usr/bin/env sh

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

set -e

cd $(dirname "$0")

[ -z "$MSYSTEM" ] && pip3 install -e . || export PYTHONPATH="$(pwd)"

if [ -z "$CI" ]; then
  export PATH="$PATH:$(pwd)/bin"
  exit 0
fi

echo "$(pwd)/bin" >> $GITHUB_PATH

unset _arch
case $1 in
  arm32v7) _arch="arm";;
  arm64v8) _arch="aarch64";;
  ppc64le|s390x|riscv64) _arch="$1";;
esac
if [ -n "$_arch" ]; then
  docker run --rm --privileged aptman/qus -s -- -p $_arch
fi
