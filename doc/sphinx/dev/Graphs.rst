.. _Development:graphs:

Graphs
######

Understanding how all the pieces in this project fit together might be daunting for newcomers. Fortunately, there is a map for helping maintainers and contributors traveling through the ecosystem. Subdir :ghsrc:`graph/ <graph/>` contains the sources of `directed graphs <https://en.wikipedia.org/wiki/Directed_graph>`__, where the relations between workflows, dockerfiles, images and tests are shown.

(`Graphviz <https://graphviz.org/>`__)'s ``digraph`` format is used, hence, graphs can be rendered to multiple image formats. The SVG output is shown in xref:img-graph[xrefstyle=short] describes which images are created in each map. See the details in the figure corresponding to the name of the subgraph:
Base (xref:img-graph-base[xrefstyle=short]),
Sim (xref:img-graph-sim[xrefstyle=short]),
Synth (xref:img-graph-synth[xrefstyle=short]),
Impl (xref:img-graph-impl[xrefstyle=short]),
Formal (xref:img-graph-formal[xrefstyle=short]),
ASIC (xref:img-graph-asic[xrefstyle=short]), and
SymbiFlow (xref:img-graph-symbiflow[xrefstyle=short]).
Multiple colours and arrow types are used for describing different dependency types. All of those are explained in the legend: xref:img-graph-legend[xrefstyle=short].

.. important::
   These graphs represent a single collection of images (the *virtual* aggregation of others). In practice, some tools might be missing in some collections. For instance, a tool might be available in Debian Buster based containers, but not in CentOS 7. That info is not tracked in the graphs yet. Please, see whether a dockerfile exists in the corresponding subdir.

[#img-graph]
.Subgraphs and images.
[link=../img/graph.svg]
graphviz::../../../graph/graph.dot[format="svg", align="center"]

[#img-graph-base]
.Base: workflows, dockerfiles, images and tests.
[link=../img/base.svg]
graphviz::../../../graph/base.dot[format="svg", align="center"]

[#img-graph-sim]
.Sim: workflows, dockerfiles, images and tests.
[link=../img/sim.svg]
graphviz::../../../graph/sim.dot[format="svg", align="center"]

[#img-graph-synth]
.Synth: workflows, dockerfiles, images and tests.
[link=../img/synth.svg]
graphviz::../../../graph/synth.dot[format="svg", align="center"]

[#img-graph-impl]
.Impl: workflows, dockerfiles, images and tests.
[link=../img/impl.svg]
graphviz::../../../graph/impl.dot[format="svg", align="center"]

[#img-graph-formal]
.Formal: workflows, dockerfiles, images and tests.
[link=../img/formal.svg]
graphviz::../../../graph/formal.dot[format="svg", align="center"]

[#img-graph-asic]
.ASIC: workflows, dockerfiles, images and tests.
[link=../img/asic.svg]
graphviz::../../../graph/asic.dot[format="svg", align="center"]

[#img-graph-symbiflow]
.SymbiFlow: workflows, dockerfiles, images and tests.
[link=../img/symbiflow.svg]
graphviz::../../../graph/symbiflow.dot[format="svg", align="center"]

[#img-graph-legend]
.Legend of the directed graph.
[link=../img/legend.svg]
graphviz::../../../graph/legend.dot[format="svg", align="center"]

.. include:: GraphGeneration.rst
