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

* |SHIELD:Image:build/base| Debian Buster, Debian Bullseye or CentOS 7, with updated ``ca-certificates``, ``curl`` and
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
   `issues <https://github.com/hdl/containers/issues>`__
   and `pull requests <https://github.com/hdl/containers/pulls>`__;
   `open an issue <https://github.com/hdl/containers/issues/new>`__
   or `let us know through the chat <https://gitter.im/hdl/community>`__.
   Someone might be working on that already!

.. NOTE::
   Currently, many projects don't use containers at all, hence, all images are generated in this repository.
   However, the workload is expected to be distributed between multiple projects in the ecosystem.


Step by step checklist
======================

.. role:: maroon

1. Create or update dockerfile(s).

  * For each tool and collection, a `Dockerfile <https://docs.docker.com/engine/reference/builder/>`__ recipe exists.

     * Optionally, add tools to multiple collections at the same time.
       That is, create one dockerfile for each collection.

     * All dockerfiles must use, at least, two stages:

        * One stage, named ``build``, is to be based on ``$REGISTRY/build/base`` or ``$REGISTRY/build/build`` or
          ``$REGISTRY/build/dev``.
          In this first stage, you need to add the missing build dependencies.
          Then, build the tool/project using the standard ``PREFIX``, but install to a custom location using ``DESTDIR``.
          See :ref:`Package images <Development:package-images>`.

        * If the tool/project is to be used standalone, create an stage based on ``$REGISTRY/build/base``.
          Install runtime dependencies only.

        * If the tool/project is to be packaged, create an stage based on ``scratch``.

        * In any case, copy the tool artifacts from the build stage using ``COPY --from=STAGE_NAME``.

        * In practice, several dockerfiles produce at least one package image and one ready-to-use image.
          Therefore, dockerfiles will likely have more than two stages.

  * Some tools are to be added to existing images which include several tools (coloured :maroon:`BROWN` in the
    :ref:`Graphs <Development:graphs>`).
    After creating the dockerfile where the corresponding package image is defined, add
    ``COPY --from=$REGISTRY/pkg/TOOL_NAME`` statements to the dockerfiles of multi-tool images.

2. Build and test the dockerfile(s) locally.
   Use helper scripts from :ghsrc:`utils <utils>`, as explained in :ref:`Build <Development:build>` and
   :ref:`Test <Development:test>`.

  * If a new tool was added, or a new image is to be generated, a test script needs to be added to :ghsrc:`test/ <test/>`.
    See :ref:`Test <Development:test>` for naming guidelines.

  * Be careful with the order.
    If you add a new tool and include it in one of the multi-tool images, the package image needs to be built first.

3. Create or update workflow(s).

  * For each tool or multi-tool image, a GitHub Actions workflow is added to :ghsrc:`.github/workflows <.github/workflows/>`.
    Find documentation at `Workflow syntax for GitHub Actions <https://docs.github.com/en/free-pro-team@latest/actions/reference/workflow-syntax-for-github-actions>`__.
    Copying some of the existing workflows in this repo and adapting it is suggested.

  * In each workflow, all the images produced from stages of the corresponding dockerfile are built, tested and pushed.
    Scripts from :ghsrc:`utils <utils>` are used.

  * The workflow matrix is used for deciding which collections is each tool to be built for.

4. Update the documentation.

  * If a new tool was added,

     * Ensure that the tool is listed at `hdl/awesome <https://github.com/hdl/awesome>`__, since that's where all the
       tool/projects in the table point to.

     * If a tool from the *To Do* list was added, remove it from the list.

     * Add a shield/badge to the table in :ref:`Continuous Integration (CI) <Development:continous-integration>`.

  * Edit :ghsrc:`doc/tools.yml <doc/tools.yml>`.
    The table in :ref:`Tools and images <tools-and-images>` is autogenerated from that YAML file.

  * Update the :ref:`Graphs <Development:graphs>`.
