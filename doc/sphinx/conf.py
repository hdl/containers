# -*- coding: utf-8 -*-

from sys import path as sys_path
from os.path import abspath
from pathlib import Path
from json import loads

ROOT = Path(__file__).resolve().parent

sys_path.insert(0, abspath("."))

# -- General configuration ------------------------------------------------

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

# -- Options for HTML output ----------------------------------------------

html_context = {}
ctx = ROOT / "context.json"
if ctx.is_file():
    html_context.update(loads(ctx.open("r").read()))

if (ROOT / "_theme").is_dir():
    html_theme_path = ["."]
    html_theme = "_theme"
    html_theme_options = {
        "home_breadcrumbs": True,
        "vcs_pageview_mode": "blob",
    }
else:
    html_theme = "alabaster"

htmlhelp_basename = "HDLCDoc"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    "papersize": "a4paper",
}

latex_documents = [
    (master_doc, "HDLCDoc.tex", u"Building and deploying container images for open source Electronic Design Automation (Documentation)", author, "manual"),
]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "HDLC", u"Building and deploying container images for open source Electronic Design Automation (Documentation)", [author], 1)]

# -- Options for Texinfo output -------------------------------------------

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

# -- Sphinx.Ext.InterSphinx -----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# -- Sphinx.Ext.ExtLinks --------------------------------------------------

extlinks = {
    "wikipedia": ("https://en.wikipedia.org/wiki/%s", None),
    "ghsharp": ("https://github.com/hdl/containers/issues/%s", "#"),
    "ghissue": ("https://github.com/hdl/containers/issues/%s", "issue #"),
    "ghpull": ("https://github.com/hdl/containers/pull/%s", "pull request #"),
    "ghsrc": ("https://github.com/hdl/containers/blob/main/%s", None),
}
