#!/usr/bin/env python3

# Authors:
#   Unai Martinez-Corral
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

from os import environ
from subprocess import check_output
from pathlib import Path
from json import loads as json_loads

event_name = environ["GITHUB_EVENT_NAME"]
message = event_name
match event_name:
  case "push":
    keys = [
      "nvc"
    ]
    message = environ["GH_MESSAGE"]
  case "schedule":
    keys = [
      "boolector",
      "netgen",
      "nvc"
    ]
  case "workflow_dispatch":
    keys = environ["GH_INPUT_KEYS"].split(' ')
  case _:
    raise Exception(f"Unhandled event_name <{event_name}>!")

if not keys:
  raise Exception(f"Empty list of keys <{keys}>!")

summary = [f"{event_name}"]

for key in keys:
  run = json_loads(check_output([
    "./.github/trigger.sh",
    environ["GITHUB_REF_NAME"],
    key,
    environ["GH_INPUT_SKIP-RELEASE"] if event_name == "workflow_dispatch" else "false",
    f"{environ['GITHUB_SHA'][0:8]} {message.split('\n')[0]}"
  ]))
  summary.append(f"  - {key}: [{run['workflow_run_id']}]({run['html_url']})")

with Path(environ["GITHUB_STEP_SUMMARY"]).open("a") as ghs:
  for line in summary:
    ghs.write(f"{line}\n")
