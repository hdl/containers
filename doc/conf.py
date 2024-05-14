# -*- coding: utf-8 -*-

# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
#     <unai.martinezcorral@ehu.eus>
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

from sys import path as sys_path
from os.path import abspath
from pathlib import Path
from json import loads as json_loads
from yaml import load as yaml_load, Loader as yaml_Loader
from tabulate import tabulate

ROOT = Path(__file__).resolve().parent

sys_path.insert(0, abspath("."))
sys_path.insert(0, abspath("../utils/"))

# -- Generate ToolsTable.inc -------------------------------------------------------------------------------------------

imageShields = [
    "sim",
    "sim/osvb",
    "sim/scipy-slim",
    "sim/scipy",
    "sim/octave-slim",
    "sim/octave",
    "sim/octave/gnuplot",
    "impl",
    "impl/ice40",
    "impl/ecp5",
    "impl/nexus",
    "impl/generic",
    "impl/pnr",
    "impl/icestorm",
    "impl/prjtrellis",
    "impl/prjoxide",
    "formal",
    "formal/min",
    "formal/all",
    "prog",
    "conda",
    "conda/f4pga/xc7/toolchain",
    "conda/f4pga/xc7/a50t",
    "conda/f4pga/xc7/a100t",
    "conda/f4pga/xc7/a200t",
    "conda/f4pga/xc7/z010",
    "conda/f4pga/xc7/z020",
    "conda/f4pga/xc7",
    "conda/f4pga/eos-s3",
]

tools = ROOT / "tools.yml"

if not tools.exists():
    raise (Exception("Tools YAML file %s not found!" % str(tools)))

with tools.open("r", encoding="utf-8") as stream:
    tools = yaml_load(stream, Loader=yaml_Loader)

with (ROOT / "ToolsTable.inc").open("w", encoding="utf-8") as wfptr:

    def table_row(tool, var):
        pkgImages = [f"pkg/{item}" for item in var["pkg"]] if "pkg" in var else []
        useImages = var["use"] if "use" in var else []
        imageShields.extend(pkgImages)
        imageShields.extend(useImages)
        pkg = [f"  * |SHIELD:Image:{item}|\n" for item in pkgImages]
        use = [f"  * |SHIELD:Image:{item}|\n" for item in useImages]
        _in = var["in"] if "in" in var else []
        otherin = ", ".join(f"`{item}`" for item in (var["otherin"] if "otherin" in var else []))
        url = f"`{tool} <{var['url']}>`__" if 'url' in var else f' :awesome:`{tool}`'
        return (
            [
                f"{url}{' !' if ('src' in var and not var['src']) else ''}",
                "%s" % ("∅" if len(pkg) == 0 else pkg[0]),
                "%s" % ("∅" if len(use) == 0 else use[0]),
                #'%s\n' % ('Y' if any(_initem.startswith('synth') for _initem in _in) else '-')
                "%s" % ("S" if any(_initem.startswith("sim") for _initem in _in) else "🗆"),
                "%s" % ("I" if any(_initem.startswith("impl") for _initem in _in) else "🗆"),
                "%s" % ("F" if any(_initem.startswith("formal") for _initem in _in) else "🗆"),
                "%s" % ("P" if any(_initem.startswith("prog") for _initem in _in) else "🗆"),
                f"{'∅' if len(otherin) == 0 else otherin}\n",
            ],
            [] if len(pkg) < 2 else pkg[1:],
            [] if len(use) < 2 else use[1:],
        )

    table = []
    for tool, var in tools.items():
        (row, pkg, use) = table_row(tool, var)
        table.append(row)
        len_pkg = len(pkg)
        len_use = len(use)
        if len_pkg > 0 or len_use > 0:
            for num in range(max(len_pkg, len_use)):
                table.append(
                    [
                        " ",
                        pkg[num] if len_pkg > num else " ",
                        use[num] if len_use > num else " ",
                        " ",
                        " ",
                        " ",
                        " ",
                        " ",
                    ]
                )
    wfptr.write(
        tabulate(
            table,
            #'Image', 'Included in',
            headers=["Tool", "Package", "Ready-to-use", "S", "I", "F", "P", "Others"],
            tablefmt="rst",
        ).replace("..", "  ")
    )

# -- Generate shields.tools.inc and shields.build.inc ------------------------------------------------------------------


def OCIImageShield(image):
    arr = image.replace("/", ":", 1).replace("/", "--").split(":")
    attrs = f"longCache=true&style=flat-square&label={image}&logo=Docker&logoColor=fff"
    name = f"{arr[0]}/{arr[1] if len(arr) > 1 else 'latest'}"
    return f"""
.. |SHIELD:Image:{image}| image:: https://img.shields.io/docker/image-size/hdlc/{name}?{attrs}
   :alt: '{image} container image size'
   :height: 22
   :target: https://gcr.io/hdl-containers/{'debian/bullseye/' if arr[0] in ['pkg', 'build'] else ''}{image}
   :class: shield
"""


with (ROOT / "shields/shields.tools.gen.inc").open("w", encoding="utf-8") as wfptr:
    for image in imageShields:
        wfptr.write(OCIImageShield(image))

with (ROOT / "shields/shields.build.gen.inc").open("w", encoding="utf-8") as wfptr:
    for image in [
        "build/base",
        "build/build",
        "build/dev",
    ]:
        wfptr.write(OCIImageShield(image))

# -- Generate CIStatus.inc ---------------------------------------------------------------------------------------------

CIWorkflows = [
    [
        "doc",
        "base",
        "ghdl",
        "gtkwave",
        "iverilog",
        "nvc",
        "verible",
        "verilator",
        "xschem",
        "xyce",
    ],
    [
        "apicula",
        "arachne-pnr",
        "ghdl-yosys-plugin",
        "icestorm",
        "nextpnr",
        "openfpgaloader",
        "prjoxide",
        "prjtrellis",
        "f4pga",
        "vtr",
        "yosys",
    ],
    [
        "boolector",
        "cvc",
        "pono",
        "superprove",
        "sby",
        "yices2",
        "z3",
    ],
    [
        "irsim",
        "klayout",
        "magic",
        "netgen",
        "openroad",
    ],
    [
        "formal",
        "sim",
        "impl",
        "prog",
    ],
]

with (ROOT / "CIStatus.inc").open("w") as wfptr:
    # Generate shields before using them in the table
    for sublist in CIWorkflows:
        for workflow in sublist:
            wfptr.write(
                f"""\
.. |SHIELD:Workflow:{workflow}| image:: https://img.shields.io/github/actions/workflow/status/hdl/containers/{workflow}.yml?branch=main&longCache=true&style=flat-square&label={workflow}&logo=GitHub%20Actions&logoColor=fff
   :alt: '{workflow} workflow Status'
   :height: 22
   :target: https://github.com/hdl/containers/actions/workflows/{workflow}.yml
   :class: shield\n
"""
            )
    # Get the length of each column
    lengths = [len(sublist) for sublist in CIWorkflows]
    # Generate the table
    wfptr.write(
        tabulate(
            [
                [
                    (f"|SHIELD:Workflow:{sublist[num]}|" if lengths[index] > num else " ")
                    for index, sublist in enumerate(CIWorkflows)
                ] for num in range(max(lengths))
            ],
            headers=["Base, Simulation and Linting", "Synthesis, PnR and Prog", "Formal", "ASIC", "All-in-one"],
            tablefmt="rst",
        )
    )

# -- General configuration ---------------------------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.graphviz",
    "sphinxcontrib.autoprogram",
]

autodoc_default_options = {
    "members": True,
}

templates_path = ["_templates"]

source_suffix = {
    ".rst": "restructuredtext",
}

master_doc = "index"
project = "HDL Containers: Building and deploying container images for open source Electronic Design Automation"
copyright = "2019-2023, Unai Martinez-Corral and contributors"
author = "Unai Martinez-Corral and contributors"

version = "latest"
release = version  # The full version, including alpha/beta/rc tags.

language = 'en'

exclude_patterns = [
    "_build",
    "_theme",
    "logo",
    "graph",
    ".dockerfile",
    ".yml",
]

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
        "theme_overrides.css",
    ]
else:
    html_theme = "alabaster"

html_static_path = ["_static"]

html_logo = str(ROOT / "logo/icon.svg")
html_favicon = str(ROOT / "logo/icon.png")

htmlhelp_basename = "HDLCDoc"

# -- Options for LaTeX output ------------------------------------------------------------------------------------------

latex_elements = {
    "papersize": "a4paper",
}

latex_documents = [
    (
        master_doc,
        "HDLCDoc.tex",
        "Building and deploying container images for open source Electronic Design Automation (Documentation)",
        author,
        "manual",
    ),
]

# -- Options for manual page output ------------------------------------------------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        master_doc,
        "HDLC",
        "Building and deploying container images for open source Electronic Design Automation (Documentation)",
        [author],
        1,
    )
]

# -- Options for Texinfo output ----------------------------------------------------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "HDLC",
        "Building and deploying container images for open source Electronic Design Automation (Documentation)",
        author,
        "HDL Containers",
        "HDL verification.",
        "Miscellaneous",
    ),
]

# -- Sphinx.Ext.InterSphinx --------------------------------------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "constraints": ("https://hdl.github.io/constraints", None),
    "edaa": ("https://edaa-org.github.io", None),
    "clitool": ("https://edaa-org.github.io/pyEDAA.CLITool", None),
    "edalize": ("https://edalize.rtfd.io/en/latest", None),
    "pyfpga": ("https://pyfpga.github.io/pyfpga", None),
    "qus": ("https://dbhi.github.io/qus", None),
}

# -- Sphinx.Ext.ExtLinks -----------------------------------------------------------------------------------------------

extlinks = {
    "wikipedia": ("https://en.wikipedia.org/wiki/%s", None),
    "awesome": ("https://hdl.github.io/awesome/items/%s", "%s"),
    "gh": ("https://github.com/%s", "gh:%s"),
    "ghsharp": ("https://github.com/hdl/containers/issues/%s", "#%s"),
    "ghissue": ("https://github.com/hdl/containers/issues/%s", "issue #%s"),
    "ghpull": ("https://github.com/hdl/containers/pull/%s", "pull request #%s"),
    "ghsrc": ("https://github.com/hdl/containers/blob/main/%s", "%s"),
}
