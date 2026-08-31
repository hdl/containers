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
from json import loads as json_loads
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

def _scheduler(keyidx, idx):
  try:
    view = {
      'conclusion': 'failure',
      'attempt': 0
    }
    while view['conclusion'] == 'failure' and view['attempt']<RERUN:
      if view['attempt']>0:
        LOGGER.put(('p', f"Rerun {keyidx} after attempt {view['attempt']}"))
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

def _wait(keyidx, _):
  try:
    LOGGER.put(('p', f"Waiting {keyidx}..."))
    if keyidx.split('=')[0].split(':')[0] not in SCHEDULER:
      sleep(INTERVAL)
  finally:
    SYNC.put((current_thread(), _watchout.SCHEDULER))

def _watch(keyidx, idx):
  timeout = False
  try:
    conclusion = 'failure'
    attempt = 0
    while conclusion == 'failure' and attempt<RERUN:
      if attempt>0:
        LOGGER.put(('p', f"Rerun {keyidx} after attempt {attempt}"))
        check_call(["gh", "run", "rerun", idx, "--failed"])
      LOGGER.put(('p', f"Watching {keyidx}..."))
      try:
        check_call(["gh", "run", "watch", idx, "-i", str(INTERVAL)], stdout=DEVNULL, timeout=210)
      except TimeoutExpired:
        timeout = True
        return
      LOGGER.put(('p', f"Completed {keyidx}"))
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

def _dispatch(key):
  fkey = f'{key}='
  key, skip = key.split(':') if ':' in key else (key, '')
  idx = check_output([
      "gh", "workflow", "run", ".build-test-release.yml", "-r", environ["GITHUB_REF_NAME"],
      "-f", f"key={key}",
      "-f", f"skip-test={str('T' in skip)}",
      "-f", f"skip-release={str('R' in skip)}",
      "-f", f"message={environ['GH_INPUT_MESSAGE']}"
    ], encoding="utf-8").split('/')[-1].strip()
  LOGGER.put(('p', f"Dispatched {fkey[0:-1]}: https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{idx}"))
  return fkey + idx

logger_thread = Thread(target=_log)
logger_thread.start()

active = {}
done = []
pending = [
  task if '=' in task[0] else [_dispatch(task[0]), *task[1:]]
  for task in [task.split('>') for task in environ['GH_INPUT_IDS'].split()]
]

LOGGER.put(('p', '\n'.join(['Tasks:', *["  " * k + f"- {key.split('=')[0]}" +
  ((
    f": https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{key.split('=')[1]}"
    if key.split('=')[1] != 'scheduler' else ": scheduler"
  ) if '=' in key else "")
  for task in pending
  for k, key in enumerate(task)
]])))

if (lambda k: k if '!' not in k else k.split('!')[1])(pending[0][0].split('=')[0].split(':')[0]) == 'scheduler':
  task = pending.pop(0)
  scheduler_thread = Thread(target=_scheduler, args=(task[0], task[0].split('=')[1]))
  scheduler_thread.start()
  active[scheduler_thread] = (task, 0)

def _startThread():
  if not pending:
    return
  while '!' in (task := pending.pop(0))[-1]:
    done.append(task)
  for k, keyidx in enumerate(task):
    if '=' not in keyidx:
      task[k] = _dispatch(keyidx)
      break
    elif '!' not in keyidx:
      break
  idx = task[k].split('=')[1]
  thread = Thread(target=_wait if idx == 'scheduler' else _watch, args=(task[k], idx))
  thread.start()
  active[thread] = (task, k)

for _ in range(min(3, len(pending))):
  _startThread()

def _output():
  with open(environ['GITHUB_OUTPUT'], 'w', encoding='utf-8') as gho:
    gho.write(f"ids={' '.join(['>'.join(task) for task in [*done, *pending, *[task for task, _ in active.values()]]])}\n")

while active:
  _output()
  thread, watchout = SYNC.get()
  task, k = active.pop(thread)
  thread.join()
  match watchout:
    case _watchout.TIMEDOUT:
      LOGGER.put(('p', f"{task[k]}: timed out"))
      pending.append(task)
    case _watchout.CANCELLED:
      LOGGER.put(('p', f"{task[k]}: cancelled"))
      done.append([*task[0:k], *[f"X!{key}" for key in task[k:]]])
    case _watchout.COMPLETED:
      task[k] = f"!{task[k]}"
      if k < len(task)-1:
        LOGGER.put(('p', f"{task[k]}: finished"))
        pending.append(task)
      else:
        LOGGER.put(('p', f"{task[k]}: completed"))
        done.append(task)
    case _watchout.SCHEDULER:
      key = task[k].split('=')[0].split(':')[0]
      if key not in SCHEDULER:
        pending.append(task)
      else:
        match SCHEDULER[key]:
          case 'cancelled':
            LOGGER.put(('p', f"{task[k]}: cancelled"))
            done.append([*task[0:k], *[f"X!{keyidx}" for keyidx in task[k:]]])
          case _:
            LOGGER.put(('p', f"{task[k]}: finished"))
            task[k] = f"!{task[k]}"
            pending.append(task)
    case _:
      raise Exception(f"Unknown thread exit <{watchout}>!")
  _startThread()
  LOGGER.put(('p', '\n'.join([
    f"- {len(done)} done: {done}",
    f"- {len(pending)} pending: {pending}",
    f"- {len(active)} active: {active}"
  ])))

_output()
LOGGER.put(('z', 'hdlc::watch::main::close'))
logger_thread.join()
