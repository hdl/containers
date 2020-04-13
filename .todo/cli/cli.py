#!/usr/bin/env python3

from pathlib import Path
from os import listdir

from pyAttributes.ArgParseAttributes import (
    ArgParseMixin,
    ArgumentAttribute,
    Attribute,
    CommandAttribute,
    CommonSwitchArgumentAttribute,
    DefaultAttribute,
    SwitchArgumentAttribute
)

from hub import get_all_registry_info, print_repos, print_tags
from graph import parse_dockerfile, generate_graph
from tasks import build, task


class Tool():
    HeadLine = "ghdl/docker CLI tool"

    def __init__(self):
        pass

    def PrintHeadline(self):
      print("{line}".format(line="="*80))
      print("{headline: ^80s}".format(headline=self.HeadLine))
      print("{line}".format(line="="*80))

    @staticmethod
    def hub():
        repo_list = get_all_registry_info()
        print()
        print_repos(repo_list)
        print()
        print_tags(repo_list)

    @staticmethod
    def graph():
        dockerfiles = Path(__file__).parent / ".." / "dockerfiles"
        generate_graph({ dfile: parse_dockerfile(dockerfiles / dfile) for dfile in listdir(dockerfiles) })

    @staticmethod
    def task(name, args=None, dry_run=False):
        task(name, args, dry_run)

    @staticmethod
    def build(repo, tag='latest'):
        build(repo, tag)


class WithBuildAttributes(Attribute):
  def __call__(self, func):
    self._AppendAttribute(func, SwitchArgumentAttribute("--dry-run", dest="dry_run", help="Print build commands but do not execute them."))
    # ... add more if needed
    return func


class CLI(Tool, ArgParseMixin):
    def __init__(self):
        import argparse
        import textwrap
        # Call constructor of the main interitance tree
        super().__init__()
        # Call constructor of the ArgParseMixin
        ArgParseMixin.__init__(
          self,
          description=textwrap.dedent('Helper tool to build one or multiple images, to easily browse publicly available tags, and to generate graphs showing the dependencies between tags.'),
          epilog=textwrap.fill("Happy hacking!"),
          formatter_class=argparse.RawDescriptionHelpFormatter,
          add_help=False
        )

    @CommonSwitchArgumentAttribute("-q", "--quiet",   dest="quiet",   help="Reduce messages to a minimum.")
    @CommonSwitchArgumentAttribute("-v", "--verbose", dest="verbose", help="Print out detailed messages.")
    @CommonSwitchArgumentAttribute("-d", "--debug",   dest="debug",   help="Enable debug mode.")
    def Run(self):
        ArgParseMixin.Run(self)

    @DefaultAttribute()
    def HandleDefault(self, args):
        self.PrintHeadline()
        self.MainParser.print_help()

    @CommandAttribute("help", help="Display help page(s) for the given command name.")
    @ArgumentAttribute(metavar="<Command>", dest="Command", type=str, nargs="?", help="Print help page(s) for a command.")
    def HandleHelp(self, args):
        if (args.Command == "help"):
            print("This is a recursion ...")
            return
        if (args.Command is None):
            self.PrintHeadline()
            self.MainParser.print_help()
        else:
            try:
                self.PrintHeadline()
                self.SubParsers[args.Command].print_help()
            except KeyError:
                print("Command {0} is unknown.".format(args.Command))

    @CommandAttribute("hub", help="Show list of repos and tags at hub.docker.com/u/ghdl.")
    def HandleHub(self, _):
        self.hub()

    @CommandAttribute("build", help="Build a single image.")
    @WithBuildAttributes()
    @ArgumentAttribute(metavar='<Repo>', dest="Repo", type=str, help="Repo - hub repo name")
    @ArgumentAttribute(metavar='<Tag>', dest="Tag", type=str, help="Tag - target image tag")
    def HandleBuild(self, args):
        self.build(args.Repo, args.Tag, args.dry_run)

    @CommandAttribute("task", help="Run a task, i.e. build a group of images.")
    @WithBuildAttributes()
    @ArgumentAttribute(metavar='<Name>', dest="Name", type=str, help="Name - unique identifier")
    @ArgumentAttribute(metavar='<Args>', dest="Args", type=str, nargs='*', help="Args - optional arguments/filters")
    def HandleTask(self, args):
        self.task(args.Name, args.Args, args.dry_run)

    @CommandAttribute("graph", help='Generate a dot graph from the multi-stage dockerfiles (WIP).')
    def HandleGraph(self, _):
        self.graph()


if __name__ == "__main__":
    CLI().Run()
