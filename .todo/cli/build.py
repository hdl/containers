import sys
from os import environ
from pathlib import Path
from subprocess import check_call

from utils import gstart, gend


def build_image(repo, tag, dfile, args=None, dry_run=False):
    gstart("[DOCKER build] %s : %s" % (repo, tag))

    ctx = args["context"] if args and "context" in args else None
    tgt = args["target"] if args and "target" in args else None
    bargs = args["args"] if args and "args" in args else None

    cmd = ["docker", "build", "-t", "ghdl/%s:%s" % (repo, tag)]
    if tgt:
        cmd += ["--target=%s" % tgt]
    if bargs:
        for arg in bargs:
            cmd += ["--build-arg", arg]


    def do_build(cmd, stdin=None):
        pcmd = ' '.join(cmd)
        if stdin:
            pcmd += " < %s" % stdin.name
        print("CMD: %s" % pcmd)
        if dry_run or environ.get("SKIP_BUILD"):
            print("SKIP")
            return
        sys.stdout.flush()
        check_call(cmd, stdin=stdin)


    pfile = Path(__file__).parent.parent/"dockerfiles"/dfile

    if ctx:
        cmd += ["-f", str(pfile), str(ctx)]
        do_build(cmd)
        return

    with pfile.open('r') as fptr:
        cmd += ["-"]
        do_build(cmd, fptr)

    gend()
