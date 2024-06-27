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

* :gh:`tmeissner/formal_hw_verification`:
  the CI workflow uses image ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]formal/all`` along with GitHub Actions'
  *Docker Step* syntax.

* :gh:`stnolting/neorv32-setups`:
  the implementation workflow (for generating bitstreams from VHDL sources) uses image
  ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]impl`` along with GitHub Actions' *Docker Step* syntax.

.. TIP::
  * :gh:`pyTooling/Actions <pyTooling/Actions/#context>`
  * `docs.github.com: Learn GitHub Actions » Referencing a container on Docker Hub <https://docs.github.com/en/actions/learn-github-actions/finding-and-customizing-actions#referencing-a-container-on-docker-hub>`__


F4PGA
=====

.. |SHIELD:F4PGA:Examples| image:: https://img.shields.io/website.svg?label=f4pga-examples.rtfd.io&longCache=true&style=flat-square&url=http%3A%2F%2Ff4pga-examples.rtfd.io%2Fen%2Flatest%2Findex.html&logo=ReadTheDocs&logoColor=fff
   :alt: 'f4pga-examples.rtfd.io'
   :height: 22
   :target: https://f4pga-examples.rtfd.io/en/latest/building-examples.html

As explained in :ref:`F4PGA (Conda) <tools-and-images:f4pga>`, multiple ready-to-use images are provided
including Miniconda, F4PGA toolchains and architecture definitions for Xilinx's **xc7** or QuickLogic's **eos-s3**
devices.
These container images are expected to be used as explained in |SHIELD:F4PGA:Examples|, assuming that the
environment is prepared already and available in the PATH.
Hence, the Conda environment can be activated straightaway.
See, for instance:

.. sourcecode:: bash

  :~# git clone https://github.com/chipsalliance/f4pga-examples
  ...
  :~# cd f4pga-examples

  :~/f4pga-examples# docker run --rm -it \
    -v /$(pwd)://wrk \
    -w //wrk \
    gcr.io/hdl-containers/conda/f4pga/xc7/a100t

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
