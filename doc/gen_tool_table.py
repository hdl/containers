#!/usr/bin/env python

from pathlib import Path

tools = {
    'ghdl': {
        'url': 'https://github.com/ghdl/ghdl',
        'pkg': ['ghdl'],
        'use': ['ghdl'],
        'in': [
            'impl',
            'formal'
        ],
        'otherin': ['ghdl:yosys']
    },
    'ghdl-yosys-plugin': {
        'url': 'https://github.com/ghdl/ghdl-yosys-plugin',
        'pkg': ['ghdl-yosys-plugin'],
        'use': ['ghdl:yosys'],
        'in': [
            'impl',
            'formal'
        ]
    },
    'graphviz': {
        'url': 'https://graphviz.org/',
        'in': [
            'impl',
            'formal'
        ],
        'otherin': [
            'yosys',
            'ghdl:yosys',
        ]
    },
    'gtkwave': {
        'url': 'https://github.com/gtkwave/gtkwave',
        'pkg': ['gtkwave'],
        'in': []
    },
    'icestorm': {
        'url': 'https://github.com/YosysHQ/icestorm',
        'pkg': ['icestorm'],
        'use': ['icestorm'],
        'in': [
            'impl',
            'prog'
        ],
        'otherin': [
            'nextpnr',
            'nextpnr:ice40',
            'nextpnr:ecp5',
        ]
    },
    'nextpnr': {
        'url': 'https://github.com/YosysHQ/nextpnr',
        'use': [
            'nextpnr',
            'nextpnr:ice40',
            'nextpnr:ecp5'
        ],
        'in': ['impl']
    },
    'openocd': {
        'url': 'http://openocd.org/',
        'in': ['prog']
    },
    'prjtrellis': {
        'url': 'https://github.com/YosysHQ/prjtrellis',
        'pkg': ['prjtrellis'],
        'use': ['prjtrellis'],
        'in': [
            'impl'
        ],
        'otherin': [
            'nextpnr',
            'nextpnr:ice40',
            'nextpnr:ecp5',
        ]
    },
    'symbiyosys': {
        'url': 'https://github.com/YosysHQ/SymbiYosys',
        'pkg': ['symbiyosys'],
        'in': ['formal']
    },
    'yosys': {
        'url': 'https://github.com/YosysHQ/yosys',
        'pkg': ['yosys'],
        'use': ['yosys'],
        'in': [
            'impl',
            'formal'
        ],
        'otherin': ['ghdl:yosys']
    },
    'z3': {
        'url': 'https://github.com/Z3Prover/z3',
        'pkg': ['z3'],
        'in': ['formal']
    },
}


def shield_dockerhub(repo, tag):
    latest = f':{tag}' if tag != 'latest' else ''
    return f'https://hub.docker.com/r/hdlc/{repo}/tags[image:https://img.shields.io/docker/image-size/hdlc/{repo}/{tag}?longCache=true&style=flat-square&label={repo}{latest}&logo=Docker&logoColor=fff[title=\'hdlc/{repo}:{tag} Docker image size\']]'


def shield_dockerhub_split_tag(item):
    items = item.split(':')
    return shield_dockerhub(items[0], 'latest' if len(items)==1 else items[1])


with (Path(__file__).resolve().parent/'tools.adoc').open('w') as fptr:

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

        #fptr.write('|%s\n' % ('Y' if 'synth' in var['in'] else '-'))
        fptr.write('^.|%s\n' % ('I' if 'impl' in var['in'] else '-'))
        fptr.write('^.|%s\n' % ('F' if 'formal' in var['in'] else '-'))
        fptr.write('^.|%s\n' % ('P' if 'prog' in var['in'] else '-'))

        otherin = ', '.join('`%s`' % item for item in (
            var['otherin'] if 'otherin' in var else []
        ))
        fptr.write('|%s\n' % ('-' if len(otherin) == 0 else otherin))

    fptr.write('\n|===')
