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
from threading import Thread, current_thread
from time import sleep
from queue import Queue
from subprocess import DEVNULL, TimeoutExpired, check_call, check_output
from json import loads as json_loads, dumps as json_dumps
from enum import Enum

class _watchout(Enum):
  COMPLETED = 0
  CANCELLED = 1
  TIMEDOUT = 2
  SCHEDULER = 3

RERUN = int(environ['GH_INPUT_RERUN'])

LOGGER = Queue()
SYNC = Queue()
SCHEDULER = {}

INTERVAL = 60

def _log():
  while True:
    cmd, content = LOGGER.get()
    match cmd:
      case 'z':
        print(f"Exiting function log [{content}]")
        break
      case 'p':
        print(content)
      case _:
        raise Exception(f"Unknown log type <{cmd}>!")

def _scheduler(idx):
  try:
    view = {
      'conclusion': 'failure',
      'attempt': 0
    }
    while view['conclusion'] == 'failure' and view['attempt']<RERUN:
      if view['attempt']>0:
        LOGGER.put(('p', f"Rerun scheduler after attempt {view['attempt']}"))
        check_call(["gh", "run", "rerun", idx, "--failed"])
      view['status'] = 'queued'
      while view['status'] != 'completed':
        sleep(INTERVAL)
        jobs_pick = 'map( pick(.name, .status, .conclusion) | select(.name | test("-results$")))'
        jobs = json_loads(check_output([
            'gh', 'api', '-X', 'GET', 'repos/{owner}/{repo}/actions/runs/'f'{idx}/jobs',
            '-f', 'filter=all', '-f', 'per_page=100', '-q', f'.jobs | {jobs_pick}',
        ], encoding='utf-8'))
        view = json_loads(check_output([
          'gh', 'run', 'view', idx, '--json', 'attempt,status,conclusion,jobs', '-q', f'.jobs |= {jobs_pick}'
        ], encoding='utf-8'))
        if not view['jobs']:
          view['jobs'] = jobs
        SCHEDULER.update({
          job['name'].split(' / ')[1].removesuffix('-results'): job['conclusion']
          for job in view['jobs'] if job['status'] == 'completed'
        })
  finally:
    SYNC.put((current_thread(), _watchout.CANCELLED if view['conclusion'] == 'cancelled' else _watchout.COMPLETED))

def _wait(wflow, _):
  try:
    LOGGER.put(('p', f"Waiting {wflow}..."))
    if wflow not in SCHEDULER:
      sleep(INTERVAL)
  finally:
    SYNC.put((current_thread(), _watchout.SCHEDULER))

def _watch(wflow, idx):
  timeout = False
  try:
    conclusion = 'failure'
    attempt = 0
    while conclusion == 'failure' and attempt<RERUN:
      if attempt>0:
        LOGGER.put(('p', f"Rerun {wflow} after attempt {attempt}"))
        check_call(["gh", "run", "rerun", idx, "--failed"])
      LOGGER.put(('p', f"Watching {wflow}..."))
      try:
        check_call(["gh", "run", "watch", idx, "-i", str(INTERVAL)], stdout=DEVNULL, timeout=210)
      except TimeoutExpired:
        timeout = True
        return
      LOGGER.put(('p', f"Completed {wflow}"))
      attempt, conclusion = json_loads(check_output(
        ['gh', 'run', 'view', idx, '--json', 'attempt,conclusion', '-q', '[.attempt, .conclusion]'],
        encoding='utf-8'
      ))
  finally:
    SYNC.put((current_thread(),
      _watchout.TIMEDOUT if timeout else
      _watchout.CANCELLED if conclusion == 'cancelled' else
      _watchout.COMPLETED
    ))

def _dispatch(wflow, data):
  idx = check_output([
      "gh", "workflow", "run", ".build-test-release.yml", "-r", environ["GITHUB_REF_NAME"],
      "-f", f"key={wflow}",
      "-f", f"skip-test={data['skip-test']}",
      "-f", f"skip-release={data['skip-release']}",
      "-f", f"message={environ['GH_INPUT_MESSAGE']}"
    ] if wflow not in [
      'formal',
      'impl'
    ] else [
      "gh", "workflow", "run", f"{wflow}.yml", "-r", environ["GITHUB_REF_NAME"],
      "-f", f"message={environ['GH_INPUT_MESSAGE']}"
    ], encoding="utf-8").split('/')[-1].strip()
  LOGGER.put(('p', f"Dispatched {wflow}: https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{idx}"))
  del pending[wflow]
  inprogress.append({'key': wflow, 'idx': idx, 'out': data['out']})

logger_thread = Thread(target=_log)
logger_thread.start()

schedule = json_loads(environ['GH_INPUT_SCHEDULE'])
pending, inprogress = (schedule[k] for k in ('pending', 'inprogress'))
done = schedule.get('done', {})
active = {}

for wflow, data in list(pending.items()):
  if data['in'] == 0:
    _dispatch(wflow, data)

#LOGGER.put(('p', '\n'.join(['Tasks:', *["  " * k + f"- {key.split('=')[0]}" +
#  ((
#    f": https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{key.split('=')[1]}"
#    if key.split('=')[1] != 'scheduler' else ": scheduler"
#  ) if '=' in key else "")
#  for task in pending
#  for k, key in enumerate(task)
#]])))

scheduler = next((wflow for wflow in inprogress if wflow['key'] == 'scheduler'), None)
if scheduler:
  scheduler_thread = Thread(target=_scheduler, args=(scheduler['idx'],))
  scheduler_thread.start()
  active[scheduler_thread] = scheduler
  inprogress.remove(scheduler)

def _startThread():
  wflow = inprogress.pop(0)
  thread = Thread(target=_wait if wflow['idx'] == 'scheduler' else _watch, args=(wflow['key'], wflow['idx']))
  thread.start()
  active[thread] = wflow

for _ in range(min(3, len(inprogress))):
  _startThread()

def _output():
  with open(environ['GITHUB_OUTPUT'], 'w', encoding='utf-8') as gho:
    gho.write(f"schedule={json_dumps({'pending': pending, 'inprogress': [*inprogress, *active.values()], 'done': done})}\n")

def _completed(wflow):
  done[wflow['key']] = wflow['idx']
  for node in wflow['out']:
    pending[node]['in'] -= 1
    if pending[node]['in'] == 0:
      _dispatch(node, pending[node])

while active:
  _output()
  thread, watchout = SYNC.get()
  wflow = active.pop(thread)
  thread.join()
  key = wflow['key']
  match watchout:
    case _watchout.TIMEDOUT:
      LOGGER.put(('p', f"{key}: timed out"))
      inprogress.append(wflow)
#    case _watchout.CANCELLED:
#      LOGGER.put(('p', f"{key}: cancelled"))
#      done[f"!{key}"] = wflow['idx']
#      for node in wflow['out']:
#        if node in pending:
#          pending[f"!{node}"] = pending.pop(node)
    case _watchout.COMPLETED | _watchout.CANCELLED:
      LOGGER.put(('p', f"{key}: completed"))
      _completed(wflow)
    case _watchout.SCHEDULER:
      if key not in SCHEDULER:
        inprogress.append(wflow)
      else:
        match SCHEDULER[key]:
          case 'cancelled':
            LOGGER.put(('p', f"{key}: cancelled"))
            #done.append([*task[0:k], *[f"X!{keyidx}" for keyidx in task[k:]]])
          case _:
            LOGGER.put(('p', f"{key}: completed"))
            #task[k] = f"!{task[k]}"
            #pending.append(task)
        _completed(wflow)
    case _:
      raise Exception(f"Unknown thread exit <{watchout}>!")
  for _ in range(min(4-len(active), len(inprogress))):
    _startThread()
  LOGGER.put(('p', '\n'.join([
    f"- {len(done)} done: {done}",
    f"- {len(inprogress)} inprogress: {inprogress}",
    f"- {len(pending)} pending: {pending}",
    f"- {len(active)} active: {active}"
  ])))

_output()
LOGGER.put(('z', 'hdlc::watch::main::close'))
logger_thread.join()

#  Thread(target=watch,
#    kwargs={
#      "idx": idx
#    }
#  ).start()

# success
# failure
# cancelled
# skipped
#-
# startup_failure
# action_required
