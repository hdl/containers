HDL Containers
##############

.. |SHIELD:WorkflowTest| image:: https://img.shields.io/github/workflow/status/dbhi/qus/Test?longCache=true&style=flat-square&logo=github&label=Test
   :alt: 'Test' workflow Status
   :height: 22
   :target: https://github.com/hdl/containers

.. image:: _static/banner.svg
   :width: 500 px
   :align: center
   :target: https://github.com/ghdl/ghdl-cosim

.. raw:: html

    <br>

    <hr>

This repository contains scripts and recipes for building, testing and deploying `OCI <https://opencontainers.org/>`__
images (aka `Docker <https://www.docker.com/>`__ | `Podman <https://podman.io>`__ images) including open source `Electronic Design Automation (EDA) <https://en.wikipedia.org/wiki/Electronic_design_automation>`__ tooling.
All the images are pushed to `gcr.io/hdl-containers <http://gcr.io/hdl-containers/>`__, and mirrored to
`ghcr.io/hdl <https://github.com/orgs/hdl/packages>`__ and
`hub.docker.com/u/hdlc <https://hub.docker.com/u/hdlc>`__:

.. |SHIELD:WorkflowTest| image:: https://img.shields.io/badge/-gcr.io/hdl--containers-555555.svg?longCache=true&style=flat-square&logo=OpenContainersInitiative&logoColor=f2f1ef
   :alt: 'Google Container Registry'
   :height: 22
   :target: https://gcr.io/hdl-containers

.. |SHIELD:WorkflowTest| image:: https://img.shields.io/badge/-ghcr.io/hdl-555555.svg?longCache=true&style=flat-square&logo=OpenContainersInitiative&logoColor=f2f1ef
   :alt: 'GitHub Container Registry'
   :height: 22
   :target: https://github.com/hdl/containers/packages

.. |SHIELD:WorkflowTest| image:: https://img.shields.io/badge/-docker.io/hdlc-555555.svg?longCache=true&style=flat-square&logo=OpenContainersInitiative&logoColor=f2f1ef
   :alt: 'Docker Hub'
   :height: 22
   :target: https://hub.docker.com/u/hdlc

Find usage guidelines and how to contribute in the following sections:

- `User Guide <ug/index.html>`__
- `Development and contributing <dev/index.html>`__

.. toctree::
  :hidden:

  CollectionsAndArchitectures
  ToolsAndImages
  ToDo
  Context
  References
