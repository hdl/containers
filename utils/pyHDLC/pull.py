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


def PullImage(
    image: Union[str, List[str]],
    registry: Optional[str] = "gcr.io/hdl-containers",
    collection: Optional[str] = "debian/bullseye",
    architecture: Optional[str] = "amd64",
    dry: Optional[bool] = False,
) -> None:
    def _pull(img):
        _imageName = "{0}/{1}/{2}/{3}".format(registry, architecture, collection, img)
        _exec(
            args=["docker", "pull", _imageName], dry=dry, collapse=f"Pull {_imageName}"
        )

    for _image in [image] if isinstance(image, str) else image:
        _pull(_image)
