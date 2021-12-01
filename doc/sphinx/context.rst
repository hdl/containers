.. _context:

Context
#######

This project started in GitHub repository `ghdl/ghdl <https://github.com/ghdl/ghdl>`__ (which was named tgingold/ghdl back then). The main purpose was testing GHDL on multiple GNU/Linux distributions (Debian, Ubuntu and Fedora), since `Travis CI <https://travis-ci.org/>`__ supported Ubuntu only and Docker. For each target platform, two images were used, one for building and another one for testing.

Later, most of the Docker related sources were split to repository `ghdl/docker <https://github.com/ghdl/docker>`__. There, some additional simulation tools were added, such as `VUnit <http://vunit.github.io/>`__ and `GtkWave <http://gtkwave.sourceforge.net/>`__. Images including the `ghdl-language-server <https://github.com/ghdl/ghdl-language-server>`__ were also added. When synthesis features were added to GHDL, and since it provides a plugin for `Yosys <https://github.com/YosysHQ/yosys>`__, tools for providing a complete open source workflow were requested. Those were `nextpnr <https://github.com/YosysHQ/nextpnr>`__, `icestorm <https://github.com/YosysHQ/icestorm>`__, `prjtrellis <https://github.com/YosysHQ/prjtrellis>`__, `SymbiYosys <https://github.com/YosysHQ/SymbiYosys>`__, etc.

At some point, ghdl/docker had as much content related to non-GHDL tools, as resources related to the organisation. At the same time, `SymbiFlow <https://symbiflow.github.io>`__ aimed at gathering open source projects for providing an integrated open source EDA solution. However, it did not have official container images and `help was wanted <https://symbiflow.github.io/developers.html>`__. This repository was initially created for moving all the tools which were not part of GHDL, from ghdl/docker to symbiflow/containers. However, apart from adding known Verilog tools, the scope was widened. Hence, the repository was published in `hdl/containers <https://github.com/hdl/containers>`__.
