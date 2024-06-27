.. _UserGuide:fine-grained:

Fine-grained pulling
####################

.. role:: green

.. NOTE::
  These images are coloured :green:`GREEN` in the :ref:`Development:graphs`.

Ready-to-use images are provided for each tool, which contain the tool and the dependencies for it to run successfully.
These are typically named ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]TOOL_NAME``.

.. HINT::
  Since all the images in each collection are based on the same root image, pulling multiple images involves retrieving
  a few additional layers only.
  Therefore, this is the recommended approach for CI or other environments with limited resources.

Makefiles
=========

* :gh:`ghdl-yosys-blink: Makefile <antonblanchard/ghdl-yosys-blink/blob/master/Makefile>`:
  an example showcasing how to use this fine-grained approach with a makefile.
  The same make based strategy is used in :gh:`gh:antonblanchard/microwatt <antonblanchard/microwatt/blob/master/Makefile>`.

* :gh:`marph91/icestick-remote`: the CI workflow for synthesis uses this approach.

Those projects use a partial Makefile such as the following, for optionally wrapping regular tool calls:

.. sourcecode:: bash

   CONTAINER_ENGINE ?= docker

   PWD = $(shell pwd)
   CONTAINER_ARGS = run --rm -v $(PWD):/wrk -w /wrk

   GHDL    = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/ghdl/yosys ghdl
   YOSYS   = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/ghdl/yosys yosys
   NEXTPNR = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/nextpnr/ice40 nextpnr-ice40
   ICEPACK = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/icestorm icepack

Python launchers
================

There are several EDA tooling management projects which allow wrapping the execution of commands on containers.
Any of them can be used with the containers provided in this repository.

EDA²'s Docker abstraction
-------------------------

Layer CLITool of EDA² (see :doc:`edaa:index` and :doc:`clitool:index`), provides ``Docker.py`` to be combined with any
of the tools supported in the same repository.

Edalize's Launcher
------------------

Edalize (see :doc:`edalize:index`) provides ``EDALIZE_LAUNCHER``, which allows overriding each command:
:gh:`olofk/edalize: search?q=EDALIZE_LAUNCHER <olofk/edalize/search?q=EDALIZE_LAUNCHER>`.
:gh:`el_docker <olofk/edalize/blob/master/scripts/el_docker>` is a built-in launcher for Docker.
See also:

* `olofkindgren.blogspot.com: Edalize 0.3.0 <https://olofkindgren.blogspot.com/2022/01/edalize-030.html>`__
* :gh:`Support for open source EDA tools from containers (gh:olofk/edalize#221) <olofk/edalize/pull/221>`
* :gh:`librecores/eda-container-wrapper`
* `carlosedp/runme.py <https://gist.github.com/carlosedp/c0e29d55e48309a48961f2e3939acfe9>`__

  * :gh:`Improve launcher script with new containers (gh:olofk/edalize#299) <olofk/edalize/pull/299>`

PyFPGA's OpenFlow
-----------------

PyFPGA's OpenFlow (see :doc:`pyfpga:index` and :gh:`PyFPGA/openflow`) allows running tools in containers, similarly to
``el_docker``.
In fact, OpenFlow can be used along with :gh:`Edalize <olofk/edalize>`'s ``EDALIZE_LAUNCHER`` environment variable.
