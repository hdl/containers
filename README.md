<p align="center">
<b>WORK IN PROGRESS</b>
<br>
<b>This repository is not officialy related to SymbiFlow at the moment.</b>
</p>

<p align="center">
  <a title="'doc' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Adoc"><img alt="'doc' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/doc?longCache=true&style=flat-square&label=doc&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'base' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Abase"><img alt="'base' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/base?longCache=true&style=flat-square&label=base&logo=GitHub%20Actions&logoColor=fff"></a>
</p>

This repository contains scripts and GitHub Actions (GHA) YAML workflows for building and deploying the docker images that are used and/or published by [SymbiFlow](https://github.com/SymbiFlow). All of them are pushed to [hub.docker.com/u/symbiflow](https://hub.docker.com/u/symbiflow).

----

## Proposed collaboration flow

This repository provides base images for building and for runtime:

- [![symbiflow/build:base Docker pulls](https://img.shields.io/docker/image-size/symbiflow/build/base?longCache=true&style=flat-square&label=symbiflow%2Fbuild:base&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/build/tags) Debian Buster with updated `ca-certificates`, `curl` and Python 3.
- [![symbiflow/build:build Docker pulls](https://img.shields.io/docker/image-size/symbiflow/build/build?longCache=true&style=flat-square&label=symbiflow%2Fbuild:build&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/build/tags) based on `base`, includes `clang` and `make`.
- [![symbiflow/build:dev Docker pulls](https://img.shields.io/docker/image-size/symbiflow/build/dev?longCache=true&style=flat-square&label=symbiflow%2Fbuild:dev&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/build/tags) based on `build`, includes `cmake`, `libboost-all-dev` and `python3-dev`.

Then, each project:

- Uses base building images for building their own tools.
- Produces cache images based on `scratch`, and/or other reusable packages.
- Produces ready-to-use images based on the runtime base image.

Last, this repository merges multiple tools into ready-to-use images for specific use cases.

Finally, users consume the ready-to-use images that include a single tool, or the ones including many of them.

Some projects don't use containers at all. In some of those cases, all images are generated in this repository. However, the workload is expected to be distributed between multiple projects in the ecosystem.

## Tools/projects

The following is a non-exhaustive list of projects that we'd like to support in this repository:

- [ ] [bitman](https://github.com/khoapham/bitman)
- [ ] [cocotb](https://github.com/cocotb/cocotb)
- [ ] [fujprog](https://github.com/kost/fujprog)
- [ ] [ghdl](https://github.com/ghdl/ghdl)
- [ ] [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)
- [ ] [graphviz](https://graphviz.org/)
- [ ] [gtkwave](https://github.com/gtkwave/gtkwave)
- [ ] [icestorm](https://github.com/cliffordwolf/icestorm)
- [ ] [iverilog](https://github.com/steveicarus/iverilog)
- [ ] [netlistsvg](https://github.com/nturley/netlistsvg)
- [ ] [nextpnr](https://github.com/YosysHQ/nextpnr)
- [ ] [openFPGALoader](https://github.com/trabucayre/openFPGALoader)
- [ ] [openocd](http://openocd.org/)
- [ ] [prjtrellis](https://github.com/SymbiFlow/prjtrellis)
- [ ] [symbiyosys](https://github.com/YosysHQ/SymbiYosys)
- [ ] [verilator](https://github.com/verilator/verilator)
- [ ] [vunit](https://github.com/VUnit/vunit)
- [ ] [yosys](https://github.com/YosysHQ/yosys)

## References

- SymbiFlow:
  - [SymbiFlow/symbiflow-examples](https://github.com/SymbiFlow/symbiflow-examples)
  - [SymbiFlow/make-env](https://github.com/SymbiFlow/make-env)
    - [bit.ly/edda-conda-eda-spec](http://bit.ly/edda-conda-eda-spec): Conda based system for FPGA and ASIC Dev
    - [Support providing the environment using docker rather than conda #15](https://github.com/SymbiFlow/make-env/issues/15)
- GHDL:
  - [ghdl/docker](https://github.com/ghdl/docker)
  - [ghdl/setup-ghdl-ci](https://github.com/ghdl/setup-ghdl-ci)
- DBHI:
  - [dbhi/qus](https://github.com/dbhi/qus)
  - [dbhi/docker](https://github.com/dbhi/docker)
- [open-tool-forge/fpga-toolchain](https://github.com/open-tool-forge/fpga-toolchain)
- [im-tomu/fomu-toolchain](https://github.com/im-tomu/fomu-toolchain)
- [alpin3/ulx3s](https://github.com/alpin3/ulx3s)
- [eine/elide](https://github.com/eine/elide/tree/master/elide/docker)
- [hackfin/ghdl-cross.mk](https://github.com/hackfin/ghdl-cross.mk)
