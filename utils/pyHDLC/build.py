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

from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from run import _exec

DefaultOpts: Dict[str, Tuple[str, str, str]] = {
    "apicula": ["apicula", None, None],
    "pkg/apicula": ["apicula", "pkg", None],
    "arachne-pnr": ["arachne-pnr", None, None],
    "pkg/arachne-pnr": ["arachne-pnr", "pkg", None],
    "build/base": ["base", "base", None],
    "build/build": ["base", "build", None],
    "build/dev": ["base", None, None],
    "pkg/boolector": ["boolector", None, None],
    "pkg/cvc": ["cvc", None, None],
    "formal/min": ["formal", "min", None],
    "formal": ["formal", "latest", None],
    "formal/all": ["formal", None, None],
    "pkg/ghdl-yosys-plugin": ["ghdl-yosys-plugin", "pkg", None],
    "ghdl/yosys": ["ghdl-yosys-plugin", None, None],
    "pkg/ghdl": ["ghdl", "pkg-mcode", None],
    "pkg/ghdl/llvm": ["ghdl", "pkg-llvm", None],
    "ghdl": ["ghdl", "mcode", None],
    "ghdl/llvm": ["ghdl", "llvm", None],
    "pkg/gtkwave": ["gtkwave", None, None],
    "pkg/icestorm": ["icestorm", "pkg", None],
    "icestorm": ["icestorm", None, None],
    "build/impl": ["impl", "base", None],
    "impl/ice40": ["impl", "ice40", None],
    "impl/icestorm": ["impl", "icestorm", None],
    "impl/ecp5": ["impl", "ecp5", None],
    "impl/prjtrellis": ["impl", "prjtrellis", None],
    "impl/generic": ["impl", "generic", None],
    "impl/pnr": ["impl", "pnr", None],
    "impl": ["impl", None, None],
    "iverilog": ["iverilog", None, None],
    "pkg/iverilog": ["iverilog", "pkg", None],
    "klayout": ["klayout", None, None],
    "pkg/klayout": ["klayout", "pkg", None],
    "magic": ["magic", None, None],
    "pkg/magic": ["magic", "pkg", None],
    "netgen": ["netgen", None, None],
    "pkg/netgen": ["netgen", "pkg", None],
    "build/nextpnr/base": ["nextpnr", "base", None],
    "build/nextpnr/build": ["nextpnr", "build", None],
    "pkg/nextpnr/ice40": ["nextpnr", "pkg-ice40", None],
    "nextpnr/ice40": ["nextpnr", "ice40", None],
    "nextpnr/icestorm": ["nextpnr", "icestorm", None],
    "pkg/nextpnr/nexus": ["nextpnr", "pkg-nexus", None],
    "nextpnr/nexus": ["nextpnr", "nexus", None],
    "nextpnr/prjoxide": ["nextpnr", "prjoxide", None],
    "pkg/nextpnr/ecp5": ["nextpnr", "pkg-ecp5", None],
    "nextpnr/ecp5": ["nextpnr", "ecp5", None],
    "nextpnr/prjtrellis": ["nextpnr", "prjtrellis", None],
    "pkg/nextpnr/generic": ["nextpnr", "pkg-generic", None],
    "nextpnr/generic": ["nextpnr", "generic", None],
    "nextpnr": ["nextpnr", None, None],
    "openfpgaloader": ["openfpgaloader", None, None],
    "pkg/openfpgaloader": ["openfpgaloader", "pkg", None],
    "prjoxide": ["prjoxide", None, None],
    "pkg/prjoxide": ["prjoxide", "pkg", None],
    "prjtrellis": ["prjtrellis", None, None],
    "pkg/prjtrellis": ["prjtrellis", "pkg", None],
    "prog": ["prog", None, None],
    "sim": ["sim", None, None],
    "pkg/osvb": ["osvb", "pkg", None],
    "sim/osvb": ["osvb", None, None],
    "pkg/pono": ["pono", None, None],
    "sim/scypy-slim": ["scypy", None, None],
    "sim/scypy": ["osvb", None, "sim/scypy-slim"],
    "sim/octave-slim": ["octave", None, None],
    "sim/octave": ["osvb", None, "sim/octave-slim"],
    "pkg/superprove": ["superprove", None, None],
    "pkg/symbiyosys": ["symbiyosys", None, None],
    "verilator": ["verilator", None, None],
    "pkg/verilator": ["verilator", "pkg", None],
    "vtr": ["vtr", None, None],
    "pkg/vtr": ["vtr", "pkg", None],
    "xyce": ["xyce", None, None],
    "pkg/xyce": ["xyce", "pkg", None],
    "pkg/yices2": ["yices2", None, None],
    "yosys": ["yosys", None, None],
    "pkg/yosys": ["yosys", "pkg", None],
    "pkg/z3": ["z3", None, None],
}


def BuildImage(
    image: Union[str, List[str]],
    registry: Optional[str] = "gcr.io/hdl-containers",
    collection: Optional[str] = "debian/bullseye",
    architecture: Optional[str] = "amd64",
    dockerfile: Optional[str] = None,
    target: Optional[str] = None,
    argimg: Optional[str] = None,
    pkg: Optional[bool] = False,
    dry: Optional[bool] = False,
    default: Optional[bool] = False,
) -> None:
    def _build(img, reg, collection, dfile, tgt, argimg, pkg):
        if default:
            [dfile, tgt, argimg] = DefaultOpts[img]

        if dfile is None:
            dfile = img

        if pkg is True:
            img = f"pkg/{img}"
            if tgt is None:
                tgt = "pkg"

        _imageName = "{0}/{1}/{2}/{3}".format(reg, architecture, collection, img)

        cmd = ["docker", "build"]
        cmd += ["--progress=plain", "--build-arg", "BUILDKIT_INLINE_CACHE=1"]
        cmd += [
            "--build-arg",
            "ARCHITECTURE={0}".format(architecture)
            if dfile == "base"
            else "REGISTRY={0}/{1}/{2}".format(registry, architecture, collection),
        ]
        cmd += ["-t", _imageName]

        if tgt is not None:
            cmd += ["--target={0}".format(tgt)]

        if argimg is not None:
            cmd += ["--build-arg", "IMAGE={0}".format(argimg)]

        _dfile = Path(collection.replace("/", "-")) / "{0}.dockerfile".format(dfile)
        if not _dfile.exists():
            raise Exception("Dockerfile <{0}> does not exist!".format(_dfile))

        cmd += ["-f", str(_dfile), "."]

        _exec(args=cmd, dry=dry, collapse=f"Build {_imageName}")

    for _image in [image] if isinstance(image, str) else image:
        _build(_image, registry, collection, dockerfile, target, argimg, pkg)
