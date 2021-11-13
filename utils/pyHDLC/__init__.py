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
from pyHDLC.run import _exec

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
    "pkg/gtkwave": ["gtkwave", "pkg", None],
    "gtkwave": ["gtkwave", None, None],
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
    "sim/scipy-slim": ["scipy", None, None],
    "sim/scipy": ["osvb", None, "sim/scipy-slim"],
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


defaultRegistry = "gcr.io/hdl-containers"
defaultCollection = "debian/bullseye"
defaultArchitecture = "amd64"


def PullImage(
    image: Union[str, List[str]],
    registry: Optional[str] = defaultRegistry,
    collection: Optional[str] = defaultCollection,
    architecture: Optional[str] = defaultArchitecture,
    dry: Optional[bool] = False,
) -> None:
    for img in [image] if isinstance(image, str) else image:
        imageName = f"{registry}/{architecture}/{collection}/{img.split('#')[0]}"
        _exec(
            args=["docker", "pull", imageName], dry=dry, collapse=f"[Pull] Pull {imageName}"
        )


def BuildImage(
    image: Union[str, List[str]],
    registry: Optional[str] = defaultRegistry,
    collection: Optional[str] = defaultCollection,
    architecture: Optional[str] = defaultArchitecture,
    dockerfile: Optional[str] = None,
    target: Optional[str] = None,
    argimg: Optional[str] = None,
    pkg: Optional[bool] = False,
    dry: Optional[bool] = False,
    default: Optional[bool] = False,
    test: Optional[bool] = False,
) -> None:
    for rimg in [image] if isinstance(image, str) else image:

        items = rimg.split('#')
        pimg = items[0]
        withDir = None
        if len(items) > 1:
            withDir = items[1]

        if pimg.startswith('pkg/'):
            isPkg = True
            img = pimg[4:]
        else:
            isPkg = pkg
            img = pimg
            if pkg is True:
                pimg = f"pkg/{pimg}"

        if default:
            key = pimg
            if (isPkg is True) and (pimg not in DefaultOpts):
                key = img
            if key not in DefaultOpts:
                raise Exception(f"Key '{key}' is an unknown default image name!")
            [dockerfile, target, argimg] = DefaultOpts[key]

        if dockerfile is None:
            dockerfile = img

        if (pkg is True) and (target is None):
            target = "pkg"

        imageName = f"{registry}/{architecture}/{collection}/{pimg}"

        cmd = ["docker", "build", "-t", imageName, "--progress=plain", "--build-arg", "BUILDKIT_INLINE_CACHE=1"]
        cmd += [
            "--build-arg",
            f"ARCHITECTURE={architecture}"
            if dockerfile == "base"
            else f"REGISTRY={registry}/{architecture}/{collection}",
        ]

        if argimg is not None:
            cmd += ["--build-arg", f"IMAGE={argimg}"]

        if target is not None:
            cmd += [f"--target={target}"]

        dpath = Path(collection.replace("/", "-")) / f"{dockerfile}.dockerfile"
        if not dpath.exists():
            raise Exception(f"Dockerfile <{dpath}> does not exist!")

        cmd += ["-f", str(dpath), "."]

        _exec(args=cmd, dry=dry, collapse=f"[Build] Build {imageName}")

        if test:
            TestImage(
                f"{pimg}{(f'#{withDir}' if withDir is not None else '')}",
                registry,
                collection,
                architecture,
                dry,
            )


def TestImage(
    image: Union[str, List[str]],
    registry: Optional[str] = defaultRegistry,
    collection: Optional[str] = defaultCollection,
    architecture: Optional[str] = defaultArchitecture,
    dry: Optional[bool] = False,
) -> None:
    imagePrefix = f"{registry}/{architecture}/{collection}"
    for img in [image] if isinstance(image, str) else image:
        if img.startswith("pkg/"):
            pimg = img[4:]
            if '#' in pimg:
                # If a custom package location is specified, split it.
                [pimg, pdir] = pimg.split('#')
            else:
                # Otherwise, use the "escaped" image name as the location of the package.
                pdir = pimg.replace('/', '-')

            testScript = pimg.replace('/', '--')

            # The testScript is used as a tag for the temporary image.
            # Nevertheless, any other image name and/or tag might be used.
            testImage = f"{imagePrefix}/testpkg:{testScript}"

            _exec(args=[
                "docker",
                "build",
                "-t",
                f"{testImage!s}",
                "--progress=plain", "--build-arg", "BUILDKIT_INLINE_CACHE=1",
                "--build-arg",
                f"IMAGE={imagePrefix!s}/pkg/{pimg!s}",
                "--build-arg",
                f"PACKAGE={pdir!s}",
                "-f",
                str(Path(__file__).resolve().parent / "testpkg.dockerfile"),
                "."
            ], dry=dry, collapse=f"[Test] Build {testImage!s}")

            _exec(args=[
                "docker",
                "run",
                "--rm",
                "-v",
                f"{Path.cwd() / 'test'}://wrk",
                f"{testImage!s}",
                f"//wrk/{testScript}.pkg.sh"
            ], dry=dry, collapse=f"[Test] Test {testImage}")

            continue

        # If not a package image...

        imageName=f"{imagePrefix}/{img}"

        _exec(args=[
            'docker',
            'inspect',
            """--format={{ println "Architecture:" .Architecture .Variant }}{{ println "Size:" .Size }}VirtualSize: {{ .VirtualSize }}""",
            f"{imageName}"
        ], dry=dry, collapse=f"[Test] Inspect {imageName}")

        _exec(args=[
            'docker',
            'run',
            '--rm',
            '-v',
            f"{Path.cwd() / 'test'}://wrk",
            f"{imageName!s}",
            f"//wrk/{img.replace(':', '--').replace('/', '--')!s}.sh"
        ], dry=dry, collapse=f"[Test] Test {imageName!s}")


def PushImage(
    image: Union[str, List[str]],
    registry: Optional[str] = defaultRegistry,
    collection: Optional[str] = defaultCollection,
    architecture: Optional[str] = defaultArchitecture,
    dry: Optional[bool] = False,
    mirror: Optional[Union[str, List[str]]] = None,
) -> None:
    def dpush(imgName):
        _exec(args=["docker", "push", imgName], dry=dry, collapse=f"Push {imgName}")

    mirrors = [] if mirror is None else [mirror] if isinstance(mirror, str) else mirror

    for rimg in [image] if isinstance(image, str) else image:
        # Note that '#' might be used in the image names as a package location, to be used in TestImage.
        # This usage of '#' is different from the one in the mirror names below.
        # There, it denotes keywords for replacement.
        img = rimg.split('#')[0]
        imageName = f"{registry}/{architecture}/{collection}/{img}"
        dpush(imageName)
        for mirror in mirrors:
            mimg = (
                img.replace("/", ":", 1).replace("/", "--")
                if mirror.startswith("docker.io")
                else img
            )
            mirrorName = f"{mirror.replace('#A', architecture).replace('#C', collection)}/{mimg}"
            _exec(
                args=["docker", "tag", imageName, mirrorName],
                dry=dry,
                collapse=f"Tag {imageName} {mirrorName}",
            )
            dpush(mirrorName)
