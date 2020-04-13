Images for development (i.e., building and/or testing):

- [![ghdl/cache Docker pulls](https://img.shields.io/docker/pulls/ghdl/cache?label=ghdl%2Fcache&style=flat-square)](https://hub.docker.com/r/ghdl/cache) external dependencies which we want to keep almost in the edge.

Ready-to-use images:

- [![ghdl/synth Docker pulls](https://img.shields.io/docker/pulls/ghdl/synth?label=ghdl%2Fsynth&style=flat-square)](https://hub.docker.com/r/ghdl/synth) images allow to generate and program bitstreams from HDL sources with open source tools: [ghdl](https://github.com/ghdl/ghdl), [yosys](https://github.com/YosysHQ/yosys), [nextpnr](https://github.com/YosysHQ/nextpnr) (`master`), [icestorm](https://github.com/cliffordwolf/icestorm), [prjtrellis](https://github.com/SymbiFlow/prjtrellis), etc.

## GHA workflows

<p align="center">
  <!--SymbiFlow/containers-->
  <a title="'cache' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Acache"><img alt="'cache' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/cache?longCache=true&style=flat-square&label=cache"></a><!--
  -->
  <a title="'synth' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Asynth"><img alt="'synth' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/synth?longCache=true&style=flat-square&label=synth"></a><!--
  -->
</p>

> NOTE: currently, there is no triggering mechanism set up between different GitHub repositories. All the workflows in this repo are triggered by CRON jobs.

### · [cache](.github/workflows/cache.yml) (5 jobs -max 4-, 11 images) [weekly]

Build and push all the images to `ghdl/cache:*` and some to `ghdl/synth:*`. Each of the following images includes a tool on top of a `debian:buster-slim` image:

- `ghdl/synth:yosys`: includes [yosys](https://github.com/YosysHQ/yosys) (`master`).
- `ghdl/synth:icestorm`: includes [icestorm](https://github.com/cliffordwolf/icestorm) (`master`) without `iceprog`.
- `ghdl/synth:trellis`: includes [prjtrellis](https://github.com/SymbiFlow/prjtrellis) (`master`).
- `ghdl/synth:prog`: includes `iceprog` from [icestorm](https://github.com/cliffordwolf/icestorm) (`master`) and [openocd](http://openocd.org/).
- `ghdl/synth:nextpnr-ice40`: includes [nextpnr](https://github.com/YosysHQ/nextpnr) (`master`) with support for ICE40 devices only.
- `ghdl/synth:nextpnr-ecp5`: includes [nextpnr](https://github.com/YosysHQ/nextpnr) (`master`) with support for ECP5 devices only.
- `ghdl/synth:nextpnr`: includes [nextpnr](https://github.com/YosysHQ/nextpnr) (`master`) with support for all architectures (see [nextpnr: Additional notes for building nextpnr](https://github.com/YosysHQ/nextpnr#additional-notes-for-building-nextpnr)).

Furthermore:

- `ghdl/cache:yosys-gnat`: includes `libgnat-8` on top of `ghdl/synth:yosys`.
- `ghdl/cache:gtkwave`: contains a tarball with [GtkWave](http://gtkwave.sourceforge.net/) (`gtkwave3-gtk3`), prebuilt for images based on Debian Buster.
- `ghdl/cache:formal`: contains a tarball with [SymbiYosys](https://github.com/YosysHQ/SymbiYosys) (`master`) and [z3](https://github.com/Z3Prover/z3) (`master`), prebuilt for images based on Debian Buster.
- `ghdl/synth:symbiyosys`: includes the tarball from `ghdl/cache:formal` and Python3 on top of `ghdl/synth:yosys`.
