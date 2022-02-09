#!/usr/bin/env python3

# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

from pathlib import Path
from urllib import request
from json import dump, load
from rich import print as rprint


def DumpRegistryDataToJSON(ddir, idx):
    """
    Retrieve data from a container registry through the v2 API and save it to JSON files.

    For now, gcr.io is supported only.
    """
    ddir.mkdir(parents=True, exist_ok=True)
    print(f"[DumpRegistryDataToJSON] Request {idx}")
    data = loads(request.urlopen(f'https://gcr.io/v2/{idx}/tags/list').read())
    print(data['name'])
    with (ddir / f"{idx.replace('/','--')}.json").open('w') as fptr:
        dump(data, fptr)
    for item in data['child']:
        DumpRegistryDataToJSON(f"{idx}/{item}")


def ReadDigestsFromJSON(ddir):
    """
    Read JSON files and generate a dictionary of digests with metadata (names and tags).
    """
    print(f"[DumpRegistryDataToJSON] JSON files location: {ddir}")
    Digests = {}
    for item in ddir.iterdir():
        name = item.stem.replace('--','/')
        with item.open('r') as fptr:
            data = load(fptr)
        for digest, data in data['manifest'].items():
            if len(data['tag']) != 0:
                if digest not in Digests:
                    Digests[digest] = {
                        name: data['tag']
                    }
                    continue
                if name not in Digests[digest]:
                    Digests[digest][name] = data['tag']
                else:
                    Digests[digest][name] += data['tag']
    return Digests


def DigestsToImages(digests):
    """
    Transform a dictionary of digests with data into a dictionary of images with data.

    Use the complete image names (REGISTRY/ARCHITECTURE/COLLECTION/...) as keys.
    """
    Images = {}
    for digest, data in digests.items():
        for name, tags in data.items():
            items = name.split('/')
            if len(items) < 3:
                continue
            if any(collection_root in name.split('/')[2] for collection_root in ['debian', 'centos']):
                data.pop(name)
                break
        print(name)
        if name not in Images:
            Images[name] = {
                digest: {
                    'tags': tags,
                    'other': data
                }
            }
        else:
            if digest in Images[name]:
                raise Exception(f"Digest {digest} exists already!")
            Images[name][digest] = {
                'tags': tags,
                'other': data
            }
    return Images


def ImagesToTree(images):
    """
    Extract the hierarchy from image names (keys) and build a tree dictionary.
    """
    Hierarchy = {}
    for name, data in images.items():
        def walk(obj, items):
            item = items[0]
            if item not in obj:
                obj[item] = {}
            if len(items) > 1:
                walk(obj[item], items[1:])
            else:
                obj[item]['data'] = {
                    'name': name,
                    'items': data
                }
        walk(Hierarchy, name.split('/'))
    return Hierarchy


def TreeFromJSON(ddir):
    """
    Shortcut for JSON -> dictionary of Digests -> dictionary of Images -> Tree.
    """
    return ImagesToTree(DigestsToImages(ReadDigestsFromJSON(ddir)))


if __name__ == "__main__":
    sys_exit(OSVDE(tk.Tk()).mainloop())

    ROOT = Path(__file__).resolve().parent / 'registry'
    if not ROOT.exists():
        DumpRegistryDataToJSON(ROOT, 'hdl-containers')
    rprint(TreeFromJSON(ROOT))
