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

cd "$(dirname "$0")"

if [ -n "${MSYSTEM:-}" ]; then
  export PYTHONPATH="$(pwd)"
  export PATH="$PATH:$(pwd)/bin"
  exit 0
fi

PYTHON="${PYTHON:-python3}"

[ -n "${VIRTUAL_ENV:-}" ] || echo "WARNING: no active virtualenv; see doc/dev/Utils.rst" >&2

"$PYTHON" -m pip install -e .

"$PYTHON" -c 'import pyHDLC' || { echo "ERROR: pyHDLC installation failed" >&2; exit 1; }

if [ -n "${GITHUB_PATH:-}" ]; then
  echo "$(pwd)/bin" >> "$GITHUB_PATH"
fi

_arch=""
case "${1:-}" in
  arm32v7) _arch="arm";;
  arm64v8) _arch="aarch64";;
  ppc64le|s390x|riscv64) _arch="$1";;
esac
if [ -n "$_arch" ]; then
  command -v docker >/dev/null 2>&1 || { echo "ERROR: docker required for cross-arch setup" >&2; exit 1; }
  docker run --rm --privileged aptman/qus -s -- -p "$_arch"
fi
