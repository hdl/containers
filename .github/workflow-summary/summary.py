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

metadata = {}
for item in Path('.').glob('*.json'):
  with open(item, 'r', encoding='utf-8') as ptr:
    content = json_load(ptr)
    if 'key' not in content:
      metadata[item.stem] = content

for job in json_loads(environ['GH_OUTPUT_MATRIX']):

  for idx, item in metadata.items():

    _status = item['status']
    _architecture = item['architecture']
    _collection = item['collection']
    _images = ' '.join(item['images'])
    _pull = item['pull']

    if (
      job['arch'] == _architecture and
      job['os'] == _collection and
      job['imgs'] == _images
    ):

      summary = [f"{_status} {_architecture}/{_collection} | {_images}"]
      if _pull:
        summary.extend([
          "",
          "- Pull:",
          *[f"  - {img}" for img in _pull],
          ""
        ])

      with open(f'{idx}.md', 'r') as rptr, open(environ['GITHUB_STEP_SUMMARY'], 'a') as aptr:
        aptr.write(f"<details>\n\n<summary>\n{'\n'.join(summary)}\n</summary>\n\n")
        if _status != 'success':
          aptr.write("See partial job summary.\n")
        copyfileobj(rptr, aptr)
        aptr.write('\n</details>\n\n')

      del metadata[idx]

      break

  else:

    raise Exception(f"Summary metadata of job <{job}> not found!")
