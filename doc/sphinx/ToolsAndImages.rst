.. _tools-and-images:

Tools and images
################

By default, latest development versions (branches ``master`` | ``main``) of tools are built.
Then, smoke tests are executed and, if successful, the corresponding images are updated in the registries.
However, some specific tools are *not* built from sources, but installed through system package managers.
Those are marked with ``!`` in the table below.

include::ToolsTable.py[]

.. NOTE::
  Package images are not to be used for executing the tools, but for composing images including multiple resources.
  See `Development: Package images <dev/index.html#_package_images>`__ for further details.

Images including multiple tools
===============================

* **S**\ imulation:

  * OCIImage:sim[] GHDL + Verilator + Icarus Verilog
  * OCIImage:sim/osvb[] cocotb, OSVVM and VUnit; on top of ``sim``.
  * OCIImage:sim/scipy-slim[] ``matplotlib`` and ``numpy``, on top of ``sim``.
  * OCIImage:sim/scipy[] ``osvb`` on top of ``scipy-slim``.
  * OCIImage:sim/octave-slim[] ``octave``, on top of ``sim``.
  * OCIImage:sim/octave[] ``osvb`` on top of ``octave-slim``.

* **I**\ mplementation: GHDL + Yosys + nextpnr

  * OCIImage:impl/ice40[] nextpnr-ice40 only, and OCIImage:impl/icestorm[] including icestorm.
  * OCIImage:impl/ecp5[] nextpnr-ecp5 only, and OCIImage:impl/prjtrellis[] including prjtrellis.
  * OCIImage:impl/generic[] nextpnr-generic only.
  * OCIImage:impl/pnr[] all nextpnr targets (ecp5, ice40, and generic).
  * OCIImage:impl[] impl:pnr, including icestorm and prjtrellis.

* **F**\ ormal:

  * OCIImage:formal[] all solvers depending on Python 3.
  * OCIImage:formal/min[] Z3 only.
  * OCIImage:formal/all[] all solvers, depending on either Python 2 or Python 3.

* **P**\ rogramming: OCIImage:prog[]

.. _tools-and-images:symbiflow:

SymbiFlow (Conda)
=================

`SymbiFlow <https://hdl.github.io/awesome/items/symbiflow/>`__ is an ecosystem of EDA tools for the development of FPGAs of multiple vendors.
The tools used in the SymbiFlow ecosystem are packaged by `Antmicro <https://antmicro.com>`__ and contributors using `Conda <https://docs.conda.io/en/latest>`__.
The sources of Conda packages for EDA tooling are found in
https://github.com/hdl/conda-ci[image:https://img.shields.io/badge/hdl-conda--ci-f2f1ef.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[title='hdl/conda-ci GitHub repository']],
https://github.com/hdl/conda-compilers[image:https://img.shields.io/badge/hdl-conda--compilers-f2f1ef.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[title='hdl/conda-compilers GitHub repository']],
https://github.com/hdl/conda-eda[image:https://img.shields.io/badge/hdl-conda--eda-f2f1ef.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[title='hdl/conda-eda GitHub repository']],
https://github.com/hdl/conda-misc[image:https://img.shields.io/badge/hdl-conda--misc-f2f1ef.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[title='hdl/conda-misc GitHub repository']] and
https://github.com/hdl/conda-prog[image:https://img.shields.io/badge/hdl-conda--prog-f2f1ef.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[title='hdl/conda-prog GitHub repository']].

In HDL Containers, as a complement to container images based on tools built on other container images, a set of SymbiFlow is provided.
The base is OCIImage:conda[], which includes a `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__ setup.
On top of that, the following ready-to-use images allow following the guidelines in https://github.com/SymbiFlow/symbiflow-examples[image:https://img.shields.io/badge/SymbiFlow-symbiflow--examples-9258ff.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef&labelColor=5a2ab5[title='SymbiFlow/symbiflow-examples GitHub repository']]
(https://symbiflow-examples.rtfd.io/en/latest/building-examples.html[image:https://img.shields.io/website.svg?label=symbiflow-examples.rtfd.io&longCache=true&style=flat-square&url=http%3A%2F%2Fsymbiflow-examples.rtfd.io%2Fen%2Flatest%2Findex.html&logo=ReadTheDocs&logoColor=fff[title='symbiflow-examples.rtfd.io']]):

* OCIImage:conda/symbiflow/xc7/toolchain[]: the toolchain for ``FPGA_FAM=xc7``, on top of ``conda``.
  The following images are based on this:

  * OCIImage:conda/symbiflow/xc7/a50t[]: includes architecture definitions for *xc7a50t*.

  * OCIImage:conda/symbiflow/xc7/a100t[]: includes architecture definitions for *xc7a100t*.

  * OCIImage:symbiflow/xc7/a200t[]: includes architecture definitions for *xc7a200t*.

  * OCIImage:conda/symbiflow/xc7/z010[]: includes architecture definitions for *xc7z010*.

  * OCIImage:conda/symbiflow/xc7/z020[]: includes architecture definitions for *xc7z020*.

  * OCIImage:conda/symbiflow/xc7[]: includes all the architecture definitions for the *xc7* family, except *xc7a200t* (due to hard disk limits on GitHub Actions).

* OCIImage:conda/symbiflow/eos-s3[]: the toolchain for ``FPGA_FAM=eos-s3`` and the architecture definitions, on top of ``conda``.

.. important::
  The compression ratio of these images is very high compared to other container images.
  That is because these include a significant amount of data in text format, which is much better compressed than binaries.
  As a result, the size of the images when pulled is approximately as follows:

  * xc7/toolchain: 3 GB

  * xc7/a50t: 6 GB

  * xc7/a100t: 8.5 GB

  * xc7/a200t: 15 GB

  * xc7/z010: 5 GB

  * xc7/z020: 7.5 GB

  * xc7: 18 GB (would be 30 GB if a200t was included)

  * eos-s3: 2 GB

.. _tools-and-images:to-do:

To Do
=====

* `BitMan <https://github.com/khoapham/bitman>`__
* `ecpprog <https://hdl.github.io/awesome/items/ecpprog>`__
* `fujprog <https://hdl.github.io/awesome/items/fujprog>`__
* `netlistsvg <https://hdl.github.io/awesome/items/netlistsvg>`__
* `xschem <https://github.com/StefanSchippers/xschem>`__ (`#28 <https://github.com/hdl/containers/issues/28>`__)
* `IRSIM <http://opencircuitdesign.com/irsim/>`__ (`#30 <https://github.com/hdl/containers/issues/30>`__)
* `ecpdap <https://github.com/adamgreig/ecpdap>`__
* `LSOracle <https://github.com/lnis-uofu/LSOracle>`__
