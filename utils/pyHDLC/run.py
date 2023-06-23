# Authors:
#   Unai Martinez-Corral
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

from typing import List, Optional
from pathlib import Path
from sys import executable, platform, stdout as sys_stdout, stderr as sys_stderr
from os import environ
from subprocess import check_call, STDOUT
from shutil import which


isGHA: bool = "GITHUB_ACTIONS" in environ

isWin: bool = platform == "win32"

shell: List[str] = [which("bash")] if platform == "win32" else []


def _exec(args: List[str], dry: Optional[bool] = False, collapse: Optional[str] = None):
    isGroup = isGHA and collapse is not None

    if isGroup:
        print(f"\n::group::{collapse}")
        sys_stdout.flush()
        sys_stderr.flush()

    print("·", " ".join(args))
    sys_stdout.flush()
    sys_stderr.flush()

    if not dry:
        check_call(args, stderr=STDOUT)

    if isGroup:
        print("\n::endgroup::")
        sys_stdout.flush()
        sys_stderr.flush()


def _sh(args: List[str], dry: Optional[bool] = False):
    _exec(shell + args, dry=dry)


def _py(args: List[str], dry: Optional[bool] = False):
    _exec([executable] + args, dry=dry)


def GHASummary(content: List[str]):
    if not isGHA:
        print("· Printing GHA summary skipped")
        return
    with Path(environ["GITHUB_STEP_SUMMARY"]).open("a") as wfptr:
        for line in content:
            wfptr.write(f"{line}\n")
