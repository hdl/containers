#!/usr/bin/env sh

# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

pip3 install -r pyHDLC/requirements.txt

HDL_ARCH="${HDL_ARCH:-$1}"

if [ -n "$CI" ]; then
  echo "$(pwd)/bin" >> $GITHUB_PATH
  echo "PYTHONPATH=$(pwd)" >> $GITHUB_ENV

  if [ -n "$HDL_ARCH" ]; then
    unset _arch
    case $HDL_ARCH in
      arm32v7) _arch="arm";;
      arm64v8) _arch="aarch64";;
      ppc64le|s390x|riscv64) _arch="$HDL_ARCH";;
    esac
    if [ -n "$_arch" ]; then
      docker run --rm --privileged aptman/qus -s -- -p $_arch
    fi
  fi

else

  export PATH="$PATH:$(pwd)/bin"
  export PYTHONPATH="$(pwd)"

fi
