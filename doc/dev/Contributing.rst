.. _Development:contributing:

Contributing
############

As explained in :ref:`Tools and images <tools-and-images>` and in the :ref:`User Guide <UserGuide>`,
multiple collections of images are provided.
For each collection, a set of base images is provided, which are to be used for building and for runtime.
These are defined in ``base.dockerfile``.
See, for instance, :ghsrc:`debian-bullseye/base.dockerfile <debian-bullseye/base.dockerfile>`.
All the images in the ecosystem are based on these:

.. include:: ../shields/shields.build.gen.inc

* |SHIELD:Image:build/base| Debian Bullseye or Rocky Linux 8, with updated ``ca-certificates``, ``curl`` and
  Python 3.

* |SHIELD:Image:build/build| based on ``base``, includes ``clang`` and ``make``.

* |SHIELD:Image:build/dev| based on ``build``, includes ``cmake``, ``libboost-all-dev`` and ``python3-dev``.

Then, for each project/tool there are dockerfiles (one for each collection), a GitHub Actions workflow, and one or more
test scripts.
Those are used for:

* Tools are built using ``REGISTRY/[ARCHITECTURE/][COLLECTION/]build`` images.

* Package images based on ``scratch`` (and/or other reusable packages) are produced.

* Ready-to-use images based on the runtime base image (``REGISTRY/[ARCHITECTURE/][COLLECTION/]build/base``) are produced.

* Ready-to-use images are tested before uploading.

The :ref:`Package images <Development:package-images>` created in some dockerfiles/workflows are based on ``scratch``
and contain pre-built assets.
Therefore, they are not really useful *per se*, but meant to be used for building other.
In fact, multiple tools are merged into ready-to-use images for common use cases (such as ``impl``,
``formal`` or ``prog``).

.. IMPORTANT::
   Before working on adding or extending the support for a tool, please check the
   :gh:`issues <hdl/containers/issues>` and :gh:`pull requests <hdl/containers/pulls>`;
   :gh:`open an issue <hdl/containers/issues/new>`
   or `let us know through the chat <https://gitter.im/hdl/community>`__.
   Someone might be working on that already!

.. NOTE::
   Currently, many projects don't use containers at all, hence, all images are generated in this repository.
   However, the workload is expected to be distributed between multiple projects in the ecosystem.


.. _Development:contributing:Dockerfiles:

Dockerfiles
===========

Two kinds of `Dockerfile <https://docs.docker.com/engine/reference/builder/>`__ definitions are supported by the utils
used in this repository: single-file solutions, or aided by additional assets.
Nonetheless, all dockerfiles use, at least, two or three stages:

* A global argument named ``REGISTRY`` defines the default registry path and collection to be used.

* One stage, named ``build``, based on ``$REGISTRY/build/base`` or ``$REGISTRY/build/build`` or ``$REGISTRY/build/dev``,
  is used to (optionally) install build dependencies, and to actually build the tool.

  * The tool/project is built using the standard ``PREFIX``, but installed to a custom location using ``DESTDIR``.
    See :ref:`Package images <Development:package-images>`.

* If the tool/project is to be packaged, one stage based on image ``scratch`` is named ``pkg`` and it contains the
  artifacts of the build stage only.

  * Tool artifacts are copied from the build stage using ``COPY --from=STAGE_NAME``.

* If the tool/project is to be used standalone, a final stage based on image ``$REGISTRY/build/base`` is used to
  (optionally) install runtime dependencies, to copy the build artifacts from the build stage, and to (optionally) set
  the default command for the image.

.. NOTE::
  In some dockerfiles, global argument ``IMAGE`` is used to compose stages on top of multiple intermediate images.


.. _Development:contributing:Dockerfiles:single-file:

Single-file example
-------------------

Some tools are defined in a dockerfile only, without any additional assets.
In those cases, the dockerfile is named after the name of the main tool/image built there.

.. sourcecode:: dockerfile
  :caption: Reference Dockerfile to build a TOOL and generate a regular image and a package image.

  ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

  #--

  FROM $REGISTRY/build/build AS build

  RUN apt-get update -qq \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
      ... \
   && apt-get autoclean && apt-get clean && apt-get -y autoremove \
   && rm -rf /var/lib/apt/lists/*

  RUN git clone REPOSITORY_URL /tmp/TOOL \
   && cd /tmp/TOOL \
   && ./configure \
   && make -j$(nproc) \
   && make DESTDIR=/opt/TOOL install

  #---

  FROM scratch AS pkg
  COPY --from=build /opt/TOOL /TOOL

  #---

  FROM $REGISTRY/build/base

  RUN apt-get update -qq \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
      ... \
   && apt-get autoclean && apt-get clean && apt-get -y autoremove \
   && rm -rf /var/lib/apt/lists/*

  COPY --from=build /opt/TOOL /
  CMD ["TOOL"]

.. NOTE::
  Typically, stage ``pkg`` is used as a target to build a package image, and the dockerfile is used without a target in
  order to build the regular image for the tool.
  However, some tools/groups require additional stages, and some other don't have the package or the regular stage.


.. _Development:contributing:Dockerfiles:with-assets:

Example with HDLC script
------------------------

On the other hand, the dockerfiles to build tools with additional assets are named ``Dockerfile`` and located in a
subdir under the collection directory, named after the name of the main tool/image built there.
Those are typically used along with a shell script named ``HDLC``.
The structure of these dockerfiles is similar to the :ref:`Development:contributing:Dockerfiles:single-file`, however,
BuilKit's ``--mount`` feature is used to source a helper script (``HDLC``) without creating additional stages/steps (see
:ref:`Development:contributing:BuildKit`).
A similar strategy can be used to run or copy additional assets into the images.

.. sourcecode:: bash
  :caption: Reference HDLC script to decouple dependency lists and build steps from the Dockerfile.

  makedepends=(
    ...
  )

  build() {
    mkdir /tmp/TOOL
    cd /tmp/TOOL
    git clone REPOSITORY_URL ./
    ./configure
    make -j$(nproc)
    make DESTDIR=/opt/TOOL install
  }

  depends=(
    ...
  )

.. NOTE::
  The default shell in the collections used in this repository is set to ``bash``.
  Therefore, arrays and other bash extensions are supported in these scripts.

.. sourcecode:: dockerfile
  :caption:
    Reference Dockerfile to build a TOOL and generate a regular image and a package image, using an HDLC script and
    BuildKit mount features.

  ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

  #---

  FROM $REGISTRY/build/build AS build

  RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
   && mkdir -p /usr/share/man/man1/ \
   && apt-get update -qq \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${makedepends[@]} \
   && apt-get autoclean && apt-get clean && apt-get -y autoremove \
   && update-ca-certificates \
   && rm -rf /var/lib/apt/lists/*

  RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build

  #---

  FROM scratch AS pkg
  COPY --from=build /opt/TOOL /TOOL

  #---

  FROM $REGISTRY/build/base

  RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
   && apt-get update -qq \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${depends[@]} \
   && apt-get autoclean && apt-get clean && apt-get -y autoremove \
   && rm -rf /var/lib/apt/lists/*

  COPY --from=build /opt/TOOL /
  CMD ["TOOL"]


.. _Development:contributing:BuildKit:

BuildKit
========

The usage of dockerfiles in this repository relies on the image build engine making an analysis and pruning of the stages.
Furthermore, option ``--mount`` used in some of the dockerfiles requires `docs.docker.com: BuildKit <https://docs.docker.com/go/buildkit/>`__.
Therefore, enabling BuildKit is required in order to build the images.

Depending on the version of Docker on your host or CI service, BuildKit features might need to be enabled explicitly.
As explained in `docs.docker.com: To enable BuildKit builds <https://docs.docker.com/develop/develop-images/build_enhancements/#to-enable-buildkit-builds>`__, either set the ``DOCKER_BUILDKIT=1`` environment variable, or set the daemon feature to
``true`` in the JSON configuration file: (``{ "features": { "buildkit": true } }``).

Find further details about BuildKit's mount syntax in :gh:`moby/buildkit: frontend/dockerfile/docs/syntax.md <moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md>`.

* :gh:`bind <moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#run---mounttypebind-the-default-mount-type>`
* :gh:`cache <moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#run---mounttypecache>`
* :gh:`tmpfs <moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#run---mounttypetmpfs>`
* :gh:`secret <moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#run---mounttypesecret>`
* :gh:`ssh <moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#run---mounttypessh>`
* :gh:`here-documents <moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#here-documents>`

.. NOTE::
  In order to use those features, apart from using BuildKit ``# syntax=docker/dockerfile:1.3`` might need to be added as
  the first line of the Dockerfile.
  That depends on the version of Docker.
  Recent versions should not require it.

.. _Development:contributing:checklist:

Step by step checklist
======================

.. role:: maroon

1. Create or update dockerfile(s).

  * For each tool and collection, a Dockerfile recipe exists.
    Find details about the requirements when writing dockerfiles in :ref:`Development:contributing:Dockerfiles`.

     * Optionally, add tools to multiple collections at the same time.
       That is, create one dockerfile for each collection.

  * Some tools are to be added to existing images which include several tools (coloured :maroon:`BROWN` in the
    :ref:`Graphs <Development:graphs>`).
    After creating the dockerfile where the corresponding package image is defined, add
    ``COPY --from=$REGISTRY/pkg/TOOL_NAME`` statements to the dockerfiles of multi-tool images.

2. Build and test the dockerfile(s) locally.
   Use helper scripts from subdir :ghsrc:`utils/`, as explained in :ref:`Development:utils`.

  * If a new tool was added, or a new image is to be generated, a test script needs to be added to :ghsrc:`test/`.
    See :ref:`Development:test` for naming guidelines.

  * Be careful with the order.
    If you add a new tool and include it in one of the multi-tool images, the package image needs to be built first.

3. Create or update workflow(s).

  * For each tool or multi-tool image, a GitHub Actions workflow is added to :ghsrc:`.github/workflows <.github/workflows/>`.
    In each workflow, multiple images produced from stages of the corresponding dockerfile are built, tested and pushed.
    Scripts from :ghsrc:`utils/` are used.
    Find details at :ref:`Development:continous-integration:structure`.

      * Copying some of the existing workflows in this repo and adapting it is suggested.

      * If necessary, update the :ghsrc:`config.yml <utils/pyHDLC/config.yml>` to override the defaults or to define new
        job/task lists.

4. Update the documentation.

  * If a new tool was added,

     * Ensure that the tool is listed at :gh:`hdl/awesome`, since that's where all the tool/projects in
       :ref:`tools-and-images` point to.

     * If a tool from the :ref:`tools-and-images:to-do` list was added, remove it from the list.

     * Add a shield/badge to :ref:`Continuous Integration (CI) » Status <Development:continous-integration:status>` by
       editing variable ``CIWorkflows`` in :ghsrc:`doc/conf.py`.

  * Edit :ghsrc:`doc/tools.yml <doc/tools.yml>`.
    The table in :ref:`Tools and images <tools-and-images>` is autogenerated from that YAML file.

  * Update the :ref:`Graphs <Development:graphs>` in :ghsrc:`doc/graph/`.
