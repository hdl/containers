#!/usr/bin/env python3

# Authors:
#   Patrick Lehmann
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

from pathlib import Path
from typing import List

from setuptools import (
    setup as setuptools_setup,
    find_namespace_packages as setuptools_find_namespace_packages
)


packagePath = Path(__file__).resolve().parent / 'pyHDLC'
requirementsFile = packagePath / "requirements.txt"


# Read requirements file and add them to package dependency list
def get_requirements(file: Path) -> List[str]:
    requirements = []
    with file.open("r") as fh:
        for line in fh.read().splitlines():
            if line.startswith("#") or line == "":
                continue
            elif line.startswith("-r"):
                # Remove the first word/argument (-r)
                filename = " ".join(line.split(" ")[1:])
                requirements += get_requirements(file.parent / filename)
            elif line.startswith("https"):
                # Convert 'URL#NAME' to 'NAME @ URL'
                splitItems = line.split("#")
                requirements.append("{} @ {}".format(splitItems[1], splitItems[0]))
            else:
                requirements.append(line)
    return requirements


setuptools_setup(
    name=packagePath.name,
    version="0.0.0",
    license="Apache-2.0",
    author="Unai Martinez-Corral and contributors",
    author_email="unai.martinezcorral@ehu.eus",
    description="Helper tool for HDL Containers.",
    url="https://github.com/hdl/containers",
    packages=setuptools_find_namespace_packages(exclude=[]),
    classifiers=[],
    python_requires='>=3.6',
    install_requires=list(set(get_requirements(requirementsFile))),
    entry_points={
        "console_scripts": [
            "pyHDLC = pyHDLC.cli:main",
        ]
    },
)
