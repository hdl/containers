.. _UserGuide:all-in-one:

All-in-one images
#################

.. role:: maroon

.. NOTE::
   These images are coloured :maroon:`BROWN` in the :ref:`Development:graphs`.

Multiple tools from fine-grained images are included in larger images for common use cases.
These are named ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]MAIN_USAGE``.
This is the recommended approach for users who are less familiar with containers and want a quick replacement for
full-featured virtual machines.
Coherently, some common Unix tools (such as make or cmake) are also included in these all-in-one images.

* `gh:tmeissner/formal_hw_verification <https://github.com/tmeissner/formal_hw_verification>`__:
  the CI workflow uses image ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]formal/all`` along with GitHub Actions'
  *Docker Step* syntax.

* `gh:stnolting/neorv32-setups <https://github.com/stnolting/neorv32-setups>`__:
  the implementation workflow (for generating bitstreams from VHDL sources) uses image
  ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]impl`` along with GitHub Actions' *Docker Step* syntax.

.. TIP::
  * `gh:pyTooling/Actions <https://github.com/pyTooling/Actions/#context>`__
  * `docs.github.com: Learn GitHub Actions > Referencing a container on Docker Hub <https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/finding-and-customizing-actions#referencing-a-container-on-docker-hub>`__


SymbiFlow
=========

.. |SHIELD:SymbiFlow:Examples| image:: https://img.shields.io/website.svg?label=symbiflow-examples.rtfd.io&longCache=true&style=flat-square&url=http%3A%2F%2Fsymbiflow-examples.rtfd.io%2Fen%2Flatest%2Findex.html&logo=ReadTheDocs&logoColor=fff
   :alt: 'symbiflow-examples.rtfd.io'
   :height: 22
   :target: https://symbiflow-examples.rtfd.io/en/latest/building-examples.html

As explained in :ref:`SymbiFlow (Conda) <tools-and-images:symbiflow>`, multiple ready-to-use images are provided
including Miniconda, SymbiFlow toolchains and architecture definitions for Xilinx's **xc7** or QuickLogic's **eos-s3**
devices.
These container images are expected to be used as explained in |SHIELD:SymbiFlow:Examples|, assuming that the
environment is prepared already and available in the PATH.
Hence, the Conda environment can be activated straightaway.
See, for instance:

.. code-block:: bash

  :~# git clone https://github.com/SymbiFlow/symbiflow-examples
  ...
  :~# cd symbiflow-examples

  :~/symbiflow-examples# docker run --rm -it \
    -v /$(pwd)://wrk \
    -w //wrk \
    gcr.io/hdl-containers/conda/symbiflow/xc7/a100t

  ...
  (xc7) root@c3d4dd1d97cc:/wrk# TARGET="arty_100" make -C xc7/picosoc_demo/
  ...
  (xc7) root@c3d4dd1d97cc:/wrk# ls -1 xc7/picosoc_demo/build/arty_100/
  constraints.place
  fasm.log
  pack.log
  packing_pin_util.rpt
  place.log
  pre_pack.report_timing.setup.rpt
  report_timing.hold.rpt
  report_timing.setup.rpt
  report_unconstrained_timing.hold.rpt
  report_unconstrained_timing.setup.rpt
  route.log
  top.bit
  top.eblif
  top.fasm
  top.ioplace
  top.json
  top.json.carry_fixup.json
  top.json.carry_fixup_out.json
  top.json.post_abc9.ilang
  top.json.pre_abc9.ilang
  top.net
  top.net.post_routing
  top.place
  top.route
  top.sdc
  top_io.json
  top_synth.log
  top_synth.v
  top_synth.v.premap.v
