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
from json import dumps as json_dumps
from subprocess import check_output

evname = environ["GITHUB_EVENT_NAME"]

match evname:
  case "push":
    tasks_trigger = environ["HDLC_PUSH_TRIGGER"]
  case "schedule":
    tasks_trigger = environ["HDLC_SCHEDULE_TRIGGER"]
  case "workflow_dispatch":
    tasks_trigger = environ["GH_INPUT_KEYS_TRIGGER"]
  case _:
    tasks_trigger = ""
    print(f"Empty dispatch key list for event name <{evname}>!")

skip_dispatch = evname == 'pull_request'

match evname:
  case "schedule":
    tasks_call = environ["HDLC_SCHEDULE_CALL"]
    skip_call = True
  case "workflow_dispatch":
    tasks_call = environ["GH_INPUT_KEYS_CALL"]
    skip_call = environ["GH_INPUT_SKIP-RELEASE"]
    skip_dispatch = skip_call
  case _:
    tasks_call = environ["HDLC_PUSH_CALL"]
    skip_call = skip_dispatch

tasks_trigger = tasks_trigger.split()
tasks_call = tasks_call.split()

if not (tasks_trigger or tasks_call):
  raise Exception(f"Both lists of keys empty <dispatch:{tasks_trigger}> <call:{tasks_call}>!")

if len(tasks_trigger)+len(tasks_call) != len(set([*tasks_trigger, *tasks_call])):
  raise Exception(f"Same key(s) requested for both dispatch and call <dispatch:{tasks_trigger}> <call:{tasks_call}>!")

for t, task in enumerate(tasks_call):
  if '>' in task:
    keys = task.split('>')
    tasks_call[t] = keys[0]
    tasks_trigger.append('>'.join([f"{keys[0]}=scheduler", *keys[1:]]))

with open(environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as gho:
  gho.write("cout=" + json_dumps({
    "matrix": [
      {'key': call.split(':')[0], 'skip-test': 'T' in call.split(':')[1]}
      if ':' in call else
      {'key': call, 'skip-test': False}
      for call in tasks_call
    ] if tasks_call else 'skip',
    "skip-release": skip_call
  }))

tasks_trigger = ['>'.join([
  (f'{key}R' if ':' in key else f'{key}:R')
  if skip_dispatch else key
  for key in seq.split('>')
]) for seq in tasks_trigger]

watchurl = check_output([
  "gh", "workflow", "run", ".watch.yml", "-r", environ['GITHUB_REF_NAME'],
  "-f", f"ids={' '.join(['scheduler='+environ['GITHUB_RUN_ID'], *tasks_trigger])}",
  "-f", f"rerun={environ['GH_INPUT_RERUN']}",
  "-f", f"message={environ['GITHUB_SHA'][0:8]} " + (
    evname if evname in ['schedule', 'workflow_dispatch']
    else environ['GH_MESSAGE'].split('\n')[0]
  )
], encoding="utf-8")

with open(environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as ghs:
  ghs.write('\n'.join([
    f"- Event: {evname}",
    f"- Watch: [{watchurl.split('/')[-1]}]({watchurl})",
    f"- Dispatch (skip-release: {skip_dispatch}):" + (" none" * (not bool(tasks_trigger))),
    *[f'  - {trigger}' for trigger in tasks_trigger],
    f"- Call (skip-release: {skip_call}):" + (" none" * (not bool(tasks_call))),
    *[f'  - {call}' for call in tasks_call],
    ""
  ]))
