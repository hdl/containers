.. _context:

About
#####

Unai Martinez-Corral [
:gh:`@GitHub <umarcor>`
`@GitLab <https://gitlab.com/umarcor>`__
`@Twitter <https://twitter.com/unaimarcor>`__
]
and :gh:`contributors <hdl/containers/graphs/contributors>`

Context
=======

This project started in early 2017 at GitHub repository :gh:`ghdl/ghdl` (which was named ``tgingold/ghdl`` back then).
The main purpose was testing GHDL on multiple GNU/Linux distributions (Debian, Ubuntu and Fedora), since
`Travis CI <https://travis-ci.org/>`__ supported Ubuntu only and Docker.
For each target platform, two images were used, one for building and another one for testing.

Later, most of the Docker related sources were split to repository :gh:`ghdl/docker`.
There, some additional simulation tools were added, such as `VUnit <http://vunit.github.io/>`__ and
`GtkWave <http://gtkwave.sourceforge.net/>`__.
Images including the :gh:`ghdl-language-server <ghdl/ghdl-language-server>` were also added.
When experimental synthesis support was added to GHDL in 2019, and since it provides a plugin for :gh:`Yosys <YosysHQ/yosys>`,
containers including tools for providing a complete open source bitstream generation and formal verification workflow
were requested and contributed.
Those were
:gh:`nextpnr <YosysHQ/nextpnr>`,
:gh:`icestorm <YosysHQ/icestorm>`,
:gh:`prjtrellis <YosysHQ/prjtrellis>`,
:gh:`SymbiYosys <YosysHQ/SymbiYosys>`,
etc.

At some point, ``ghdl/docker`` had as much content related to non-GHDL tools as resources related to the organisation.
In the second half of 2019, sharing the development effort was proposed to maintainers of Yosys (:gh:`YosysHQ/yosys#1287 <YosysHQ/yosys/issues/1287>`)
and LibreCores (:gh:`librecores/docker-images#33 <librecores/docker-images/issues/33>`), which went unfortunately
unnoticed.

At the same time, `F4PGA <https://f4pga.org>`__ aimed at gathering open source projects for providing an integrated open
source EDA solution.
However, it did not have official container images and `help was wanted <https://f4pga.org/developers.html>`__.
This repository was initially created for moving all the tools which were not part of GHDL, from ghdl/docker to
f4pga/containers.
However, since F4PGA was (partially still is) focused on Verilog, the scope was widened to include VHDL, and the
repository was published at :gh:`hdl/containers` in 2020.

In parallel to splitting ghdl/docker form ghdl/ghdl, in early 2019 :gh:`dbhi/qus` (see :doc:`qus:index`) was created
as a generalisation of :gh:`multiarch/qemu-user-static`.
*qus* is used in :gh:`dbhi/containers` to build multi-architecture container images and manifests on Continuous
Integration (CI) services with amd64 hosts only (say Travis CI or :gh:`GitHub Actions <features/actions>`).
Currently, ``hdl/containers`` uses the same solution to build container images for *foreign* architectures.

Until the end of 2020, the scope of ``hdl/containers`` was limited to HDL simulation, formal verification and FPGA
bitstream generation on ``amd64``; and container images were distributed through ``docker.io`` only.
In 2021, tools for ASIC development and images for other architectures were added, and two other registries were used:
``gcr.io`` (Google Container Registry) and ``ghcr.io`` (GitHub Container Registry).
Due to ``docker.io`` not supporting multiple ``/`` separators in image names, ``gcr.io`` was used as the default to push
images for all architectures and collections.

Since most of the plumbing is automated, from 2024Q3 to 2026Q3 latest available images were used in teaching and development
but this repository was not actively maintained.
However, the Google Container Registry (GCR) was deprecated and it was shut down in 2025; thus, producing errors when
trying to pull ``gcr.io/hdl/containers/*`` images.
In 2026 the default in the recipes was changed to ``ghcr.io``.

HDL Organisation
================

.. include:: shields/shields.hdl.inc

* |SHIELD:HDL:packages|

* |SHIELD:HDL:awesome| |SHIELD:Site:awesome|

* |SHIELD:HDL:constraints| |SHIELD:Documentation:constraints|

* |SHIELD:HDL:smoke-tests|
