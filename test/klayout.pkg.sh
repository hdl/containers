#!/bin/sh
# SPDX-License-Identifier: Apache-2.0

set -e

cd $(dirname "$0")

./_tree.sh

./_todo.sh
