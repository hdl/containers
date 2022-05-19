# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021-2022 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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
from string import Template
from re import search as re_search, IGNORECASE as re_IGNORECASE

from dataclasses import dataclass
from yamldataclassconfig.config import YamlDataClassConfig

from pyHDLC.run import _exec, GHASummary


@dataclass
class ConfigDefaultImageItem(YamlDataClassConfig):
    """
    Optionally overridable fields for image build argument defaults.
    """
    #: The dockerfile to pass to `docker build`.
    dockerfile: Optional[str] = None
    #: The target stage to pass to `docker build`.
    target: Optional[str] = None
    #: The base IMAGE to pass as a build-arg to `docker build`.
    argimg: Optional[str] = None

@dataclass
class ConfigDefaults(YamlDataClassConfig):
    """
    Default global parameters and images which need explicitly overriding build argument defaults.
    See :ref:`Development:configuration:defaults`.
    """
    #: Default registry prefix.
    registry: str = "gcr.io/hdl-containers"
    #: Default collection.
    collection: str = "debian/bullseye"
    #: Default architecture.
    architecture: str = "amd64"
    #: Allows override default image build arguments.
    images: Optional[Dict[str, ConfigDefaultImageItem]] = None

ConfigJobsSysDict = Dict[str, List[str]]
ConfigJobsDict = Dict[str, ConfigJobsSysDict]

@dataclass
class ConfigJobsCustomExcludeItem(YamlDataClassConfig):
    """
    An exclusion rule for a list of taks generated through a cross-product.
    """
    #: Collection(s) and architecture(s).
    sys: ConfigJobsSysDict
    #: Combination of argument values to exclude.
    params: Dict[str, str]

@dataclass
class ConfigJobsCustomItem(YamlDataClassConfig):
    """
    A custom list of jobs/tasks defined by combining lists of images and system, optionally applying exclusion rules.
    """
    #: Either a list or a list of lists of image names.
    #: Argument substitution is supported through ``${arg}``.
    images: List[Any]
    #: Collection(s) and architecture(s).
    sys: ConfigJobsSysDict
    #: Optionally, declare combinations of *sys* and *images* which should be excluded from the produced cross-products.
    exclude: Optional[List[ConfigJobsCustomExcludeItem]] = None #= {}

@dataclass
class ConfigJobs(YamlDataClassConfig):
    """
    List of jobs/tasks to be used in CI to dynamically spawn jobs.
    See :ref:`Development:configuration:jobs`.
    """
    #: Build two images for each collection and architecture, a regular image and a package image.
    default: ConfigJobsDict #= {}
    #: Build a package image for each collection and architecture.
    pkgonly: ConfigJobsDict #= {}
    #: Build a regular image for each collection and architecture.
    runonly: ConfigJobsDict #= {}
    #: Declare the lists of jobs/tasks as cross-products (``exclude`` is supported).
    custom: Dict[str, ConfigJobsCustomItem] #= {}

@dataclass
class Config(YamlDataClassConfig):
    """
    Configuration containing global defaults, image building argument overrides and job/task list declarations.
    See :ref:`Development:configuration`.
    """
    #: Version of the configuration file syntax.
    HDLC: Optional[int] = None
    #: Placeholder for anchors used to reduce verbosity. This field is resolved by the loader and ignored by the analyzer.
    anchors: Optional[Any] = None #= {}
    #: Default global parameters and images which need explicitly overriding build argument defaults.
    defaults: ConfigDefaults = ConfigDefaults()
    #: List of jobs/tasks to be used in CI to dynamically spawn jobs.
    jobs: Optional[ConfigJobs] = None #= ConfigJobs()


CONFIG = Config()
CPATH = Path(__file__).resolve().parent / 'config.yml'
if CPATH.exists():
    CONFIG.load(CPATH)
    print(f"Read configuration file {CPATH!s} (HDLC v{CONFIG.HDLC})")


def _generateJobList(
    name: str
) -> List[Dict[str, str]]:

    cjobs = CONFIG.jobs

    def _combine(
        systems: ConfigJobsDict,
        images: List[str]
    ) -> List[Dict[str, str]]:
        return [
            {
                "os": collection,
                "arch": architecture,
                "imgs": " ".join(imgs)
            }
            for imgs in images
            for collection, architectures in systems.items()
            for architecture in architectures
        ]

    if name in cjobs.default:
        print(f"[Jobs] '{name}' is Default")
        return _combine(cjobs.default[name], [[f"pkg/{name}", name]])

    if name in cjobs.pkgonly:
        print(f"[Jobs] '{name}' is PkgOnly")
        return _combine(cjobs.pkgonly[name], [[f"pkg/{name}"]])
        return

    if name in cjobs.runonly:
        print(f"[Jobs] '{name}' is RunOnly")
        return _combine(cjobs.runonly[name], [[name]])
        return

    if name in cjobs.custom:
        print(f"[Jobs] '{name}' is Custom")

        def _customItem(custom):

            paramSets = [probe for probe in custom.images if isinstance(probe, dict)]

            if len(paramSets) > 0:
                print(f"[Jobs] Images of '{name}' has Params")

                patterns = [probe for probe in custom.images if not isinstance(probe, dict)]

                if custom.exclude is None:
                    return _combine(
                        custom.sys,
                        [
                            [
                                Template(pattern).substitute(params)
                                for pattern in patterns
                            ]
                            # TODO Handle individual params being a list of strings, instead of a single string.
                            for params in paramSets
                        ]
                    )

                excludes = [
                    (collection, architectures, exclude.params)
                    for exclude in custom.exclude
                    for collection, architectures in exclude.sys.items()
                ]

                # TODO Merge this list generation into the for loops beloew.
                # I.e., filter during generation, instead of generating all the cases and then filtering.
                systems = [
                    (collection, architectures.copy(), params)
                    for collection, architectures in custom.sys.items()
                    for params in paramSets
                ]

                for item in systems:
                    for excl in excludes:
                        # TODO Handle individual params being a list of strings, instead of a single string.
                        if (item[0] == excl[0]) and (item[2] == excl[2]):
                            # TODO Handle excl[1]==None (that is, remove all archs for a collection)
                            for arch in excl[1]:
                                if arch in item[1]:
                                    item[1].remove(arch)

                return [
                    {
                        "os": item[0],
                        "arch": architecture,
                        "imgs": " ".join([
                            Template(pattern).substitute(item[2])
                            for pattern in patterns
                        ])
                    }
                    for item in systems if len(item[1]) != 0
                    for architecture in item[1]
                ]

            if isinstance(custom.images[0], str):
                print(f"[Jobs] Images of '{name}' is List of strings")
                return _combine(custom.sys, [custom.images])

            if isinstance(custom.images[0], list):
                print(f"[Jobs] Images of '{name}' is List of lists")
                print(custom.images)
                return _combine(custom.sys, custom.images)

            raise Exception("Not implemented yet!")

        return _customItem(cjobs.custom[name])

    raise Exception(f"Unknown job {name}")


def _jobSummary(
    jobs: List[Dict[str, str]]
) -> None:
    content = []
    for job in jobs:
        content.append(f"- {job['arch']} | {job['os']}")
        imgs = job['imgs']
        content.extend([f"  - {img}" for img in imgs.split(' ')] if ' ' in imgs else [f"  - {imgs}"])
    return content


def GenerateJobList(
    name: str,
    fmt: str = 'gha',
    dry: bool = False,
) -> None:
    """
    Generate list of jobs for a named task.

    :param name:
      Identifier to extract jobs from the YAML configuration file.

    :param fmt:
      Output format (by default, print GitHub Actions' set-output syntax).

    :param dry:
      Do not set the output, just print the list of jobs.
    """
    jobs = _generateJobList(name)

    summary = _jobSummary(jobs)
    print('\n'.join(summary))

    if dry:
        return
    if fmt.lower() in ["gha"]:
        print(f'::set-output name=matrix::{jobs!s}')
        GHASummary(summary)


def PullImage(
    image: Union[str, List[str]],
    registry: str = CONFIG.defaults.registry,
    collection: str = CONFIG.defaults.collection,
    architecture: str = CONFIG.defaults.architecture,
    dry: bool = False,
) -> None:
    """
    Pull container image(s) from registry.

    :param image:
      Bare image name(s), without registry, collection or architecture.
      The supported syntax for each image name is ``name[#location]``, where the optional ``location`` is ignored if
      provided (it's used in :func:`TestImage` only).

    :param registry:
      Optionally, set the prefix of the registry.

    :param collection:
      Optionally, set the collection to pull the image for.

    :param architecture:
      Optionally, set the architecture to pull the image for.

    :param dry:
      Do not pull the image, just print the command that would be executed.
    """
    for img in [image] if isinstance(image, str) else image:
        imageName = f"{registry}/{architecture}/{collection}/{img.split('#')[0]}"
        _exec(
            args=["docker", "pull", imageName], dry=dry, collapse=f"[Pull] Pull {imageName}"
        )


def _NormaliseBuildParams(
    image: str,
    dockerfile: Optional[str] = None,
    target: Optional[str] = None,
    argimg: Optional[str] = None,
    pkg: bool = False,
    default: bool = False,
) -> Tuple[str, bool, Optional[str], str, Optional[str], Optional[str]]:
    items = image.split('#')
    imageNameWithoutDirSuffix = items[0]
    withDir = None
    if len(items) > 1:
        withDir = items[1]

    if imageNameWithoutDirSuffix.startswith('pkg/'):
        isPkg = True
        imageNameWithoutPrefixOrSuffix = imageNameWithoutDirSuffix[4:]
    else:
        isPkg = pkg
        imageNameWithoutPrefixOrSuffix = imageNameWithoutDirSuffix
        if pkg:
            imageNameWithoutDirSuffix = f"pkg/{imageNameWithoutDirSuffix}"

    if default:
        def get_default_params():
            cfgi = CONFIG.defaults.images
            if cfgi is not None:
                key = imageNameWithoutPrefixOrSuffix if isPkg and (imageNameWithoutDirSuffix not in cfgi) else imageNameWithoutDirSuffix
                if key in cfgi:
                    cfg = cfgi[key]
                    return [cfg.dockerfile, cfg.target, cfg.argimg]
            return [None, None, None]
        [dockerfile, target, argimg] = get_default_params()

    return (
        imageNameWithoutDirSuffix,
        isPkg,
        withDir,
        imageNameWithoutPrefixOrSuffix if dockerfile is None else dockerfile,
        "pkg" if isPkg and (target is None) else target,
        argimg,
    )


def BuildImage(
    image: Union[str, List[str]],
    registry: str = CONFIG.defaults.registry,
    collection: str = CONFIG.defaults.collection,
    architecture: str = CONFIG.defaults.architecture,
    dockerfile: Optional[str] = None,
    target: Optional[str] = None,
    argimg: Optional[str] = None,
    pkg: bool = False,
    dry: bool = False,
    default: bool = False,
    test: bool = False,
) -> None:
    """
    Build and optionally test container image(s).

    :param image:
      Bare image name(s), without registry, collection or architecture.
      The supported syntax for each image name is ``name[#location]``, where the optional ``location`` is ignored during
      the build if provided (it's used for testing only, see :func:`TestImage`).

    :param registry:
      Optionally, set the prefix of the registry.

    :param collection:
      Optionally, set the collection to build the image from.

    :param architecture:
      Optionally, set the architecture to build the image for.

    :param dockerfile:
      Optionally, set the Dockerfile to build the image with.

    :param target:
      Optionally, set the target stage in the dockerfile.

    :param argimg:
      Optionally, set the build argument IMAGE.

    :param pkg:
      Optionally, specify explicitly whether the image to be built is a package image.

    :param dry:
      Do not build the image, just print the command(s) that would be executed.

    :param default:
      Instead of providing all of the parameters, get them from the YAML configuration file.

    :param test:
      Test the image(s) after building.
    """
    for rimg in [image] if isinstance(image, str) else image:

        [img, isPkg, withDir, dockerfile, target, argimg] = _NormaliseBuildParams(
            image=rimg,
            dockerfile=dockerfile,
            target=target,
            argimg=argimg,
            pkg=pkg,
            default=default
        )

        imageName = f"{registry}/{architecture}/{collection}/{img}"

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

        def _getCollectionAndDockerfilePaths(collection, dockerfile):
            collectionPath = Path(collection.replace("/", "-"))
            dockerfilePath = collectionPath / dockerfile

            if dockerfilePath.is_dir():
                contextPath = dockerfilePath
                dockerfilePath = contextPath / 'Dockerfile'
            else:
                contextPath = collectionPath
                dockerfilePath = contextPath / f"{dockerfile}.dockerfile"

            if not dockerfilePath.exists():
                raise Exception(f"Dockerfile <{dockerfilePath}> does not exist!")

            return (contextPath, dockerfilePath)

        (contextPath, dockerfilePath) = _getCollectionAndDockerfilePaths(collection, dockerfile)

        if len(dockerfilePath.suffix) != 0:
            cmd += ["-f", str(dockerfilePath)]

        cmd += [str(contextPath)]

        _exec(args=cmd, dry=dry, collapse=f"[Build] Build {imageName}")

        with dockerfilePath.open('r') as rfptr:
            for line in rfptr:
                if re_search('FROM scratch AS version', line, re_IGNORECASE):
                    _exec(
                        args=['docker', 'build', '--target', 'version', '-o', 'dist', str(contextPath)],
                        dry=dry,
                        collapse=f"[Build] Version {imageName}"
                    )
                    break

        if test:
            TestImage(
                f"{img}{(f'#{withDir}' if withDir is not None else '')}",
                registry,
                collection,
                architecture,
                dry,
            )


def TestImage(
    image: Union[str, List[str]],
    registry: str = CONFIG.defaults.registry,
    collection: str = CONFIG.defaults.collection,
    architecture: str = CONFIG.defaults.architecture,
    dry: bool = False,
) -> None:
    """
    Test container image(s).

    :param image:
      Bare image name(s), without registry, collection or architecture.
      The supported syntax for each image name is ``name[#<DirName>]``, where the optional ``<DirName>`` is used as the
      location in package images to copy the content from.

    :param registry:
      Optionally, set the prefix of the registry.

    :param collection:
      Optionally, set the collection to test the image from.

    :param architecture:
      Optionally, set the architecture to test the image for.

    :param dry:
      Do not test the image, just print the command(s) that would be executed.
    """
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
    registry: str = CONFIG.defaults.registry,
    collection: str = CONFIG.defaults.collection,
    architecture: str = CONFIG.defaults.architecture,
    dry: bool = False,
    mirror: Optional[Union[str, List[str]]] = None,
) -> None:
    """
    Push container image(s) to registry/registries.

    :param image:
      Bare image name(s), without registry, collection or architecture.
      The supported syntax for each image name is ``name[#location]``, where the optional ``location`` is ignored if
      provided (it's used in :func:`TestImage` only).

    :param registry:
      Optionally, set the prefix of the registry.

    :param collection:
      Optionally, set the collection to push the image from.

    :param architecture:
      Optionally, set the architecture to push the image for.

    :param dry:
      Do not push the image, just print the command(s) that would be executed.

    :param mirror:
      List of additional registry/registries to push to. Supported placeholders:

      * ``#A``: architecture
      * ``#C``: collection
    """
    def dpush(args: List[str]):
        _exec(args=["docker", "push"]+args, dry=dry, collapse=f"Push {' '.join(args)}")

    def dtag(imgName: str, tags: List[str]):
        for tag in tags:
            _exec(
                args=["docker", "tag", imgName, tag],
                dry=dry,
                collapse=f"Tag {tag}",
            )

    mirrors = [] if mirror is None else [mirror] if isinstance(mirror, str) else mirror

    for rimg in [image] if isinstance(image, str) else image:
        # Note that '#' might be used in the image names as a package location, to be used in TestImage.
        # This usage of '#' is different from the one in the mirror names below.
        # There, it denotes keywords for replacement.
        img = rimg.split('#')[0]
        imageName = f"{registry}/{architecture}/{collection}/{img}"
        dpush([imageName])

        print('\nChecking version file...')
        versionString = None
        versionFile = Path('dist') / f'hdlc.{rimg if rimg[0:4] != "pkg/" else rimg[4:]}.version'
        if versionFile.exists():
            with versionFile.open('r') as rfptr:
                versionString = rfptr.read().strip()
        print(f'{rimg}: {versionString}')

        for mirror in mirrors:
            isDocker = mirror.startswith("docker.io")
            mimg = img.replace("/", ":", 1).replace("/", "--") if isDocker else img
            mirrorName = f"{mirror.replace('#A', architecture).replace('#C', collection)}/{mimg}"
            if isDocker or (versionString is None):
                dtag(imageName, [mirrorName])
                dpush([mirrorName])
                continue
            dtag(imageName, [mirrorName, f'{mirrorName}:{versionString}'])
            dpush(['--all-tags', mirrorName])
