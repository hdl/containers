#!/usr/bin/env python3

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

from typing import List
from pathlib import Path
from os import listdir

from pyAttributes.ArgParseAttributes import (
    ArgParseMixin,
    ArgumentAttribute,
    Attribute,
    CommandAttribute,
    CommonSwitchArgumentAttribute,
    DefaultAttribute,
    SwitchArgumentAttribute,
)

from pyHDLC import (
    DefaultOpts,
    PullImage,
    BuildImage,
    TestImage,
    PushImage,
)


class WithRegistryAttributes(Attribute):
    def __call__(self, func):
        for _item in [
            ArgumentAttribute(
                dest="Image",
                nargs="+",
                type=str,
                help="image name(s), without registry prefix.",
            ),
            ArgumentAttribute(
                "-r",
                "--registry",
                dest="Registry",
                type=str,
                help="container image registry prefix.",
                default="gcr.io/hdl-containers",
            ),
            ArgumentAttribute(
                "-c",
                "--collection",
                dest="Collection",
                type=str,
                help="name of the collection/subset of images.",
                default="debian/bullseye",
            ),
            ArgumentAttribute(
                "-a",
                "--arch",
                dest="Architecture",
                type=str,
                help="name of the architecture.",
                default="amd64",
            ),
            # ... add more if needed
        ]:
            self._AppendAttribute(
                func,
                _item,
            )
        return func


class CLI(ArgParseMixin):
    HeadLine = "hdl/containers (HDLC) command-line tool"

    def __init__(self):
        import argparse
        import textwrap

        # Call constructor of the main interitance tree
        super().__init__()
        # Call constructor of the ArgParseMixin
        ArgParseMixin.__init__(
            self,
            description=textwrap.dedent(
                """
                Helper tool for building one or multiple images, for easily browsing publicly
                available tags, and for generating graphs showing the dependencies between them.
                """
            ),
            epilog=textwrap.fill("Happy hacking!"),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
        )

    def PrintHeadline(self):
        print("{line}".format(line="=" * 80))
        print("{headline: ^80s}".format(headline=self.HeadLine))
        print("{line}".format(line="=" * 80))

    @CommonSwitchArgumentAttribute(
        "-n",
        "--noexec",
        dest="noexec",
        help="print commands but do not execute them.",
        default=False,
    )
    def Run(self):
        ArgParseMixin.Run(self)

    @DefaultAttribute()
    def HandleDefault(self, args):
        self.PrintHeadline()
        self.MainParser.print_help()

    @CommandAttribute("help", help="Display help page(s) for the given command name.")
    @ArgumentAttribute(
        dest="Command",
        type=str,
        nargs="?",
        help="Print help page(s) for a command.",
    )
    def HandleHelp(self, args):
        if args.Command == "help":
            print("This is a recursion ...")
            return
        if args.Command is None:
            self.PrintHeadline()
            self.MainParser.print_help()
        else:
            try:
                self.PrintHeadline()
                self.SubParsers[args.Command].print_help()
            except KeyError:
                print("command {0} is unknown.".format(args.Command))

    @CommandAttribute("pull", help="Pull images by name.")
    @WithRegistryAttributes()
    def HandlePull(self, args):
        PullImage(
            image=args.Image,
            registry=args.Registry,
            collection=args.Collection,
            architecture=args.Architecture,
            dry=args.noexec,
        )

    @CommandAttribute("build", help="Build images by name.")
    @WithRegistryAttributes()
    @ArgumentAttribute(
        "-f",
        "--dockerfile",
        dest="Dockerfile",
        type=str,
        help="dockerfile to be built, from the collection.",
    )
    @ArgumentAttribute(
        "-t",
        "--target",
        dest="Target",
        type=str,
        help="target stage in the dockerfile.",
    )
    @ArgumentAttribute(
        "-i",
        "--argimg",
        dest="ArgImg",
        type=str,
        help="base image passed as an ARG to the dockerfile.",
    )
    @SwitchArgumentAttribute(
        "-p",
        "--pkg",
        dest="Pkg",
        help="preprend 'pkg/' to Image and set Target to 'pkg' (if unset).",
        default=False,
    )
    @SwitchArgumentAttribute(
        "-d",
        "--default",
        dest="Default",
        help="set default Dockerfile, Target and ArgImg options, given the image name(s).",
        default=False,
    )
    def HandleBuild(self, args):
        BuildImage(
            image=args.Image,
            registry=args.Registry,
            collection=args.Collection,
            architecture=args.Architecture,
            dockerfile=args.Dockerfile,
            target=args.Target,
            argimg=args.ArgImg,
            pkg=args.Pkg,
            dry=args.noexec,
            default=args.Default,
        )

    @CommandAttribute("test", help="Test images by name.")
    @WithRegistryAttributes()
    def HandleTest(self, args):
        TestImage(
            image=args.Image,
            registry=args.Registry,
            collection=args.Collection,
            architecture=args.Architecture,
            dry=args.noexec,
        )

    @CommandAttribute("push", help="Push images by name.")
    @WithRegistryAttributes()
    @ArgumentAttribute(
        "-m",
        "--mirror",
        nargs="*",
        dest="Mirror",
        type=str,
        help="registry to mirror the image(s) to.",
    )
    def HandlePush(self, args):
        PushImage(
            image=args.Image,
            registry=args.Registry,
            collection=args.Collection,
            architecture=args.Architecture,
            dry=args.noexec,
            mirror=args.Mirror,
        )


if __name__ == "__main__":
    CLI().Run()
