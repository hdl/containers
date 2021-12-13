.. _UserGuide:fine-grained:

Fine-grained pulling
####################

.. note::

  These images are coloured [lime]#GREEN# in the :ref:`Graph generation/parsing <Development:graph-generation>`].

Ready-to-use images are provided for each tool, which contain the tool and the dependencies for it to run successfully. These are typically named ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]TOOL_NAME``.

.. note:: Since all the images in each collection are based on the same root image, pulling multiple images involves
  retrieving a few additional layers only. Therefore, this is the recommended approach for CI or other environments with
  limited resources.

* `ghdl-yosys-blink: Makefile <https://github.com/antonblanchard/ghdl-yosys-blink/blob/master/Makefile>`__: an example
  showcasing how to use this fine-grained approach with a makefile.
  The same make based strategy is used in `antonblanchard/microwatt <https://github.com/antonblanchard/microwatt/blob/master/Makefile>`__.
* `marph91/icestick-remote <https://github.com/marph91/icestick-remote>`__: the CI workflow for synthesis uses this approach.

Those projects use a partial Makefile such as the following, for optionally wrapping regular tool calls:

.. code-block:: bash

   CONTAINER_ENGINE ?= docker
   
   PWD = $(shell pwd)
   CONTAINER_ARGS = run --rm -v $(PWD):/wrk -w /wrk
   
   GHDL    = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/ghdl/yosys ghdl
   YOSYS   = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/ghdl/yosys yosys
   NEXTPNR = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/nextpnr/ice40 nextpnr-ice40
   ICEPACK = $(CONTAINER_ENGINE) $(CONTAINER_ARGS) gcr.io/hdl-containers/icestorm icepack

Moreover, `PyFPGA <https://github.com/PyFPGA/>`__ is a set of Python classes for vendor-independent FPGA development.
`PyFPGA/openflow <https://github.com/PyFPGA/openflow>`__ allows running GHDL, Yosys, etc. in containers.
In fact, openflow can be used along with `Edalize <https://github.com/olofk/edalize>`__'s ``EDALIZE_LAUNCHER`` environment
variable.
See also `librecores/eda-container-wrapper <https://github.com/librecores/eda-container-wrapper>`__.
