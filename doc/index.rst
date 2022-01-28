HDL Containers
##############

.. include:: shields/shields.index.inc

.. centered::
  |SHIELD:Code:Repository|
  |SHIELD:Code:License|
  |SHIELD:Documentation:License|
  |SHIELD:Community:Chat|

.. raw:: html

    <br>

.. image:: _static/banner_path.svg
   :width: 500 px
   :align: center
   :target: https://github.com/hdl/containers

.. raw:: html

    <br>

    <hr>

This repository contains scripts and recipes for building, testing and deploying `OCI <https://opencontainers.org/>`__
images (aka `Docker <https://www.docker.com/>`__ | `Podman <https://podman.io>`__ images) including open source
:wikipedia:`Electronic Design Automation (EDA) <Electronic_design_automation>` tooling.
All the images are pushed to `gcr.io/hdl-containers <http://gcr.io/hdl-containers/>`__, and mirrored to
`ghcr.io/hdl <https://github.com/orgs/hdl/packages>`__ and `hub.docker.com/u/hdlc <https://hub.docker.com/u/hdlc>`__:

.. centered:: |SHIELD:Registry:GCR| |SHIELD:Registry:GHCR| |SHIELD:Registry:Docker|

.. toctree::
  :hidden:

  Home <http://hdl.github.io/containers>
  CollectionsAndArchitectures
  ToolsAndImages
  About

.. toctree::
  :caption: User Guide
  :hidden:

  ug/index
  ug/FineGrained
  ug/AllInOne
  ug/GUI
  USB/IP <ug/USBIP>

.. toctree::
  :caption: Development
  :hidden:

  dev/Contributing
  dev/Graphs
  dev/PackageImages
  dev/Utils
  dev/CI
  dev/Tasks

.. toctree::
  :caption: Appendix
  :hidden:

  References
  License
  Doc-License

