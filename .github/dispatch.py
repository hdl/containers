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

evname = environ["GITHUB_EVENT_NAME"]

match evname:
  case "push":
    keys_trigger = environ["HDLC_PUSH_TRIGGER"].split(' ')
  case "schedule":
    keys_trigger = environ["HDLC_SCHEDULE_TRIGGER"].split(' ')
  case "workflow_dispatch":
    keys_trigger = environ["GH_INPUT_KEYS_TRIGGER"].split(' ')
  case _:
    keys_trigger = []
    print(f"Empty dispatch key list for event name <{evname}>!")

skip_dispatch = evname == 'pull_request'

match evname:
  case "schedule":
    keys_call = environ["HDLC_SCHEDULE_CALL"].split(' ')
    skip_call = True
  case "workflow_dispatch":
    keys_call = environ["GH_INPUT_KEYS_CALL"].split(' ')
    skip_call = environ["GH_INPUT_SKIP-RELEASE"]
    skip_dispatch = skip_call
  case _:
    keys_call = environ["HDLC_PUSH_CALL"].split(' ')
    skip_call = skip_dispatch

if not (keys_trigger or keys_call):
  raise Exception(f"Both lists of keys empty <dispatch:{keys_trigger}> <call:{keys_call}>!")

if len(keys_trigger)+len(keys_call) != len(set([*keys_trigger, *keys_call])):
  raise Exception(f"Key(s) requested for both dispatch and call <dispatch:{keys_trigger}> <call:{keys_call}>!")

with open(environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as gho:
  gho.write(
    f"matrix={[{'key': call} for call in keys_call]!s}\n"
    f"skip-release={skip_call}\n"
  )

dispatch = []
if keys_trigger:
  message = f"message={environ['GITHUB_SHA'][0:8]} " + (
    evname if evname in ['schedule', 'workflow_dispatch']
    else environ['GH_MESSAGE'].split('\n')[0]
  )
  dispatch = [f'{key}=' + check_output([
    "gh", "workflow", "run", ".build-test-release.yml", "-r", environ["GITHUB_REF_NAME"],
    "-f", f"key={key}",
    "-f", f"skip-release={str(skip_dispatch)}",
    "-f", message
  ], encoding="utf-8").split('/')[-1].strip() for key in keys_trigger]

watchurl = check_output([
  "gh", "workflow", "run", ".watch.yml", "-r", environ['GITHUB_REF_NAME'],
  "-f", f"ids={' '.join(['scheduler='+environ['GITHUB_RUN_ID'], *dispatch])}",
  "-f", message
], encoding="utf-8")

with open(environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as ghs:
  ghs.write('\n'.join([
    f"- Event: {evname}",
    f"- Watch: [{watchurl.split('/')[-1]}]({watchurl})",
    f"- Dispatch (skip-release: {skip_dispatch}):",
    *[
      (lambda key, idx : f"  - {key}: [{idx}](https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{idx})")
      (*(lambda l : l.split('='))(item))
      for item in dispatch
    ],
    f"- Call (skip-release: {skip_call}):",
    *[f'  - {call}' for call in keys_call],
    ""
  ]))
