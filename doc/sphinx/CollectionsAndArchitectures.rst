.. _colections:

Collections and architectures
#############################

Images are organised in *_collections_* and built for multiple architectures.
A *_collection_* is a set of images which share a common ancestor; a base layer.
Having images with a common ancestor allows reducing bandwidth and disk usage when pulling several of them.
See `docs.docker.com: About storage drivers | Images and layers <https://docs.docker.com/storage/storagedriver/#images-and-layers>`__

Collections:

* ``debian/bullseye`` based on ``ARCHITECTURE/debian:bullseye-slim`` (default)
* ``debian/buster`` based on ``ARCHITECTURE/debian:buster-slim``
* ``centos/7`` based on ``ARCHITECTURE/centos:7``

Architectures:

* `amd64 <https://hub.docker.com/u/amd64>`__
* `arm32v7 <https://hub.docker.com/u/arm32v7>`__
* `arm64v8 <https://hub.docker.com/u/arm64v8>`__
* `ppc64le <https://hub.docker.com/u/ppc64le>`__
* `s390x <https://hub.docker.com/u/s390x>`__
* `mips64le <https://hub.docker.com/u/mips64le>`__
* `riscv64 <https://hub.docker.com/u/riscv64>`__

Each image is published to
.. |SHIELD:WorkflowTest| image: https://img.shields.io/badge/-gcr.io/hdl--containers/&#91;ARCHITECTURE/&#93;&#91;COLLECTION/&#93;IMAGE-555555.svg?longCache=true&style=flat-square&logo=Google%20Cloud&logoColor=f2f1ef
   :alt:
   :height: 22
   :target: 
and
.. |SHIELD:WorkflowTest| image: https://img.shields.io/badge/-ghcr.io/hdl/&#91;ARCHITECTURE/&#93;&#91;COLLECTION/&#93;IMAGE-555555.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef
   :alt:
   :height: 22
   :target: 

However, the ``ARCHITECURE`` and ``COLLECTION`` are optional because:

* Images for the default architecture are mirrored to image:https://img.shields.io/badge/-gcr.io/hdl--containers/COLLECTION/IMAGE-555555.svg?longCache=true&style=flat-square&logo=Google%20Cloud&logoColor=f2f1ef[] and image:https://img.shields.io/badge/-ghcr.io/hdl/COLLECTION/IMAGE-555555.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[].
* Images of the default collection are mirrored to image:https://img.shields.io/badge/-gcr.io/hdl--containers/ARCHITECTURE/IMAGE-555555.svg?longCache=true&style=flat-square&logo=Google%20Cloud&logoColor=f2f1ef[] and image:https://img.shields.io/badge/-ghcr.io/hdl/ARCHITECTURE/IMAGE-555555.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[].
* Images of the default collection for the default architecture are mirrored to https://hub.docker.com/u/hdlc[image:https://img.shields.io/badge/-docker.io/hdlc-555555.svg?longCache=true&style=flat-square&logo=Docker&logoColor=f2f1ef[title='Docker Hub']].
* Images of the default collection for the default architecture which are not ``build`` or ``pkg`` are mirrored to image:https://img.shields.io/badge/-gcr.io/hdl--containers/IMAGE-555555.svg?longCache=true&style=flat-square&logo=Google%20Cloud&logoColor=f2f1ef[] and image:https://img.shields.io/badge/-ghcr.io/hdl/IMAGE-555555.svg?longCache=true&style=flat-square&logo=GitHub&logoColor=f2f1ef[].

.. important::
   Image names and tags in this documentation are provided without the *registry prefix*.
   Hence, one of the prefixes listed above needs to be used when actually pulling/using the images.
   See :ref:`User Guide <UserGuide>` for further details.

.. important::
   The table below shows the tools available in the default collection for the default architecture.
   Some tools are available in a subset of collections or for a subset of architectures only.
   Browse the registries and/or the Continuous Integration workflows for finding images available in collections other than the default.
