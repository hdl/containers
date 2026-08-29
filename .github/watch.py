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

def _watch(item):
  try:
    key=item.split('=')
    idx=key[1]
    key=key[0]

    conclusion = 'failure'
    attempt = 0

    while conclusion == 'failure' and attempt<RERUN:
      if attempt>0:
        LOGGER.put(('p', f"Rerun {item} after attempt {attempt}"))
        check_call(["gh", "run", "rerun", idx, "--failed"])
      LOGGER.put(('p', f"Watching {item}..."))
      check_call(["gh", "run", "watch", idx, "-i", str(300)], stdout=DEVNULL)
      LOGGER.put(('p', f"Completed {item}"))
      view = json_loads(check_output(['gh', 'run', 'view', idx, '--json', 'attempt,conclusion'], encoding='utf-8'))
      attempt = int(view['attempt'])
      conclusion = view['conclusion']

    mdref=f"{key}: [{idx}](https://github.com/{environ['GITHUB_REPOSITORY']}/actions/runs/{idx})"
    LOGGER.put(('s', f"- {mdref} | {conclusion} [{attempt}]" ))

  finally:
    SYNC.put(current_thread())

logger_thread = Thread(target=_log)
logger_thread.start()

pending = environ['GH_INPUT_IDS'].split(' ')
active = {}

def _startThread():
  if not pending:
    return
  item = pending.pop(0)
  thread = Thread(target=_watch, args=(item,))
  thread.start()
  active[thread] = item

for _ in range(min(3, len(pending))):
  _startThread()

done = []

while active:
  thread = SYNC.get()
  item = active.pop(thread)
  thread.join()
  done.append(item)
  LOGGER.put(('p', f"Thread {item} finished"))
  _startThread()
  LOGGER.put(('p', '\n'.join([
    f"- {len(done)} done: {done}",
    f"- {len(pending)} pending: {pending}",
    f"- {len(active)} active: {active}"
  ])))

LOGGER.put('z', 'hdlc::watch::main::close')
logger_thread.join()
