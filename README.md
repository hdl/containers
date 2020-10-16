<p align="center">
<b>WORK IN PROGRESS</b>
<br>
<b>This repository is not officialy related to SymbiFlow at the moment.</b>
</p>

<p align="center">
  <a title="'doc' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Adoc"><img alt="'doc' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/doc?longCache=true&style=flat-square&label=doc&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'base' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Abase"><img alt="'base' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/base?longCache=true&style=flat-square&label=base&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
</p>
<p align="center">
  <a title="'ghdl' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Aghdl"><img alt="'ghdl' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/ghdl?longCache=true&style=flat-square&label=ghdl&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'gtkwave' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Agtkwave"><img alt="'gtkwave' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/gtkwave?longCache=true&style=flat-square&label=gtkwave&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'icestorm' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Aicestorm"><img alt="'icestorm' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/icestorm?longCache=true&style=flat-square&label=icestorm&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'nextpnr' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Anextpnr"><img alt="'nextpnr' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/nextpnr?longCache=true&style=flat-square&label=nextpnr&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'prjtrellis' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Aprjtrellis"><img alt="'prjtrellis' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/prjtrellis?longCache=true&style=flat-square&label=prjtrellis&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
</p>
<p align="center">
  <a title="'symbiyosys' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Asymbiyosys"><img alt="'symbiyosys' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/symbiyosys?longCache=true&style=flat-square&label=symbiyosys&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'yosys' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Ayosys"><img alt="'yosys' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/yosys?longCache=true&style=flat-square&label=yosys&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'z3' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Az3"><img alt="'z3' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/z3?longCache=true&style=flat-square&label=z3&logo=GitHub%20Actions&logoColor=fff"></a>
</p>
<p align="center">
  <a title="'formal' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Aformal"><img alt="'formal' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/formal?longCache=true&style=flat-square&label=formal&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'prog' workflow Status" href="https://github.com/eine/symbiflow-containers/actions?query=workflow%3Aprog"><img alt="'prog' workflow Status" src="https://img.shields.io/github/workflow/status/eine/symbiflow-containers/prog?longCache=true&style=flat-square&label=prog&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
</p>

This repository contains scripts and GitHub Actions (GHA) YAML workflows for building and deploying the docker images that are used and/or published by [SymbiFlow](https://github.com/SymbiFlow). All of them are pushed to [hub.docker.com/u/symbiflow](https://hub.docker.com/u/symbiflow).

----

## Proposed collaboration flow

This repository provides base images for building and for runtime:

- [![symbiflow/build:base Docker image size](https://img.shields.io/docker/image-size/symbiflow/build/base?longCache=true&style=flat-square&label=symbiflow%2Fbuild:base&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/build/tags) Debian Buster with updated `ca-certificates`, `curl` and Python 3.
- [![symbiflow/build:build Docker image size](https://img.shields.io/docker/image-size/symbiflow/build/build?longCache=true&style=flat-square&label=symbiflow%2Fbuild:build&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/build/tags) based on `base`, includes `clang` and `make`.
- [![symbiflow/build:dev Docker image size](https://img.shields.io/docker/image-size/symbiflow/build/dev?longCache=true&style=flat-square&label=symbiflow%2Fbuild:dev&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/build/tags) based on `build`, includes `cmake`, `libboost-all-dev` and `python3-dev`.

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
- [x] [ghdl](https://github.com/ghdl/ghdl)
  - [![symbiflow/ghdl:latest Docker image size](https://img.shields.io/docker/image-size/symbiflow/ghdl/latest?longCache=true&style=flat-square&label=symbiflow%2Fghdl&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/ghdl/tags)
  - [![symbiflow/ghdl:yosys Docker image size](https://img.shields.io/docker/image-size/symbiflow/ghdl/yosys?longCache=true&style=flat-square&label=symbiflow%2Fghdl:yosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/ghdl/tags)
  - In `symbiflow/formal`.
- [x] [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)
  - In `symbiflow/ghdl:yosys` and `symbiflow/formal`.
- [x] [graphviz](https://graphviz.org/)
  - In `symbiflow/yosys`, `symbiflow/ghdl:yosys` and `symbiflow/formal`.
- [x] [gtkwave](https://github.com/gtkwave/gtkwave)
  - [![symbiflow/pkg:gtkwave Docker image size](https://img.shields.io/docker/image-size/symbiflow/pkg/gtkwave?longCache=true&style=flat-square&label=symbiflow%2Fpkg:gtkwave&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/pkg/tags)
- [x] [icestorm](https://github.com/cliffordwolf/icestorm)
  - [![symbiflow/icestorm:latest Docker image size](https://img.shields.io/docker/image-size/symbiflow/icestorm/latest?longCache=true&style=flat-square&label=symbiflow%2Ficestorm&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/icestorm/tags)
  - [![symbiflow/pkg:icestorm Docker image size](https://img.shields.io/docker/image-size/symbiflow/pkg/icestorm?longCache=true&style=flat-square&label=symbiflow%2Fpkg:icestorm&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/pkg/tags)
- [ ] [iverilog](https://github.com/steveicarus/iverilog)
- [ ] [netlistsvg](https://github.com/nturley/netlistsvg)
- [x] [nextpnr](https://github.com/YosysHQ/nextpnr)
  - [![symbiflow/nextpnr:latest Docker image size](https://img.shields.io/docker/image-size/symbiflow/nextpnr/latest?longCache=true&style=flat-square&label=symbiflow%2Fnextpnr&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/nextpnr/tags)
  - [![symbiflow/nextpnr:ice40 Docker image size](https://img.shields.io/docker/image-size/symbiflow/nextpnr/ice40?longCache=true&style=flat-square&label=symbiflow%2Fnextpnr:ice40&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/nextpnr/tags)
  - [![symbiflow/nextpnr:ecp5 Docker image size](https://img.shields.io/docker/image-size/symbiflow/nextpnr/ecp5?longCache=true&style=flat-square&label=symbiflow%2Fnextpnr:ecp5&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/nextpnr/tags)
- [ ] [openFPGALoader](https://github.com/trabucayre/openFPGALoader)
- [x] [openocd](http://openocd.org/)
  - In `symbiflow/prog`.
- [x] [prjtrellis](https://github.com/SymbiFlow/prjtrellis)
  - [![symbiflow/prjtrellis:latest Docker image size](https://img.shields.io/docker/image-size/symbiflow/prjtrellis/latest?longCache=true&style=flat-square&label=symbiflow%2Fprjtrellis&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/prjtrellis/tags)
  - [![symbiflow/pkg:prjtrellis Docker image size](https://img.shields.io/docker/image-size/symbiflow/pkg/prjtrellis?longCache=true&style=flat-square&label=symbiflow%2Fpkg:prjtrellis&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/pkg/tags)
- [x] [symbiyosys](https://github.com/YosysHQ/SymbiYosys)
  - [![symbiflow/pkg:symbiyosys Docker image size](https://img.shields.io/docker/image-size/symbiflow/pkg/symbiyosys?longCache=true&style=flat-square&label=symbiflow%2Fpkg:symbiyosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/pkg/tags)
  - In `symbiflow/formal`.
- [ ] [verilator](https://github.com/verilator/verilator)
- [ ] [vunit](https://github.com/VUnit/vunit)
- [ ] [Yices 2](https://github.com/SRI-CSL/yices2)
- [x] [yosys](https://github.com/YosysHQ/yosys)
  - [![symbiflow/yosys:latest Docker image size](https://img.shields.io/docker/image-size/symbiflow/yosys/latest?longCache=true&style=flat-square&label=symbiflow%2Fyosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/yosys/tags)
  - [![symbiflow/pkg:yosys Docker image size](https://img.shields.io/docker/image-size/symbiflow/pkg/yosys?longCache=true&style=flat-square&label=symbiflow%2Fpkg:yosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/pkg/tags)
  - In `symbiflow/ghdl:yosys` and `symbiflow/formal`.
- [x] [z3](https://github.com/Z3Prover/z3)
  - [![symbiflow/pkg:z3 Docker image size](https://img.shields.io/docker/image-size/symbiflow/pkg/z3?longCache=true&style=flat-square&label=symbiflow%2Fpkg:z3&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/pkg/tags)
  - In `symbiflow/formal`.

## Images including multiple tools

- [![symbiflow/prog:latest Docker image size](https://img.shields.io/docker/image-size/symbiflow/prog/latest?longCache=true&style=flat-square&label=symbiflow%2Fprog&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/prog/tags)
  - iceprog
  - openocd

- [![symbiflow/formal Docker image size](https://img.shields.io/docker/image-size/symbiflow/formal/latest?longCache=true&style=flat-square&label=symbiflow%2Fformal&logo=Docker&logoColor=fff)](https://hub.docker.com/r/symbiflow/formal/tags)
  - GHDL
  - ghdl-yosys-plugin
  - graphviz
  - Symbiyosys
  - Yosys
  - z3

## Development

*NOTE: Currently, there is no triggering mechanism set up between different GitHub repositories. All the workflows in this repo are triggered by CRON jobs.*

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
