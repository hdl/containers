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
from queue import Queue
from subprocess import DEVNULL, check_call, check_output
from json import loads as json_loads

RERUN = int(environ['GH_INPUT_RERUN'])

LOGGER = Queue()
SYNC = Queue()

def _log():
  while (content := LOGGER.get())[0] != 'z':
    match content[0]:
      case 'p':
        print(content[1])
      case 's':
        with open(environ["GITHUB_STEP_SUMMARY"], 'a') as ghs:
          ghs.write(f"{content[1]}\n")
      case _:
        raise Exception(f"Unknown log type <{content[0]}>!")
  print(f"Exiting function log")

def _watch(task):
  try:
    _, idx = task.split('=')
    conclusion = 'failure'
    attempt = 0
    while conclusion == 'failure' and attempt<RERUN:
      if attempt>0:
        LOGGER.put(('p', f"Rerun {task} after attempt {attempt}"))
        check_call(["gh", "run", "rerun", idx, "--failed"])
      LOGGER.put(('p', f"Watching {task}..."))
      check_call(["gh", "run", "watch", idx, "-i", str(300)], stdout=DEVNULL)
      LOGGER.put(('p', f"Completed {task}"))
      view = json_loads(check_output(['gh', 'run', 'view', idx, '--json', 'attempt,conclusion'], encoding='utf-8'))
      attempt = int(view['attempt'])
      conclusion = view['conclusion']
  finally:
    SYNC.put(current_thread())

logger_thread = Thread(target=_log)
logger_thread.start()

pending = environ['GH_INPUT_IDS'].split()
LOGGER.put(('p', '\n- '.join(['Tasks', *pending])))

for p, key in enumerate(pending):
  idx = None
  skip_test = False
  skip_release = False
  if '=' in key:
    key, idx = key.split('=')
  if ':' in key:
    key, skip = key.split(':')
    skip_test = 'T' in skip
    skip_release = 'R' in skip
  pending[p] = f'{key}=' + (idx if idx is not None else check_output([
      "gh", "workflow", "run", ".build-test-release.yml", "-r", environ["GITHUB_REF_NAME"],
      "-f", f"key={key}",
      "-f", f"skip-test={str(skip_test)}",
      "-f", f"skip-release={str(skip_release)}",
      "-f", f"message={environ['GH_INPUT_MESSAGE']}"
    ], encoding="utf-8").split('/')[-1].strip())

with open(environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as gho:
  gho.write(f"ids={' '.join(pending)}")

LOGGER.put(('p', '\n'.join(['Runs:', *[
  (lambda key, idx : f"- {key}: https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{idx}")
  (*task.split('=')) for task in pending
]])))

active = {}

def _startThread():
  if not pending:
    return
  task = pending.pop(0)
  thread = Thread(target=_watch, args=(task,))
  thread.start()
  active[thread] = task

for _ in range(min(3, len(pending))):
  _startThread()

done = []

while active:
  thread = SYNC.get()
  task = active.pop(thread)
  thread.join()
  done.append(task)
  LOGGER.put(('p', f"Thread {task} finished"))
  _startThread()
  LOGGER.put(('p', '\n'.join([
    f"- {len(done)} done: {done}",
    f"- {len(pending)} pending: {pending}",
    f"- {len(active)} active: {active}"
  ])))

LOGGER.put('z', 'hdlc::watch::main::close')
logger_thread.join()
