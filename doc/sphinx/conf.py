# -*- coding: utf-8 -*-

# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021-2022 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
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

from sys import path as sys_path
from os.path import abspath
from pathlib import Path
from json import loads as json_loads
from yaml import load as yaml_load, Loader as yaml_Loader
from tabulate import tabulate

ROOT = Path(__file__).resolve().parent

sys_path.insert(0, abspath("."))

# -- Generate ToolsTable.inc -------------------------------------------------------------------------------------------

shields = [
    'sim',
    'sim/osvb',
    'sim/scipy-slim',
    'sim/scipy',
    'sim/octave-slim',
    'sim/octave',
    'impl',
    'impl/ice40',
    'impl/ecp5',
    'impl/generic',
    'impl/pnr',
    'impl/icestorm',
    'impl/prjtrellis',
    'formal',
    'formal/min',
    'formal/all',
    'prog',
    'conda',
    'conda/symbiflow/xc7/toolchain',
    'conda/symbiflow/xc7/a50t',
    'conda/symbiflow/xc7/a100t',
    'conda/symbiflow/xc7/a200t',
    'conda/symbiflow/xc7/z010',
    'conda/symbiflow/xc7/z020',
    'conda/symbiflow/xc7',
    'conda/symbiflow/eos-s3'
]

tools = ROOT / 'tools.yml'

if not tools.exists():
    raise(Exception('Tools YAML file %s not found!' % str(tools)))

with tools.open('r', encoding='utf-8') as stream:
    tools = yaml_load(stream, Loader=yaml_Loader)

with (ROOT/'ToolsTable.inc').open('w') as fptr:
    def table_row(tool, var):
        pkgImages = [f"pkg/{item}" for item in var['pkg']] if 'pkg' in var else []
        useImages = var['use'] if 'use' in var else []
        shields.extend(pkgImages)
        shields.extend(useImages)
        pkg = ' '.join([f"|SHIELD:Image:{item}|" for item in pkgImages])
        use = ' '.join([f"|SHIELD:Image:{item}|" for item in useImages])
        _in = var['in'] if 'in' in var else []
        otherin = ', '.join(f'`{item}`' for item in (var['otherin'] if 'otherin' in var else []))
        return [
            f"`{tool} <{var['url']}>`__{' !' if ('src' in var and not var['src']) else ''}",
            '%s' % ('-' if len(pkg) == 0 else pkg),
            '%s' % ('-' if len(use) == 0 else use),
            #fptr.write('%s\n' % ('Y' if any(_initem.startswith('synth') for _initem in _in) else '-'))
            '%s' % ('S' if any(_initem.startswith('sim') for _initem in _in) else '-'),
            '%s' % ('I' if any(_initem.startswith('impl') for _initem in _in) else '-'),
            '%s' % ('F' if any(_initem.startswith('formal') for _initem in _in) else '-'),
            '%s' % ('P' if any(_initem.startswith('prog') for _initem in _in) else '-'),
            f"{'-' if len(otherin) == 0 else otherin}\n",
        ]
    fptr.write(tabulate(
        [table_row(tool, var) for tool, var in tools.items()],
        #'Image', 'Included in',
        headers=['Tool', 'Package', 'Ready-to-use', 'S', 'I', 'F', 'P', 'Others'],
        tablefmt='rst'
    ))

# -- Generate shields.tools.inc ----------------------------------------------------------------------------------------

with (ROOT / 'shields.tools.inc').open('w', encoding='utf-8') as wfptr:
    for image in shields:
        arr = image.replace('/',':', 1).replace('/','--').split(':')
        wfptr.write(f"""
.. |SHIELD:Image:{image}| image:: https://img.shields.io/docker/image-size/hdlc/{arr[0]}/{arr[1] if len(arr) > 1 else 'latest'}?longCache=true&style=flat-square&label={image}&logo=Docker&logoColor=fff
   :alt: '{image} container image size'
   :height: 22
   :target: https://gcr.io/hdl-containers/{'debian/bullseye/' if arr[0] in ['pkg', 'build'] else ''}{image}
""")

# -- General configuration ---------------------------------------------------------------------------------------------

extensions = [
    # Standard Sphinx extensions
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]

source_suffix = {
    ".rst": "restructuredtext",
}

master_doc = "index"
project = u"HDL Containers: Building and deploying container images for open source Electronic Design Automation"
copyright = u"2019-2021, Unai Martinez-Corral and contributors"
author = u"Unai Martinez-Corral and contributors"

version = "latest"
release = version  # The full version, including alpha/beta/rc tags.

language = None

exclude_patterns = []

numfig = True

# -- Options for HTML output -------------------------------------------------------------------------------------------

html_context = {}
ctx = ROOT / "context.json"
if ctx.is_file():
    html_context.update(json_loads(ctx.open("r").read()))

if (ROOT / "_theme").is_dir():
    html_theme_path = ["."]
    html_theme = "_theme"
    html_theme_options = {
        "logo_only": True,
        "home_breadcrumbs": False,
        "vcs_pageview_mode": "blob",
    }
    html_css_files = [
        'theme_overrides.css',
    ]
else:
    html_theme = "alabaster"

html_static_path = ["_static"]

html_logo = str(ROOT / "../logo/icon.svg")
html_favicon = str(ROOT / "../logo/icon.png")

htmlhelp_basename = "HDLCDoc"

# -- Options for LaTeX output ------------------------------------------------------------------------------------------

latex_elements = {
    "papersize": "a4paper",
}

latex_documents = [
    (master_doc, "HDLCDoc.tex", u"Building and deploying container images for open source Electronic Design Automation (Documentation)", author, "manual"),
]

# -- Options for manual page output ------------------------------------------------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "HDLC", u"Building and deploying container images for open source Electronic Design Automation (Documentation)", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "HDLC",
        u"Building and deploying container images for open source Electronic Design Automation (Documentation)",
        author,
        "HDL Containers",
        "HDL verification.",
        "Miscellaneous",
    ),
]

# -- Sphinx.Ext.InterSphinx --------------------------------------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# -- Sphinx.Ext.ExtLinks -----------------------------------------------------------------------------------------------

extlinks = {
    "wikipedia": ("https://en.wikipedia.org/wiki/%s", None),
    "ghrepo": ("https://github.com/%s", ""),
    "ghsharp": ("https://github.com/hdl/containers/issues/%s", "#"),
    "ghissue": ("https://github.com/hdl/containers/issues/%s", "issue #"),
    "ghpull": ("https://github.com/hdl/containers/pull/%s", "pull request #"),
    "ghsrc": ("https://github.com/hdl/containers/blob/main/%s", ""),
}
