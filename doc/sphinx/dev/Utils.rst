.. _Development:utils:

Utils
#####

.. important::

   Some helper shell and Python utilities are available in :ghsrc:`utils/bin <utils/bin>` and :ghsrc:`utils/pyHDLC <utils/pyHDLC>`, respectively.
   A :ghsrc:`utils/setup.sh <utils/setup.sh>` script is provided for installing Python dependencies and adding the ``bin`` subdir to the ``PATH``.
   Since ``pip`` is used for installing :ghsrc:`utils/pyHDLC/requirements.txt <utils/pyHDLC/requirements.txt>`, it is desirable to create a virtual environment (`docs.python.org/3/library/venv <https://docs.python.org/3/library/venv.html>`__) before running ``setup.sh``:

  .. code-block:: shell
     
    virtualenv venv
    source venv/bin/activate
    ./utils/setup.sh

.. _Development:build:

Build
=====

``pyHDLC build`` helps building one or multiple images at once, by hiding all common options:

.. code-block:: shell

   usage: pyHDLC build [-h] [-a ARCHITECTURE] [-c COLLECTION] [-r REGISTRY] [-f DOCKERFILE] [-t TARGET] [-a ARGIMG] [-p] [-d] [-q] Image [Image ...]

   positional arguments:
     Image                 image name(s), without registry prefix.
   
   optional arguments:
     -h, --help            show this help message and exit
     -a ARCHITECTURE, --arch ARCHITECTURE
                           name of the architecture.
                           (default: amd64)
     -c COLLECTION, --collection COLLECTION
                           name of the collection/subset of images.
                           (default: debian/bullseye)
     -r REGISTRY, --registry REGISTRY
                           container image registry prefix.
                           (default: gcr.io/hdl-containers)
     -f DOCKERFILE, --dockerfile DOCKERFILE
                           dockerfile to be built, from the collection.
                           (default: None)
     -t TARGET, --target TARGET
                           target stage in the dockerfile.
                           (default: None)
     -i ARGIMG, --argimg ARGIMG
                           base image passed as an ARG to the dockerfile.
                           (default: None)
     -p, --pkg             preprend 'pkg/' to Image and set Target to 'pkg' (if unset).
                           (default: False)
     -d, --default         set default Dockerfile, Target and ArgImg options, given the image name(s).
                           (default: False)
     -q, --test            test each image right after building it.
                           (default: False)

.. important::

   `DOCKERFILE` defaults to `Image` if `None`.

Inspect
=======

All ready-to-use images (coloured [green]#GREEN# or [maroon]#BROWN# in the :ref:`Graphs <Development:graphs>`) are runnable.
Therefore, users/contributors can run containers and test the tools interactively or through scripting.
However, since ``pkg`` images are not runnable, creating another image is required in order to inspect
their content from a container. For instance:

.. code-block:: dockerfile

   FROM busybox
   COPY --from=REGISTRY/pkg/TOOL_NAME /TOOL_NAME /

In fact, ``pyHDLC test`` uses a similar dockerfile for running ``.pkg.sh`` scripts from :ghsrc:`test/ <test/>`.
See :ref:`Test <Development:test>`.

Alternatively, or as a complement, `wagoodman/dive <https://github.com/wagoodman/dive>`__ is a lightweight tool with a nice terminal based GUI for exploring layers and contents of container images.
It can be downloaded as a tarball/zipfile, or used as a container:

.. code-block:: bash

   docker run --rm -it \
     -v //var/run/docker.sock://var/run/docker.sock \
     wagoodman/dive \
     REGISTRY/[ARCHITECTURE/][COLLECTION/]IMAGE[:TAG]

[#img-dive]
.Inspection of `REGISTRY/pkg/yosys` with https://github.com/wagoodman/dive[wagoodman/dive].
[link=img/dive.png]
image::dive.png[wagoodman/dive, align="center"]

:ghsrc:`dockerDive <utils/bin/dockerDive>` is a wrapper around the wagoodman/dive container, which supports one
or two arguments for specifying the image to be inspected.
The default registry prefix is ``gcr.io/hdl-containers``, however, it can be overriden through envvar ``HDL_REGISTRY``.

For instance, inspect image ``gcr.io/hdl-containers/debian/bullseye/ghdl``:

.. code-block:: bash

   dockerDive debian/bullseye ghdl

or, inspect any image from any registry:

.. code-block:: bash

   HDL_REGISTRY=docker.io dockerDive python:slim-bullseye

.. _Development:test:

Test
====

There is a test script in :ghsrc:`test/ <test/>` for each image in this ecosystem, according to the following convention:

*  Scripts for package images, ``/[ARCHITECTURE/][COLLECTION/]pkg/TOOL_NAME[/SUBNAME]``, are named ``TOOL_NAME[--SUBNAME].pkg.sh``.
*  Scripts for other images, ``/[ARCHITECTURE/][COLLECTION/]NAME[/SUBNAME]``, are named ``NAME[--SUBNAME].sh``.
*  Other helper scripts are named ``_*.sh``.

Furthermore, `hdl/smoke-test <https://github.com/hdl/smoke-tests>`__ is a submodule of this repository (:ghsrc:`test/smoke-test <test>`). Smoke-tests contains fine grained tests that cover the most important functionalities of the tools. Those are used in other packaging projects too. Therefore, container tests are expected to execute the smoke-tests corresponding to the tools available in the image, before executing more specific tests.

``pyHDLC test`` allows testing the runnable and package images.

It is used in CI but can be useful locally too:

.. code-block:: shell

   usage: pyHDLC test [-h] [-a ARCHITECTURE] [-c COLLECTION] [-r REGISTRY] Image[#<DirName>] [Image[#<DirName>] ...]
   
   positional arguments:
     Image                 image name(s), without registry prefix.
   
   optional arguments:
     -h, --help            show this help message and exit
     -a ARCHITECTURE, --arch ARCHITECTURE
                           name of the architecture.
                           (default: amd64)
     -c COLLECTION, --collection COLLECTION
                           name of the collection/subset of images.
                           (default: debian/bullseye)
     -r REGISTRY, --registry REGISTRY
                           container image registry prefix.
                           (default: gcr.io/hdl-containers)

.. important::

   ``DirName`` allows to optionally specify the name of the directory inside the package image which needs to be copied 
   to the temporary image for testing.
   By default, the escaped name of the image is used as the location.
   Therefore, ``DirName`` is used exceptionally.
