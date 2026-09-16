# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
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

from typing import List
from sys import executable, platform, stdout as sys_stdout, stderr as sys_stderr
from os import environ
from subprocess import check_call, STDOUT
from shutil import which


isGHA: bool = "GITHUB_ACTIONS" in environ


def _exec(args: List[str], dry: bool = False, collapse: str | None = None) -> None:
    isGroup = isGHA and collapse is not None

    if isGroup:
        print(f"::group::{collapse}")
        GHASummary([f"- {collapse}"])
        sys_stdout.flush()
        sys_stderr.flush()

    print("·", " ".join(args))
    sys_stdout.flush()
    sys_stderr.flush()

    if not dry:
        check_call(args, stderr=STDOUT)

    if isGroup:
        print("::endgroup::")
        sys_stdout.flush()
        sys_stderr.flush()


def _sh(args: List[str], dry: bool = False) -> None:
    if platform != "win32":
        _exec(args, dry=dry)
        return
    shell = which("bash")
    if shell is None:
        raise FileNotFoundError("bash not found in PATH (required on win32)")
    _exec([shell, *args], dry=dry)


def _py(args: List[str], dry: bool = False) -> None:
    _exec([executable] + args, dry=dry)


def GHASummary(content: List[str]) -> None:
    if not isGHA:
        print("· Printing GHA summary skipped")
        return
    with open(environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as ghs:
        ghs.write('\n'.join(content)+'\n')

def GHAOutput(content: List[str]) -> None:
    if not isGHA:
        print("· Printing GHA output skipped")
        return
    with open(environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as gho:
        gho.write('\n'.join(content)+'\n')
