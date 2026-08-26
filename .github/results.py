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
from tabulate import tabulate
from datetime import datetime as dt

results = [(lambda key, idx : {
  'workflow': key,
  'run_id': idx,
  'results': json_loads(check_output(['gh', 'run', 'view', idx, '--json', 'jobs', '-q', '.jobs | map( \
    pick(.name, .conclusion, .startedAt, .completedAt, .databaseId) | \
    select(.name | test("(dispatch|matrix|results)$") | not) )'
  ], encoding='utf-8'))
})(*(lambda l : l.split('='))(item)) for item in environ['GH_INPUT_IDS'].split(' ')]

sym = {
  'success': '✔️',
  'failure': '❌',
  'cancelled': '✖️',
  'skipped': '➖'
}

mdtables = []
for wflow in results:
  run_url = f"https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{wflow['run_id']}"
  mdtables.extend([
    ["", "", f"[{wflow['workflow']}]({run_url})", "", ""],
    *[[
      (lambda d: f"[{d}]({run_url}/job/{d})")(job['databaseId']),
      (lambda c: sym[c] if c in sym.keys() else '❔')(job['conclusion']),
      job['name'].replace('|','\\|'),
      job['startedAt'],
      dt.fromisoformat(job['completedAt']) - dt.fromisoformat(job['startedAt'])
    ] for job in wflow['results']],
  ])

with open(environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as ghs:
  ghs.write(tabulate(
    mdtables,
    headers=['']*5,
    tablefmt='github'
  ))
