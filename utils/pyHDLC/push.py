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

from typing import List, Optional, Union
from run import _exec


def PushImage(
    image: Union[str, List[str]],
    registry: Optional[str] = "gcr.io/hdl-containers",
    collection: Optional[str] = "debian/bullseye",
    architecture: Optional[str] = "amd64",
    dry: Optional[bool] = False,
    mirror: Optional[Union[str, List[str]]] = None,
) -> None:
    def _dpush(imgName):
        _exec(args=["docker", "push", imgName], dry=dry, collapse=f"Push {imgName}")

    def _push(img):
        _imageName = "{0}/{1}/{2}/{3}".format(registry, architecture, collection, img)
        _dpush(_imageName)
        if mirror is not None:
            for _mirror in mirror:
                _img = (
                    img.replace("/", ":", 1).replace("/", "--")
                    if _mirror.startswith("docker.io")
                    else img
                )
                _mirrorName = "{0}/{1}".format(
                    _mirror.replace("#A", architecture).replace("#C", collection), _img
                )
                _exec(
                    args=["docker", "tag", _imageName, _mirrorName],
                    dry=dry,
                    collapse=f"Tag {_imageName} {_mirrorName}",
                )
                _dpush(_mirrorName)

    if isinstance(image, str):
        image = [image]

    if mirror is not None and isinstance(mirror, str):
        mirror = [mirror]

    for _image in image:
        _push(_image)
