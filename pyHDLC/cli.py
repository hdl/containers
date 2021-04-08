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

from build import Build


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
        "-n", "--noexec", dest="noexec", help="Print commands but do not execute them.", default=False
    )
    def Run(self):
        ArgParseMixin.Run(self)

    @DefaultAttribute()
    def HandleDefault(self, args):
        self.PrintHeadline()
        self.MainParser.print_help()

    @CommandAttribute("help", help="Display help page(s) for the given command name.")
    @ArgumentAttribute(
        metavar="<Command>",
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
                print("Command {0} is unknown.".format(args.Command))

    @CommandAttribute("build", help="Build a single image by name.")
    @ArgumentAttribute(
        dest="Image",
        type=str,
        help="Image name to be built (without registry prefix).",
    )
    @ArgumentAttribute(
        "-r",
        "--registry",
        dest="Registry",
        type=str,
        help="Container image registry to tag the image for.",
        default="ghcr.io/hdl",
    )
    @ArgumentAttribute(
        "-c",
        "--collection",
        dest="Collection",
        type=str,
        help="Collection to pick the dockerfile from.",
        default="debian-buster",
    )
    @ArgumentAttribute(
        "-d",
        "--dockerfile",
        dest="Dockerfile",
        type=str,
        help="Dockerfile to be built, from the collection.",
    )
    @ArgumentAttribute(
        "-t",
        "--target",
        dest="Target",
        type=str,
        help="Target stage in the dockerfile.",
    )
    @ArgumentAttribute(
        "-a",
        "--argimg",
        dest="ArgImg",
        type=str,
        help="Base image passed as an ARG to the dockerfile.",
    )
    def HandleBuild(self, args):
        Build(
            image=args.Image,
            registry=args.Registry,
            collection=args.Collection,
            dockerfile=args.Dockerfile,
            target=args.Target,
            argimg=args.ArgImg,
            dry=args.noexec,
        )


if __name__ == "__main__":
    CLI().Run()
