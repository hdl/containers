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
from subprocess import DEVNULL, check_call, check_output, run
from json import loads as json_loads
from tabulate import tabulate
from datetime import datetime as dt

schedule = json_loads(environ['GH_INPUT_SCHEDULE'])
pending, inprogress = (schedule[k] for k in ('pending', 'inprogress'))
done = schedule.get('done', {})

if environ['GH_WATCH_RESULT'] == 'cancelled':

  print("::group::⏰ Check annotations and redispatch or cancel")

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
      run_url = check_output([
        'gh', 'workflow', 'run', '.watch.yml',
        '-r', environ['GITHUB_REF_NAME'],
        '-f', f"schedule={environ['GH_INPUT_SCHEDULE']}",
        '-f', f"rerun={environ['GH_INPUT_RERUN']}",
        '-f', f"message={environ['GH_INPUT_MESSAGE']}",
      ], encoding='utf-8')
      run_id = run_url.split('/')[-1]
      with open(environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as ghs:
        ghs.write(f'Timeout! New watch dispatched: [{run_id}]({run_url})\n')
      break
  else:
    for wflow in inprogress:
      if wflow['idx'].split('!')[0] != 'scheduler':
        print(f"Cancel {wflow['key']}")
        run(["gh", "run", "cancel", wflow['idx'], "--force"], check=False)
    for wflow in inprogress:
      print(f"Watching {wflow['key']}...")
      if wflow['idx'].split('!')[0] != 'scheduler':
        check_call(["gh", "run", "watch", wflow['idx'], "-i", str(30)], stdout=DEVNULL)
      done[wflow['key']] = f"{wflow['idx']}!"
    inprogress = []

  print("::endgroup::")

results = []
for wflow in [
  *[(wflow, idx) for wflow, idx in done.items()],
  *[(wflow['key'], wflow['idx']) for wflow in inprogress],
  *[(wflow, '') for wflow in pending],
]:
  idx = wflow[1].split('!')[0]
  results.append({**({} if idx == 'scheduler' or not idx else
    json_loads(check_output(['gh', 'run', 'view', idx, '--json', 'attempt,conclusion,jobs', '-q', '''
.jobs |= map(
  pick(.name, .conclusion, .startedAt, .completedAt, .databaseId) |
  select(.name | test("(dispatch|matrix|results|matrix\\\\.key)$") | not) )
'''
    ], encoding='utf-8'))),
    'workflow': wflow[0],
    'run_id': wflow[1],
  })

sym = {
  'success': '✔️',
  'failure': '❌',
  'cancelled': '✖️',
  'skipped': '➖',
  '' : '🎬',
  'queued': '⌚',
  'scheduler': '🧱'
}

def _conclusion(conclusion):
  return sym.get(conclusion, '❔')

mdtables = []
for wflow in results:
  idx = wflow['run_id'].split('!')[0]
  if idx == 'scheduler' or not idx:
    mdtables.append([
      "",
      sym[
        'cancelled' if '!' in wflow['run_id'] else
        'queued' if not idx else
        'scheduler'
      ],
      wflow['workflow'],
      "",
      ""
    ])
    continue
  run_url = f"https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{idx}"
  mdtables.extend([
    [
      f"[{wflow['run_id']}]({run_url})",
      _conclusion(wflow['conclusion']),
      f"{wflow['workflow']}: {len(wflow['jobs'])} jobs",
      "Attempt(s)",
      wflow['attempt']
    ],
    *[[
      (lambda d: f"[{d}]({run_url}/job/{d})")(job['databaseId']),
      _conclusion(job['conclusion']),
      job['name'].replace('|','\\|'),
      job['startedAt'],
      (dt.fromisoformat(job['completedAt']) - dt.fromisoformat(job['startedAt'])) if job['conclusion'] else '-'
    ] for job in wflow['jobs']]
  ])

with open(environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as ghs:
  ghs.write(tabulate(
    mdtables,
    headers=['']*5,
    tablefmt='github'
  )+'\n')
