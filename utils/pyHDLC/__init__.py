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

from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

from dataclasses import dataclass
from yamldataclassconfig.config import YamlDataClassConfig

from pyHDLC.run import _exec


@dataclass
class ConfigDefaultImageItem(YamlDataClassConfig):
    dockerfile: Optional[str] = None
    target: Optional[str] = None
    argimg: Optional[str] = None

@dataclass
class ConfigDefaults(YamlDataClassConfig):
    registry: Optional[str] = "gcr.io/hdl-containers"
    collection: Optional[str] = "debian/bullseye"
    architecture: Optional[str] = "amd64"
    images: Optional[Dict[str, ConfigDefaultImageItem]] = None

@dataclass
class Config(YamlDataClassConfig):
    HDLC: int = None
    anchors: Optional[Any] = None
    defaults: ConfigDefaults = ConfigDefaults()


CONFIG = Config()
cpath = Path(__file__).resolve().parent / 'config.yml'
if cpath.exists():
    CONFIG.load(cpath)
    print(f"Read configuration file {cpath!s} (HDLC v{CONFIG.HDLC})")


def PullImage(
    image: Union[str, List[str]],
    registry: Optional[str] = CONFIG.defaults.registry,
    collection: Optional[str] = CONFIG.defaults.collection,
    architecture: Optional[str] = CONFIG.defaults.architecture,
    dry: Optional[bool] = False,
) -> None:
    for img in [image] if isinstance(image, str) else image:
        imageName = f"{registry}/{architecture}/{collection}/{img.split('#')[0]}"
        _exec(
            args=["docker", "pull", imageName], dry=dry, collapse=f"[Pull] Pull {imageName}"
        )


def BuildImage(
    image: Union[str, List[str]],
    registry: Optional[str] = CONFIG.defaults.registry,
    collection: Optional[str] = CONFIG.defaults.collection,
    architecture: Optional[str] = CONFIG.defaults.architecture,
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
            if pkg:
                pimg = f"pkg/{pimg}"

        if default:
            def get_default_params():
                cfgi = CONFIG.defaults.images
                if cfgi is not None:
                    key = img if isPkg and (pimg not in cfgi) else pimg
                    if key in cfgi:
                        cfg = cfgi[key]
                        return [cfg.dockerfile, cfg.target, cfg.argimg]
                return [None, None, None]
            [dockerfile, target, argimg] = get_default_params()

        if dockerfile is None:
            dockerfile = img

        if isPkg and (target is None):
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

        if target not in [None, '']:
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
    registry: Optional[str] = CONFIG.defaults.registry,
    collection: Optional[str] = CONFIG.defaults.collection,
    architecture: Optional[str] = CONFIG.defaults.architecture,
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
    registry: Optional[str] = CONFIG.defaults.registry,
    collection: Optional[str] = CONFIG.defaults.collection,
    architecture: Optional[str] = CONFIG.defaults.architecture,
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
