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
import networkx as nx
from json import dumps as json_dumps
from subprocess import check_output

ROOT = Path(__file__).parent

evname = environ["GITHUB_EVENT_NAME"]
skip_release = evname == 'pull_request'

match evname:
  case "push":
    input_tasks = environ["HDLC_PUSH"].split()
  case "schedule":
    input_tasks = environ["HDLC_SCHEDULE"].split()
  case "workflow_dispatch":
    input_tasks = environ["GH_INPUT_TASKS"].split()
    skip_release = environ["GH_INPUT_SKIP-RELEASE"]
  case _:
    input_tasks = ""
    raise Exception(f"Empty tasks list for event name <{evname}>!")

if not input_tasks:
  raise Exception(f"Empty list of tasks!")

skips = {}
for t, task in enumerate(input_tasks):
  if ':' in task:
    task, skip = task.split(':')
    input_tasks[t] = task
    skips[task] = skip

G = nx.nx_agraph.read_dot(ROOT/"needs.dot")

if not nx.is_directed_acyclic_graph(G):
  raise RuntimeError("Dependency graph contains a cycle!")

if 'base' not in input_tasks:
  G.remove_node('base')

# F>: descendants of F and F
# >T: ancestors of T and T
# F>T: nodes which are both descendants of F and ascendants of T, and both F and T
dnodes = set()
for key in input_tasks:
  if '>' not in key:
    dnodes.add(key)
    continue
  nfrom, nto = key.split('>')
  if nfrom and nto:
    dnodes.update({nfrom, nto} | (nx.ancestors(G, nto) & nx.descendants(G, nfrom)))
  elif nfrom:
    dnodes.update({nfrom} | nx.descendants(G, nfrom))
  else:
    dnodes.update({nto} | nx.ancestors(G, nto))

unknown = dnodes - set(G.nodes)
if unknown:
  raise ValueError(f"Unknown tasks: {sorted(unknown)}")

D = G.subgraph(dnodes).copy()

with open(environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as ghs:
  ghs.write('\n'.join([
  "```mermaid",
  "graph TD",
  *[f"{u} --> {v}" for u, v in D.edges],
  "```",
  ""
]))

for node in dnodes:
  if ':' in node:
    task, skip = node.split(':')
    nx.relabel_nodes(D, {node: task}, copy=False)
    skips[task] = skip

# Precompute the number of predecessors and the list of successors of each node to dynamically dispatch workflows using
# Kahn's algorithm
pending = {
  node: {
    'out': list(D.successors(node)),
    'in': degree,
    'skip-test': (node in skips) and ('T' in skips[node]),
    'skip-release': skip_release or ((node in skips) and ('R' in skips[node])),
   } for node, degree in dict(D.in_degree()).items()
}
inprogress = [{
  'key': 'scheduler',
  'idx': environ['GITHUB_RUN_ID'],
  'out': []
}]

call_wflow = []

for wflow in [
  wflow for wflow, data in pending.items()
  if data['in'] == 0 and wflow not in ['formal', 'impl']
]:
  call_wflow.append({'key': wflow, **{key: pending[wflow][key] for key in ['skip-test', 'skip-release']}})
  inprogress.append({ 'key': wflow, 'idx': 'scheduler', 'out': pending[wflow]['out'] })
  del pending[wflow]

with open(environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as gho:
  gho.write("cout=" + json_dumps({
    "matrix": call_wflow if call_wflow else 'skip',
    "skip-release": skip_release
  }))

watchurl = check_output([
  "gh", "workflow", "run", ".watch.yml", "-r", environ['GITHUB_REF_NAME'],
  "-f", f"schedule={json_dumps({'pending': pending, 'inprogress': inprogress})}",
  "-f", f"rerun={environ['GH_INPUT_RERUN']}",
  "-f", f"message={environ['GITHUB_SHA'][0:8]} " + (
    evname if evname in ['schedule', 'workflow_dispatch'] else environ['GH_MESSAGE'].split('\n')[0]
  )
], encoding="utf-8")

with open(environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as ghs:
  ghs.write('\n'.join([
    f"- Event: {evname}",
    f"- Watch: [{watchurl.split('/')[-1]}]({watchurl})",
    "- In progress:",
    *[f"  - {item['key']}" for item in inprogress],
    "- Pending:",
    *[f"  - {key}" for key in pending],
    ""
  ]))
