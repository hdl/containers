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

* `gh:ghdl-yosys-blink: Makefile <https://github.com/antonblanchard/ghdl-yosys-blink/blob/master/Makefile>`__:
  an example showcasing how to use this fine-grained approach with a makefile.
  The same make based strategy is used in `antonblanchard/microwatt <https://github.com/antonblanchard/microwatt/blob/master/Makefile>`__.

* `gh:marph91/icestick-remote <https://github.com/marph91/icestick-remote>`__: the CI workflow for synthesis uses this approach.

Those projects use a partial Makefile such as the following, for optionally wrapping regular tool calls:

.. code-block:: bash

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
`gh:olofk/edalize: search?q=EDALIZE_LAUNCHER <https://github.com/olofk/edalize/search?q=EDALIZE_LAUNCHER>`__.
`el_docker <https://github.com/olofk/edalize/blob/master/scripts/el_docker>`__ is a built-in launcher for Docker.
See also:

* `olofkindgren.blogspot.com: Edalize 0.3.0 <https://olofkindgren.blogspot.com/2022/01/edalize-030.html>`__
* `Support for open source EDA tools from containers (gh:olofk/edalize#221) <https://github.com/olofk/edalize/pull/221>`__
* `gh:librecores/eda-container-wrapper <https://github.com/librecores/eda-container-wrapper>`__
* `carlosedp/runme.py <https://gist.github.com/carlosedp/c0e29d55e48309a48961f2e3939acfe9>`__

PyFPGA's OpenFlow
-----------------

PyFPGA's OpenFlow (see :doc:`pyfpga:index` and `gh:PyFPGA/openflow <https://github.com/PyFPGA/openflow>`__) allows
running tools in containers, similarly to ``el_docker``.
In fact, OpenFlow can be used along with `Edalize <https://github.com/olofk/edalize>`__'s ``EDALIZE_LAUNCHER``
environment variable.
