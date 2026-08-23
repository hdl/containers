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
from pathlib import Path
from shutil import copyfileobj
from json import load as json_load, loads as json_loads


def _summary(job, isfirst):
  _status = job['status']
  _pull = job['pull']
  return [
    f"<details>\n\n<summary>{_status} [{job['run_attempt']}]" +
    (isfirst * f" {job['architecture']}/{job['collection']} | {job['images']}")
  ] \
  + (len(_pull)>0) * [
    "",
    "- Pull:",
    *[f"  - {img}" for img in _pull],
    ""
  ] \
  + ["</summary>\n"] \
  + (_status != 'success') * ["\nSee partial job summary."]


metadata = {}
for job in Path('.').glob('*.json'):
  with open(job, 'r', encoding='utf-8') as ptr:
    content = json_load(ptr)
    if 'key' not in content:
      metadata[job.stem] = content

for job in json_loads(environ['GH_OUTPUT_MATRIX']):
  attempts = [
    {
      'idx': idx,
      **item,
      'images': ' '.join(item['images'])
    } for idx, item in metadata.items()
    if (
      job['arch'] == item['architecture'] and
      job['os'] == item['collection'] and
      job['imgs'] == ' '.join(item['images'])
    )
  ]

  if not attempts:
    raise Exception(f"Summary metadata of job <{job}> not found!")

  for idx in [dic['idx'] for dic in attempts]:
    del metadata[idx]

  isfirst = True
  with open(environ['GITHUB_STEP_SUMMARY'], 'a') as ghs:
    for job in sorted(attempts, key=lambda dic: dic['run_attempt'], reverse=True):
      ghs.write(f"{'\n'.join(_summary(job, isfirst))}\n")
      with open(f"{job['idx']}.md", 'r') as rptr:
        copyfileobj(rptr, ghs)
      if not isfirst:
        ghs.write('\n</details>\n')
      else:
        isfirst = False
    ghs.write('\n</details>\n')
