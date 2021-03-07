#!/usr/bin/env sh
# SPDX-License-Identifier: Apache-2.0

set -e

cd $(dirname "$0")

./_env.sh

./smoke-tests/klayout.sh

./_todo.sh
