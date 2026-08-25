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
from json import loads as json_loads

watch_bdid=check_output([
  'gh', 'run', 'view', environ['GITHUB_RUN_ID'],
  '--json', 'jobs', '--jq', '.jobs[] | select(.name=="watch") | .databaseId'
], encoding='utf-8').strip()

for note in json_loads(check_output(
  ['gh', 'api', 'repos/{owner}/{repo}/check-runs/'f"{watch_bdid}/annotations"], encoding="utf-8"
)):
  if (
    note['annotation_level'] == 'failure' and
    note['message'].startswith('The job has exceeded the maximum execution time of')
  ):
    run = check_output([
      'gh', 'workflow', 'run', '.watch.yml',
      '-r', environ['GITHUB_REF_NAME'],
      '-f', f"ids={environ['GH_INPUT_IDS']}",
      '-f', f"rerun={environ['GH_INPUT_RERUN']}",
      '-f', f"message={environ['GH_INPUT_MESSAGE']}",
    ], encoding='utf-8')
    run_id = run.split('/')[-1]
    with open(environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as ghs:
      ghs.write(f'Timeout! New watch dispatched: [{run_id}]({run})')
    break
