.. _context:

About
#####

Unai Martinez-Corral and `contributors <https://github.com/hdl/containers/graphs/contributors>`__ -
`@GitHub <https://github.com/umarcor>`__
`@GitLab <https://gitlab.com/umarcor>`__
`@Twitter <https://twitter.com/unaimarcor>`__

Context
=======

This project started in early 2017 at GitHub repository `ghdl/ghdl <https://github.com/ghdl/ghdl>`__ (which was named
tgingold/ghdl back then).
The main purpose was testing GHDL on multiple GNU/Linux distributions (Debian, Ubuntu and Fedora), since
`Travis CI <https://travis-ci.org/>`__ supported Ubuntu only and Docker.
For each target platform, two images were used, one for building and another one for testing.

Later, most of the Docker related sources were split to repository `ghdl/docker <https://github.com/ghdl/docker>`__.
There, some additional simulation tools were added, such as `VUnit <http://vunit.github.io/>`__ and `GtkWave <http://gtkwave.sourceforge.net/>`__.
Images including the `ghdl-language-server <https://github.com/ghdl/ghdl-language-server>`__ were also added.
When experimental synthesis support was added to GHDL in 2019, and since it provides a plugin for
`Yosys <https://github.com/YosysHQ/yosys>`__, containers including tools for providing a complete open source bitstream
generation and formal verification workflow were requested and contributed.
Those were
`nextpnr <https://github.com/YosysHQ/nextpnr>`__,
`icestorm <https://github.com/YosysHQ/icestorm>`__,
`prjtrellis <https://github.com/YosysHQ/prjtrellis>`__,
`SymbiYosys <https://github.com/YosysHQ/SymbiYosys>`__,
etc.

At some point, ghdl/docker had as much content related to non-GHDL tools, as resources related to the organisation.
In the second half of 2019, sharing the development effort was proposed to maintainers of Yosys (`YosysHQ/yosys#1287 <https://github.com/YosysHQ/yosys/issues/1287>`__)
and LibreCores (`librecores/docker-images#33 <https://github.com/librecores/docker-images/issues/33>`__), which went
unfortunately unnoticed.

At the same time, `SymbiFlow <https://symbiflow.github.io>`__ aimed at gathering open source projects for providing an
integrated open source EDA solution.
However, it did not have official container images and `help was wanted <https://symbiflow.github.io/developers.html>`__.
This repository was initially created for moving all the tools which were not part of GHDL, from ghdl/docker to
symbiflow/containers.
However, since SymbiFlow was (partially still is) focused on Verilog, the scope was widened to include VHDL, and the
repository was published at `hdl/containers <https://github.com/hdl/containers>`__ in 2020.

In parallel to splitting ghdl/docker form ghdl/ghdl, in early 2019 `dbhi/qus <https://github.com/dbhi/qus>`__ (see
:doc:`qus:index`) was created as a generalisation of `multiarch/qemu-user-static <https://github.com/multiarch/qemu-user-static>`__.
*qus* is used in `dbhi/containers <https://github.com/dbhi/containers>`__ to build multi-architecture container images
and manifests on Continuous Integration (CI) services with amd64 hosts only (say Travis CI or `GitHub Actions <https://github.com/features/actions>`__).
Currently, hdl/containers uses the same solution to build container images for *foreign* architectures.

Until the end of 2020, the scope of hdl/containers was limited to HDL simulation, formal verification and FPGA bitstream
generation; and container images were distributed through ``docker.io`` only.
Since 2021, tools for ASIC development are also provided, and two other registries are used as well:
``gcr.io`` and ``ghcr.io``.

HDL Organisation
================

.. include:: shields/shields.hdl.inc

* |SHIELD:HDL:packages|

* |SHIELD:HDL:awesome| |SHIELD:Site:awesome|

* |SHIELD:HDL:constraints| |SHIELD:Documentation:constraints|

* |SHIELD:HDL:smoke-tests|
