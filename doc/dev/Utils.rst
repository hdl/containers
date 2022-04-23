.. _Development:utils:

Utils
#####

.. toctree::
  :hidden:

  pyHDLC_Reference

Some helper shell and Python utilities are available in :ghsrc:`utils/bin <utils/bin>` and
:ghsrc:`utils/pyHDLC <utils/pyHDLC>`, respectively.
A :ghsrc:`utils/setup.sh <utils/setup.sh>` script is provided for installing Python dependencies and adding the ``bin``
subdir to the ``PATH``.
Since ``pip`` is used for installing :ghsrc:`utils/pyHDLC/requirements.txt <utils/pyHDLC/requirements.txt>`, it is
desirable to create a virtual environment (`docs.python.org/3/library/venv <https://docs.python.org/3/library/venv.html>`__)
before running ``setup.sh``:

.. sourcecode:: shell

  virtualenv venv
  source venv/bin/activate
  ./utils/setup.sh

.. _Development:utils:pyHDLC:

.. autoprogram:: pyHDLC.cli:CLI().MainParser
  :prog: pyHDLC
  :groups:


.. _Development:test:

Smoke-tests
===========

There is a test script in :ghsrc:`test/ <test/>` for each image in this ecosystem, according to the following
convention:

* Scripts for package images, ``/[ARCHITECTURE/][COLLECTION/]pkg/TOOL_NAME[/SUBNAME]``, are named
  ``TOOL_NAME[--SUBNAME].pkg.sh``.

* Scripts for other images, ``/[ARCHITECTURE/][COLLECTION/]NAME[/SUBNAME]``, are named ``NAME[--SUBNAME].sh``.

* Other helper scripts are named ``_*.sh``.

Furthermore, :gh:`hdl/smoke-tests` is a submodule of this repository (:ghsrc:`test/smoke-tests <test>`).
Smoke-tests contains fine-grained tests that cover the most important functionalities of the tools.
Those are used in other packaging projects too.
Therefore, container tests are expected to execute the smoke-tests corresponding to the tools available in the image,
before executing more specific tests.

``pyHDLC test`` allows testing the runnable and package images.
It is used in CI but can be useful locally too.
When using `pyHDLC test`, ``DirName`` allows to optionally specify the name of the directory inside the package image
which needs to be copied to the temporary image for testing.
By default, the escaped name of the image is used as the location.


.. _Development:inspect:

Inspect
=======

.. role:: green

.. role:: maroon

All ready-to-use images (coloured :green:`GREEN` or :maroon:`BROWN` in the :ref:`Graphs <Development:graphs>`) are
runnable.
Therefore, users/contributors can run containers and test the tools interactively or through scripting.
However, since ``pkg`` images are not runnable, creating another image is required in order to inspect their content
from a container.
For instance:

.. sourcecode:: dockerfile

   FROM busybox
   COPY --from=REGISTRY/pkg/TOOL_NAME /TOOL_NAME /

In fact, ``pyHDLC test`` uses a similar dockerfile for running ``.pkg.sh`` scripts from :ghsrc:`test/ <test/>`.
See :ref:`Test <Development:test>`.

Alternatively, or as a complement, :gh:`wagoodman/dive` is a lightweight tool with a nice terminal based GUI for
exploring layers and contents of container images.
It can be downloaded as a tarball/zipfile, or used as a container:

.. sourcecode:: bash

   docker run --rm -it \
     -v //var/run/docker.sock://var/run/docker.sock \
     wagoodman/dive \
     REGISTRY/[ARCHITECTURE/][COLLECTION/]IMAGE[:TAG]

.. figure:: ../_static/img/dive.png
  :alt: gh:wagoodman/dive
  :width: 100%
  :align: center

  Inspection of ``REGISTRY/pkg/yosys`` with :gh:`wagoodman/dive`.

:ghsrc:`dockerDive <utils/bin/dockerDive>` is a wrapper around the wagoodman/dive container, which supports one
or two arguments for specifying the image to be inspected.
The default registry prefix is ``gcr.io/hdl-containers``, however, it can be overriden through envvar ``HDL_REGISTRY``.

For instance, inspect image ``gcr.io/hdl-containers/debian/bullseye/ghdl``:

.. sourcecode:: bash

   dockerDive debian/bullseye ghdl

or, inspect any image from any registry:

.. sourcecode:: bash

   HDL_REGISTRY=docker.io dockerDive python:slim-bullseye


.. _Development:configuration:

YAML Configuration File
=======================

Most of the complexity regarding images, dockerfiles, arguments and jobs is defined in the YAML configuration file
(see :ghsrc:`config.yml <utils/pyHDLC/config.yml>`), which contains two data fields:

* **defaults**: which dockerfile and (optionally) target stage or base image to be used when building "non-regular" images.
  That is, using a non-empty target, an specific base image, etc.
  If the image name is not defined in this field, the dockerfile defaults to the image name and the target depends on
  option *package*.
* **jobs**: which images and for which collections and architectures to build each list of tasks.
  For convenienve, the keywords match the name of the main tool/group in the list.

.. TIP::
  Contributors will find that field **anchors** in :ghsrc:`config.yml <utils/pyHDLC/config.yml>` is ignored by pyHDLC
  commands when analyzing the file.
  That's because anchors are used to reduce the verbosity of the YAML file, but they are resolved by the loader.

  * `yaml.org <https://yaml.org>`__
  * `blog.daemonl.com: YAML - Anchors, References, Extend <https://blog.daemonl.com/2016/02/yaml.html>`__

The fields and types supported in the configuration file are defined through dataclasses (see :ref:`Development:utils:pyHDLC:Reference:Dataclasses`).
However, some details about the syntax can be non-obvious.
See the clarifications below:

.. _Development:configuration:defaults:

Defaults
--------

If the following conditions are met, images need not to be explicitly listed in the configuration file:

* The dockerfile to be used matches the image name.
* The default target is empty, or ``pkg`` if a package image is being built.
* The ``argimg`` is empty.

Otherwise, a dictionary is expected, with the fields that need to be overriden (``dockerfile``, ``target`` and/or
``argimg``).

.. _Development:configuration:jobs:

Jobs
----

There are four kinds of job lists:

* **default**: two images are built for each collection and architecture, a regular image and a package image.
* **pkgonly**: a package image is built for each collection and architecture.
* **runonly**: a regular image is built for each collection and architecture.
* **custom**: the lists of jobs/tasks are declared as cross-products, and ``exclude`` is supported.

In **default**, **pkgonly** and **runonly**, a dictionary of lists is expected per keyword; each key corresponding to a
collection and the lists specifying the architectures.
Conversely, in **custom** three fields are expected:

* **sys**: a dictionary of lists, such as the one expected in **default**, **pkgonly** and **runonly**.

* **images**: either a list or a list of lists of image names.

  * If a single list is provided, all images are built sequentially in a single job:

    .. sourcecode:: yaml

      images:
        - formal/min
        - formal
        - formal/all

    If a list of lists is provided, each of them is built sequentially in a different job:

    .. sourcecode:: yaml

      images:
        - [ conda/f4pga/xc7/a50t  ]
        - [ conda/f4pga/xc7/a100t ]
        - [ conda/f4pga/xc7/a200t ]

  * Argument substitution is supported through ``${arg}``.
    If any of the items in the list is a dictionary, instead of a string, it is used as an argument in the substitution
    phase.
    If the same argument is provided multiple times, a cross-product of the arguments and the lists is produced:

    .. sourcecode:: yaml

      images:
        - sim/${prj}-slim
        - sim/${prj}
        - prj: scipy
        - prj: octave

    .. sourcecode:: yaml

      images:
        - pkg/nextpnr/${arch}
        - nextpnr/${arch}
        - nextpnr/${prj}
        - { arch: ice40, prj: icestorm   }
        - { arch: ecp5,  prj: prjtrellis }

* **exclude**: optionally, declare combinations of *sys* and *images* which should be excluded from the produced
  cross-products.
  For example:

  .. sourcecode:: yaml

      images:
        - pkg/nextpnr/${arch}
        - nextpnr/${arch}
        - nextpnr/${prj}
        - { arch: ecp5,  prj: prjtrellis }
        - { arch: nexus, prj: prjoxide   }
      sys: *SysDebianAmd64
      exclude:
        - sys: { debian/buster: [amd64] }
          params: { arch: nexus, prj: prjoxide }
