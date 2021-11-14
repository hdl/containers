Tools and images
################

By default, latest development versions (branches ``master``|``main``) of tools are built.
Then, smoke tests are executed and, if successful, the corresponding images are updated in the registries.
However, some specific tools are *_not_* built from sources, but installed through system package managers.
Those are marked with ``!`` in the table below.

.. note::
  Package images are not to be used for executing the tools, but for composing images including multiple resources.
  See `Development: Package images <dev/index.html#_package_images>`__ for further details.

include::ToolsTable.py[]

Images including multiple tools
===============================

* **S**imulation:

  * OCIImage:sim[] GHDL + Verilator + Icarus Verilog
  * OCIImage:sim/osvb[] cocotb, OSVVM and VUnit; on top of ``sim``.
  * OCIImage:sim/scipy-slim[] ``matplotlib`` and ``numpy``, on top of ``sim``.
  * OCIImage:sim/scipy[] ``osvb`` on top of ``scipy-slim``.
  * OCIImage:sim/octave-slim[] ``octave``, on top of ``sim``.
  * OCIImage:sim/octave[] ``osvb`` on top of ``octave-slim``.

* **I**mplementation: GHDL + Yosys + nextpnr

  * OCIImage:impl/ice40[] nextpnr-ice40 only, and OCIImage:impl/icestorm[] including icestorm.
  * OCIImage:impl/ecp5[] nextpnr-ecp5 only, and OCIImage:impl/prjtrellis[] including prjtrellis.
  * OCIImage:impl/generic[] nextpnr-generic only.
  * OCIImage:impl/pnr[] all nextpnr targets (ecp5, ice40, and generic).
  * OCIImage:impl[] impl:pnr, including icestorm and prjtrellis.

* **F**ormal:

  * OCIImage:formal[] all solvers depending on Python 3.
  * OCIImage:formal/min[] Z3 only.
  * OCIImage:formal/all[] all solvers, depending on either Python 2 or Python 3.

* **P**rogramming: OCIImage:prog[]
