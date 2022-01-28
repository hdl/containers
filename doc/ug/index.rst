.. _UserGuide:

Introduction
############


.. important::
   Image names and tags in this documentation are provided without the *registry prefix*.
   Hence, ``REGISTRY/[ARCHITECTURE/][COLLECTION/]*`` needs to be prefixed to the image names shown in :ref:`tools-and-images`.

Official guidelines and recommendations for using containers suggest keeping them small and specific for each tool/purpose
(see `docs.docker.com: Best practices for writing Dockerfiles <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/>`__).
That fits well with the field of web *microservices*, which communicate through TCP/IP and which need to be composed,
scaled and balanced all around the globe.

However, tooling in other camps is expected to communicate using a shared or local filesystem and/or pipes; therefore,
many users treat containters as *lightweight virtual machines*.
That is, they put all the tools in a single (heavy) container.
Those containers are typically not moved around as frequently as *microservices*, but cached on developers' workstations.

In this project, both paradigms are supported; fine-grained images are available, as well as all-in-one images.

.. note::
   ``hdl`` examples in :gh:`im-tomu/fomu-workshop` showcase a Makefile based solution that supports both strategies:
   the fine-grained pulling and the all-in-one approach.
   An environment variable (``CONTAINER_ENGINE``) is used for selecting which approach to use.
   For didactic purposes, both of them are used in Continuous Integration (CI).
   See :gh:`im-tomu/fomu-workshop: .github/workflows/test.yml <im-tomu/fomu-workshop/blob/master/.github/workflows/test.yml>`.

