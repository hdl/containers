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

from typing import Dict, List, Tuple
from pathlib import Path

# https://github.com/asottile/dockerfile
import dockerfile
from graphviz import Digraph

from build import DefaultOpts


ROOT = Path(__file__).resolve().parent
CDIR = ROOT.parent / "debian-buster"


class Stage:
    value: str = None
    tag: str = None
    depends: List[str]

    def __init__(self):
        self.depends = []

    def addDep(self, val: str):
        self.depends.append(val)


class Dockerfile:
    argimg: str = None
    stages: List[Stage]
    artifacts: List[Tuple[str, str, str]]

    def __init__(self):
        self.stages = []
        self.artifacts = []

    def addStage(self, stg: Stage):
        self.stages.append(stg)

    def addArtifact(self, art: Tuple[str, str, str]):
        self.artifacts.append(art)

    def markOrigin(self, val: str):
        """
        Check if a name/id corresponds to another image, an stage or an external image.
        """
        return (
            # Depends on another image in the collection
            "!R|" + " ".join(val.split("/")[1:])
            if val.startswith("$REGISTRY")
            # Depends on an internal stage
            else ("!I|" + val)
            if val in [pstg.tag for pstg in self.stages]
            # Is an external dependency
            else val
        )


class CollectionGraph:
    dfiles: List[str]
    imgs: List[str]
    pkgs: List[str]
    exts: List[str]

    def __init__(self):
        self.dfiles = []
        self.imgs = []
        self.pkgs = []
        self.exts = []

    def addItem(self, item: str):
        if item.startswith("!R|"):
            _label = item[3:]
            if _label.startswith("pkg:"):
                self.pkgs.append(_label)
            else:
                self.imgs.append(_label)
        elif item.startswith("!I|"):
            print("TODO: internal stage deps")
            return None
        else:
            _label = item
            self.exts.append(_label)
        return _label


class CollectionMap:
    data: Dict[str, Dockerfile]

    def __init__(self):
        self.data = {}

    def addDockerfile(self, name: str, dfile: Dockerfile):
        if name in self.data:
            raise Exception(f"Dockerfile <{name}> exists already!")
        self.data[name] = dfile

    def report(self):
        """
        Print report of the map data
        """
        for key, dfile in self.data.items():
            print(f"· {key} [{len(dfile.stages)}]")
            for art in dfile.artifacts:
                print(
                    f"  > {art[0]}"
                    + (f" [{art[1]}]" if art[1] is not None else "")
                    + (f" <{art[2]}>" if art[2] is not None else "")
                )
            for stg in dfile.stages:
                print(
                    f"  - {stg.value}"
                    + (f" [{stg.tag}]" if stg.tag is not None else "")
                )
                for dep in stg.depends:
                    print("    +", dep)

    def dotgraph(self):
        """
        Generate a graphviz dot diagram and render it to a SVG file
        """
        dot = Digraph(
            comment="OCI images maintained in hdl/containers",
            filename="map",
            format="svg",
        )

        graph = CollectionGraph()

        for key, dfile in self.data.items():
            graph.dfiles.append(key)

            for art in dfile.artifacts:
                _val = art[0]
                _val = graph.addItem(art[0])
                if _val is None:
                    raise Exception(f"Artifact <{_val}> should be a known image!")
                dot.edge(f"d_{key}", _val.replace(":", "--"), style="dotted")

            arts = [art[0] for art in dfile.artifacts]

            for stg in dfile.stages:
                if stg.value in arts:
                    # For now, we ignore edges about reusing images in the same dockerfile
                    continue
                if stg.value == "!R|$IMAGE":
                    # We ignore the edges with '$IMAGE' as a source; we handle them below
                    continue
                _val = graph.addItem(stg.value)
                if _val is None:
                    continue
                dot.edge(_val.replace(":", "--"), f"d_{key}")

            deps = [art[2] for art in dfile.artifacts if art[2] is not None]
            if dfile.argimg is not None:
                for dep in deps + [dfile.argimg]:
                    dot.edge(dep.replace(":", "--"), f"d_{key}")

        for item in [
            (graph.imgs, "limegreen"),
            (graph.pkgs, "mediumblue"),
            (graph.exts, "orange"),
        ]:
            for img in list(set(item[0])):
                dot.node(
                    img.replace(":", "--"),
                    label=img,
                    shape="cylinder",
                    color=item[1],
                    fontcolor=item[1],
                )

        for dfile in list(set(graph.dfiles)):
            dot.node(
                f"d_{dfile}",
                label=dfile,
                shape="note",
                color="dodgerblue",
                fontcolor="dodgerblue",
            )

        dot.render()

    def elkjsgraph(self):
        """
        Generate a elkjs JSON diagram
        """

        graph = {
            "id": "root",
            "layoutOptions": {
                "elk.algorithm": "layered"
            },
            "children": [
                    {"id": "n1", "width": 30, "height": 30},
             ],
            "edges": [
              #{"id": "e1", "sources": ["n1"], "targets": ["n2"]},
              #{"id": "e2", "sources": ["n1"], "targets": ["n3"]}
            ]
        }

        for key, dfile in self.data.items():
            print(key)
#            graph.dfiles.append(key)

#            for art in dfile.artifacts:
#                _val = art[0]
#                _val = graph.addItem(art[0])
#                if _val is None:
#                    raise Exception(f"Artifact <{_val}> should be a known image!")

        # JS script for generating an SVG output from a JSON/object. Requires 'elkjs-svg'.
        nodeRun = """
        const ELK = require('elkjs')
        const elksvg = require('elkjs-svg');
        var graph = {}
        const elk = new ELK()
        elk.layout(graph)
          .then(data => {
            var renderer = new elksvg.Renderer();
            var svg = renderer.toSvg(data);
            console.log(svg);
          })
        """

def GenerateMap(debug: bool = False):
    """
    Parse all the dockerfiles in a collection and extract the stages and the dependencies (images) of each stage;
    cross-relate them with the declarations of default images; and build a map of all the images in the collection.
    """

    cmap = CollectionMap()

    for dfilename in [Path(x.name).stem for x in CDIR.glob("*.dockerfile")]:
        if debug:
            print("·", dfilename)

        dfile = Dockerfile()

        stg = None

        for item in dockerfile.parse_file(str(CDIR / f"{dfilename}.dockerfile")):

            if item.cmd == "arg":
                _val = item.value[0]
                if not _val.startswith("REGISTRY="):
                    if _val.startswith("IMAGE="):
                        if dfile.argimg is not None:
                            raise Exception(
                                f"ARG IMAGE was already defined in <{dfilename}> [{_val}]!"
                            )
                        # Extract image name from IMAGE="name"
                        dfile.argimg = _val[7:-1]
                    else:
                        raise Exception(f"Unknown ARG <{_val}>!")

                continue

            if item.cmd == "from":
                if stg is not None:
                    # This was not the first stage in this dockerfile, save the previous one
                    dfile.addStage(stg)

                stg = Stage()

                _val = item.value[0]
                stg.value = dfile.markOrigin(_val)
                if len(item.value) != 1:
                    # Second argument must be 'AS', between the image and the tag
                    if item.value[1].upper() != "AS":
                        raise Exception("Second item should be 'AS'!")
                    stg.tag = item.value[2]

                continue

            if item.cmd == "copy":
                if "--from=" not in item.flags[0].lower():
                    raise Exception(
                        f"Second item of <{item.flags}> should be '--from=*'!"
                    )
                stg.addDep(dfile.markOrigin(item.flags[0][7:]))

                continue

            if item.cmd == "run" and len(item.flags) > 0:
                _val = item.flags[0]
                if _val.startswith("--mount=type="):
                    stg.addDep(dfile.markOrigin(_val.split(",from=")[1].split(",")[0]))
                else:
                    raise Exception(f"Unknown RUN flag <{_val}>!")

        if stg is None:
            raise Exception(f"No stages found in dockerfile <{dfilename}>!")

        dfile.addStage(stg)

        cmap.addDockerfile(dfilename, dfile)

    for key, args in DefaultOpts.items():
        if args[0] not in cmap.data:
            raise Exception(f"Dockerfile <{args[0]}> not found in data!")
        cmap.data[args[0]].addArtifact((f"!R|{key}", args[1], args[2]))

    return cmap


if __name__ == "__main__":
    # print(dockerfile.all_cmds())

    cmap = GenerateMap(True)
    cmap.report()
    cmap.dotgraph()
