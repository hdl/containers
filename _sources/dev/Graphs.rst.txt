.. _Development:graphs:

Graphs
######

Understanding how all the pieces in this project fit together might be daunting for newcomers.
Fortunately, there is a map for helping maintainers and contributors traveling through the ecosystem.
Subdir :ghsrc:`doc/graph/ <doc/graph/>` contains the sources of :wikipedia:`directed graphs <Directed_graph>`, where the
relations between workflows, dockerfiles, images and tests are shown.

(`Graphviz <https://graphviz.org/>`__)'s ``digraph`` format is used, hence, graphs can be rendered to multiple image
formats.
The output shown in :numref:`img-graph` describes which images are created in each map.
See the details in the figure corresponding to the name of the subgraph:
Base (:numref:`img-graph-base`),
Sim (:numref:`img-graph-sim`),
Synth (:numref:`img-graph-synth`),
Impl (:numref:`img-graph-impl`),
Formal (:numref:`img-graph-formal`),
ASIC (:numref:`img-graph-asic`), and
F4PGA (:numref:`img-graph-f4pga`).
Multiple colours and arrow types are used for describing different dependency types.
All of those are explained in the legend: :numref:`img-graph-legend`.

.. IMPORTANT::
   These graphs represent a single collection of images (the *virtual* aggregation of others).
   In practice, some tools might be missing in some collections.
   For instance, a tool might be available in Debian Buster based containers, but not in CentOS 7.
   That info is not tracked in the graphs yet.
   Please, see whether a dockerfile exists in the corresponding subdir.

.. graphviz:: ../graph/graph.dot
   :name: img-graph
   :align: center
   :caption: Subgraphs and images

.. graphviz:: ../graph/base.dot
   :name: img-graph-base
   :align: center
   :caption: Base: workflows, dockerfiles, images and tests.

.. graphviz:: ../graph/sim.dot
   :name: img-graph-sim
   :align: center
   :caption: Sim: workflows, dockerfiles, images and tests.

.. graphviz:: ../graph/synth.dot
   :name: img-graph-synth
   :align: center
   :caption: Synth: workflows, dockerfiles, images and tests.

.. graphviz:: ../graph/impl.dot
   :name: img-graph-impl
   :align: center
   :caption: Impl: workflows, dockerfiles, images and tests.

.. graphviz:: ../graph/formal.dot
   :name: img-graph-formal
   :align: center
   :caption: Formal: workflows, dockerfiles, images and tests.

.. graphviz:: ../graph/asic.dot
   :name: img-graph-asic
   :align: center
   :caption: ASIC: workflows, dockerfiles, images and tests.

.. graphviz:: ../graph/f4pga.dot
   :name: img-graph-f4pga
   :align: center
   :caption: F4PGA: workflows, dockerfiles, images and tests.

.. graphviz:: ../graph/legend.dot
   :name: img-graph-legend
   :align: center
   :caption: Legend of the directed graph.

.. toctree::
  :hidden:

  GraphGeneration
