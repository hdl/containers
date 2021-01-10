#!/usr/bin/env python

from sys import stdout
from pathlib import Path
from yaml import load, Loader, YAMLError


ROOT = Path(__file__).resolve().parent

_tools = ROOT / 'tools.yml'

if not _tools.exists():
    raise(Exception('Configuration file %s not found!' % str(_tools)))

with _tools.open('r') as stream:
    tools = load(stream, Loader=Loader)


def shield_dockerhub(repo, tag):
    latest = f':{tag}' if tag != 'latest' else ''
    return f'https://hub.docker.com/r/hdlc/{repo}/tags[image:https://img.shields.io/docker/image-size/hdlc/{repo}/{tag}?longCache=true&style=flat-square&label={repo}{latest}&logo=Docker&logoColor=fff[title=\'hdlc/{repo}:{tag} Docker image size\']]'


def shield_dockerhub_split_tag(item):
    items = item.split(':')
    return shield_dockerhub(items[0], 'latest' if len(items)==1 else items[1])


with (ROOT/'tools.adoc').open('w') as fptr:

    fptr.write('[cols="6, 6, 6, 1, 1, 1, 8", stripes=even]\n')

    fptr.write('''|===
.2+^.h|Tool
2+^.h|Image
4+^.h|Included in
^.h|Package
^.h|Ready-to-use
^.h| I
^.h| F
^.h| P
^.h| Others\n''')

    for tool, var in tools.items():
        fptr.write('\n')
        fptr.write('^.|%s[%s]\n' % (var['url'], tool))

        pkg = ' '.join(shield_dockerhub('pkg', item) for item in (
            var['pkg'] if 'pkg' in var else [])
        )
        fptr.write('^.|%s\n' % ('-' if len(pkg) == 0 else pkg))

        use = ' '.join(shield_dockerhub_split_tag(item) for item in (
            var['use'] if 'use' in var else []
        ))
        fptr.write('^.|%s\n' % ('-' if len(use) == 0 else use))

        _in = var['in'] if 'in' in var else []
        #fptr.write('|%s\n' % ('Y' if 'synth' in var['in'] else '-'))
        fptr.write('^.|%s\n' % ('I' if 'impl' in _in else '-'))
        fptr.write('^.|%s\n' % ('F' if 'formal' in _in else '-'))
        fptr.write('^.|%s\n' % ('P' if 'prog' in _in else '-'))

        otherin = ', '.join('`%s`' % item for item in (
            var['otherin'] if 'otherin' in var else []
        ))
        fptr.write('|%s\n' % ('-' if len(otherin) == 0 else otherin))

    fptr.write('\n|===')
