<p align="center">
  <a title="'doc' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Adoc"><img alt="'doc' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/doc/main?longCache=true&style=flat-square&label=doc&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'base' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Abase"><img alt="'base' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/base/main?longCache=true&style=flat-square&label=base&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
</p>
<p align="center">
  <a title="'ghdl' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Aghdl"><img alt="'ghdl' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/ghdl/main?longCache=true&style=flat-square&label=ghdl&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'gtkwave' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Agtkwave"><img alt="'gtkwave' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/gtkwave/main?longCache=true&style=flat-square&label=gtkwave&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'icestorm' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Aicestorm"><img alt="'icestorm' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/icestorm/main?longCache=true&style=flat-square&label=icestorm&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'nextpnr' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Anextpnr"><img alt="'nextpnr' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/nextpnr/main?longCache=true&style=flat-square&label=nextpnr&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'prjtrellis' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Aprjtrellis"><img alt="'prjtrellis' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/prjtrellis/main?longCache=true&style=flat-square&label=prjtrellis&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
</p>
<p align="center">
  <a title="'symbiyosys' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Asymbiyosys"><img alt="'symbiyosys' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/symbiyosys/main?longCache=true&style=flat-square&label=symbiyosys&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'yosys' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Ayosys"><img alt="'yosys' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/yosys/main?longCache=true&style=flat-square&label=yosys&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'ghdl-yosys-plugin' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Aghdl-yosys-plugin"><img alt="'ghdl-yosys-plugin' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/ghdl-yosys-plugin/main?longCache=true&style=flat-square&label=ghdl-yosys-plugin&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'z3' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Az3"><img alt="'z3' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/z3/main?longCache=true&style=flat-square&label=z3&logo=GitHub%20Actions&logoColor=fff"></a>
</p>
<p align="center">
  <a title="'formal' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Aformal"><img alt="'formal' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/formal/main?longCache=true&style=flat-square&label=formal&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'impl' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Aimpl"><img alt="'impl' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/impl/main?longCache=true&style=flat-square&label=impl&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
  <a title="'prog' workflow Status" href="https://github.com/hdl/containers/actions?query=workflow%3Aprog"><img alt="'prog' workflow Status" src="https://img.shields.io/github/workflow/status/hdl/containers/prog/main?longCache=true&style=flat-square&label=prog&logo=GitHub%20Actions&logoColor=fff"></a><!--
  -->
</p>

This repository contains scripts and GitHub Actions (GHA) YAML workflows for building, testing and deploying OCI images (aka Docker images) including open source EDA tooling. All of them are pushed to [hub.docker.com/u/hdlc](https://hub.docker.com/u/hdlc). See [hdl.github.io/containers](https://hdl.github.io/containers) for further details and contributing guidelines.

- [ ] [bitman](https://github.com/khoapham/bitman)
- [ ] [boolector](https://github.com/boolector/boolector)
- [ ] [cocotb](https://github.com/cocotb/cocotb)
- [ ] [CVC4](https://github.com/CVC4/CVC4)
- [ ] [fujprog](https://github.com/kost/fujprog)
- [x] [ghdl](https://github.com/ghdl/ghdl)
  - [![hdlc/ghdl:latest Docker image size](https://img.shields.io/docker/image-size/hdlc/ghdl/latest?longCache=true&style=flat-square&label=hdlc%2Fghdl&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/ghdl/tags)
  - [![hdlc/pkg:ghdl Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/ghdl?longCache=true&style=flat-square&label=hdlc%2Fpkg:ghdl&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
  - In `hdlc/ghdl:yosys`, `hdlc/impl` and `hdlc/formal`.
- [x] [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)
  - [![hdlc/ghdl:yosys Docker image size](https://img.shields.io/docker/image-size/hdlc/ghdl/yosys?longCache=true&style=flat-square&label=hdlc%2Fghdl:yosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/ghdl/tags)
  - [![hdlc/pkg:ghdl-yosys-plugin Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/ghdl-yosys-plugin?longCache=true&style=flat-square&label=hdlc%2Fpkg:ghdl-yosys-plugin&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
  - In `hdlc/impl` and `hdlc/formal`.
- [x] [graphviz](https://graphviz.org/)
  - In `hdlc/yosys`, `hdlc/ghdl:yosys`, `hdlc/impl` and `hdlc/formal`.
- [x] [gtkwave](https://github.com/gtkwave/gtkwave)
  - [![hdlc/pkg:gtkwave Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/gtkwave?longCache=true&style=flat-square&label=hdlc%2Fpkg:gtkwave&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
- [x] [icestorm](https://github.com/cliffordwolf/icestorm)
  - [![hdlc/icestorm:latest Docker image size](https://img.shields.io/docker/image-size/hdlc/icestorm/latest?longCache=true&style=flat-square&label=hdlc%2Ficestorm&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/icestorm/tags)
  - [![hdlc/pkg:icestorm Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/icestorm?longCache=true&style=flat-square&label=hdlc%2Fpkg:icestorm&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
- [ ] [iverilog](https://github.com/steveicarus/iverilog)
- [ ] [netlistsvg](https://github.com/nturley/netlistsvg)
- [x] [nextpnr](https://github.com/YosysHQ/nextpnr)
  - [![hdlc/nextpnr:latest Docker image size](https://img.shields.io/docker/image-size/hdlc/nextpnr/latest?longCache=true&style=flat-square&label=hdlc%2Fnextpnr&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/nextpnr/tags)
  - [![hdlc/nextpnr:ice40 Docker image size](https://img.shields.io/docker/image-size/hdlc/nextpnr/ice40?longCache=true&style=flat-square&label=hdlc%2Fnextpnr:ice40&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/nextpnr/tags)
  - [![hdlc/nextpnr:ecp5 Docker image size](https://img.shields.io/docker/image-size/hdlc/nextpnr/ecp5?longCache=true&style=flat-square&label=hdlc%2Fnextpnr:ecp5&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/nextpnr/tags)
  - In `hdlc/impl`.
- [ ] [openFPGALoader](https://github.com/trabucayre/openFPGALoader)
- [x] [openocd](http://openocd.org/)
  - In `hdlc/prog`.
- [x] [prjtrellis](https://github.com/hdlc/prjtrellis)
  - [![hdlc/prjtrellis:latest Docker image size](https://img.shields.io/docker/image-size/hdlc/prjtrellis/latest?longCache=true&style=flat-square&label=hdlc%2Fprjtrellis&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/prjtrellis/tags)
  - [![hdlc/pkg:prjtrellis Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/prjtrellis?longCache=true&style=flat-square&label=hdlc%2Fpkg:prjtrellis&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
- [ ] [Super Prove](https://github.com/sterin/super-prove-build)
- [x] [symbiyosys](https://github.com/YosysHQ/SymbiYosys)
  - [![hdlc/pkg:symbiyosys Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/symbiyosys?longCache=true&style=flat-square&label=hdlc%2Fpkg:symbiyosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
  - In `hdlc/formal`.
- [ ] [verilator](https://github.com/verilator/verilator)
- [ ] [vunit](https://github.com/VUnit/vunit)
- [ ] [Yices 2](https://github.com/SRI-CSL/yices2)
- [x] [yosys](https://github.com/YosysHQ/yosys)
  - [![hdlc/yosys:latest Docker image size](https://img.shields.io/docker/image-size/hdlc/yosys/latest?longCache=true&style=flat-square&label=hdlc%2Fyosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/yosys/tags)
  - [![hdlc/pkg:yosys Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/yosys?longCache=true&style=flat-square&label=hdlc%2Fpkg:yosys&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
  - In `hdlc/ghdl:yosys`, `hdlc/impl` and `hdlc/formal`.
- [x] [z3](https://github.com/Z3Prover/z3)
  - [![hdlc/pkg:z3 Docker image size](https://img.shields.io/docker/image-size/hdlc/pkg/z3?longCache=true&style=flat-square&label=hdlc%2Fpkg:z3&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/pkg/tags)
  - In `hdlc/formal`.

## Images including multiple tools

- [![hdlc/prog:latest Docker image size](https://img.shields.io/docker/image-size/hdlc/prog/latest?longCache=true&style=flat-square&label=hdlc%2Fprog&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/prog/tags)
  - iceprog
  - openocd

- [![hdlc/impl Docker image size](https://img.shields.io/docker/image-size/hdlc/impl/latest?longCache=true&style=flat-square&label=hdlc%2Fimpl&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/impl/tags)
  - GHDL
  - ghdl-yosys-plugin
  - graphviz
  - nextpnr
  - yosys

- [![hdlc/formal Docker image size](https://img.shields.io/docker/image-size/hdlc/formal/latest?longCache=true&style=flat-square&label=hdlc%2Fformal&logo=Docker&logoColor=fff)](https://hub.docker.com/r/hdlc/formal/tags)
  - GHDL
  - ghdl-yosys-plugin
  - graphviz
  - symbiyosys
  - yosys
  - z3
