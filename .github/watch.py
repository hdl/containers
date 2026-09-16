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
from typing import Dict, List, Any, Tuple

class _watchout(Enum):
  COMPLETED = 0
  CANCELLED = 1
  TIMEDOUT = 2
  SCHEDULER = 3

RERUN: int = int(environ['GH_INPUT_RERUN'])

LOGGER: Queue[Tuple[str, str]] = Queue()
SYNC: Queue[Tuple[Thread, _watchout]] = Queue()
SCHEDULER: Dict[str, str] = {}

INTERVAL: int = 60

def _log() -> None:
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

def _scheduler(idx: str) -> None:
  try:
    view: Dict[str, Any] = {
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
          'scheduler': view['conclusion'],
          **{
          job['name'].split(' / ')[1].removesuffix('-results'): job['conclusion']
          for job in view['jobs'] if job['status'] == 'completed'
        }})
  finally:
    SYNC.put((current_thread(), _watchout.CANCELLED if view['conclusion'] == 'cancelled' else _watchout.COMPLETED))

def _wait(wflow: str, _: str) -> None:
  try:
    LOGGER.put(('p', f"Waiting {wflow}..."))
    if wflow not in SCHEDULER:
      sleep(INTERVAL)
  finally:
    SYNC.put((current_thread(), _watchout.SCHEDULER))

def _watch(wflow: str, idx: str) -> None:
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

def _dispatch(wflow: str, data: Dict[str, Any]) -> None:
  idx = check_output([
      "gh", "workflow", "run", "build-test-release.yml", "-r", environ["GITHUB_REF_NAME"],
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

schedule: Dict[str, Any] = json_loads(environ['GH_INPUT_SCHEDULE'])
pending: Dict[str, Dict[str, Any]]
inprogress: List[Dict[str, Any]]
pending, inprogress = (schedule[k] for k in ('pending', 'inprogress'))
done: Dict[str, str] = schedule.get('done', {})
active: Dict[Thread, Dict[str, Any]] = {}

for wflow, data in list(pending.items()):
  if data['in'] == 0:
    _dispatch(wflow, data)

scheduler: Dict[str, Any] | None = next((wflow for wflow in inprogress if wflow['key'] == 'scheduler'), None)
if scheduler:
  scheduler_thread = Thread(target=_scheduler, args=(scheduler['idx'],))
  scheduler_thread.start()
  active[scheduler_thread] = scheduler
  inprogress.remove(scheduler)

def _startThread() -> None:
  wflow = inprogress.pop(0)
  thread = Thread(target=_wait if wflow['idx'] == 'scheduler' else _watch, args=(wflow['key'], wflow['idx']))
  thread.start()
  active[thread] = wflow

for _ in range(min(3, len(inprogress))):
  _startThread()

def _output() -> None:
  with open(environ['GITHUB_OUTPUT'], 'w', encoding='utf-8') as gho:
    gho.write(f"schedule={json_dumps({'pending': pending, 'inprogress': [*inprogress, *active.values()], 'done': done})}\n")

def _completed(wflow: Dict[str, Any]) -> None:
  done[wflow['key']] = wflow['idx']
  for node in wflow['out']:
    if node in pending:
      pending[node]['in'] -= 1
      if pending[node]['in'] == 0:
        _dispatch(node, pending[node])

def _cancelled(outs: List[str]) -> None:
  for node in outs:
    if node in pending:
      _cancelled(pending[node]['out'])
      done[node] = '!'
      del pending[node]

def _idxurl(idx: str) -> str:
  idx = idx.split('!')[0]
  return (
   f"https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{idx}"
   if idx != 'scheduler' else "scheduler"
  )

while active:
  _output()
  LOGGER.put(('p', '\n'.join([
    f"- {len(done)} done:",
    *[f"  - {wflow}: {_idxurl(idx)}" for wflow, idx in done.items()],
    f"- {len(inprogress)} inprogress:",
    *[f"  - {wflow['key']}: {_idxurl(wflow['idx'])}" for wflow in inprogress],
    f"- {len(active)} active:",
    *[f"  - {wflow['key']}: {_idxurl(wflow['idx'])} {thread}" for thread, wflow in active.items()],
    f"- {len(pending)} pending:",
    *[f"  - {key}: {data}" for key, data in pending.items()],
  ])))
  thread, watchout = SYNC.get()
  wthr = active.pop(thread)
  thread.join()
  key = wthr['key']
  match watchout:
    case _watchout.TIMEDOUT:
      LOGGER.put(('p', f"{key}: timed out"))
      inprogress.append(wthr)
    case _watchout.CANCELLED:
      LOGGER.put(('p', f"{key}: cancelled"))
      done[wthr['key']] = f"{wthr['idx']}!"
      _cancelled(wthr['out'])
    case _watchout.COMPLETED:
      LOGGER.put(('p', f"{key}: completed"))
      _completed(wthr)
    case _watchout.SCHEDULER:
      _unknown = key not in SCHEDULER
      if _unknown and not bool(SCHEDULER.get('scheduler','')):
        inprogress.append(wthr)
      else:
        if _unknown:
          SCHEDULER[key] = 'hidden'
        match SCHEDULER[key]:
          case 'cancelled':
            LOGGER.put(('p', f"{key}: cancelled"))
            done[wthr['key']] = f"{wthr['idx']}!"
            _cancelled(wthr['out'])
          case _:
            LOGGER.put(('p', f"{key}: completed {SCHEDULER[key]}"))
            _completed(wthr)
    case _:
      raise Exception(f"Unknown thread exit <{watchout}>!")
  for _ in range(min(4-len(active), len(inprogress))):
    _startThread()

_output()
LOGGER.put(('z', 'hdlc::watch::main::close'))
logger_thread.join()
