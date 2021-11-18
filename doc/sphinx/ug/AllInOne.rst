.. AllInOne:

All-in-one images
#################

.. note::
   These images are coloured [maroon]#BROWN# in the link:../dev/index.html#_graphs[Graphs].

Multiple tools from fine-grained images are included in larger images for common use cases. These are named ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]MAIN_USAGE``. This is the recommended approach for users who are less familiar with containers and want a quick replacement for full-featured virtual machines. Coherently, some common Unix tools (such as make or cmake) are also included in these all-in-one imags.

* `tmeissner/formal_hw_verification <https://github.com/tmeissner/formal_hw_verification>`__: the CI workflow uses image ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]formal/all`` along with GitHub's 'Docker Action' syntax (see `docs.github.com: Learn GitHub Actions > Referencing a container on Docker Hub <https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/finding-and-customizing-actions#referencing-a-container-on-docker-hub>`__).
* `stnolting/neorv32 <https://github.com/stnolting/neorv32>`__: the implementation workflow (for generating bitstreams from VHDL sources) uses image ``REGISTRY_PREFIX/[ARCHITECTURE/][COLLECTION/]impl`` along with GitHub's 'Docker Action' syntax (see `docs.github.com: Learn GitHub Actions > Referencing a container on Docker Hub <https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/finding-and-customizing-actions#referencing-a-container-on-docker-hub>`__).
