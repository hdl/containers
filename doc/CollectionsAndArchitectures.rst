.. include:: shields/shields.collections.inc

.. _colections:

Collections and architectures
=============================

Images in this repository are organised in *collections* and built for multiple architectures.
A *collection* is a set of images which share a common ancestor; a base layer.
Having images with a common ancestor allows reducing bandwidth and disk usage when pulling several of them.
See `docs.docker.com: About storage drivers | Images and layers <https://docs.docker.com/storage/storagedriver/#images-and-layers>`__.

Collections:

* ``debian/bullseye`` based on ``ARCHITECTURE/debian:bullseye-slim`` (default)
* ``rockylinux/8`` based on ``ARCHITECTURE/rockylinux:8``

.. IMPORTANT::
  Deprecated:

  * ``centos/7`` based on ``ARCHITECTURE/centos:7``

  Removed:

  * ``debian/buster`` based on ``ARCHITECTURE/debian:buster-slim``

Architectures:

* `amd64 <https://hub.docker.com/u/amd64>`__
* `arm32v7 <https://hub.docker.com/u/arm32v7>`__
* `arm64v8 <https://hub.docker.com/u/arm64v8>`__
* `ppc64le <https://hub.docker.com/u/ppc64le>`__
* `s390x <https://hub.docker.com/u/s390x>`__
* `mips64le <https://hub.docker.com/u/mips64le>`__
* `riscv64 <https://hub.docker.com/u/riscv64>`__

Each image is published to both `gcr.io` and `ghcr.io`:

.. centered:: |SHIELD:Generic:GCR| |SHIELD:Generic:GHCR|

However, fields ``ARCHITECURE`` and ``COLLECTION`` are optional because:

* Images for the default architecture are mirrored to |SHIELD:Mirror:GCR:NoArchitecture| and
  |SHIELD:Mirror:GHCR:NoArchitecture|.

* Images of the default collection are mirrored to |SHIELD:Mirror:GCR:NoCollection| and
  |SHIELD:Mirror:GHCR:NoCollection|.

* Images of the default collection for the default architecture are mirrored to |SHIELD:Mirror:Docker|.

* Images of the default collection for the default architecture which are not ``build`` or ``pkg`` are mirrored to
  |SHIELD:Mirror:GCR:Default| and |SHIELD:Mirror:GHCR:Default|.

.. important::
   Image names and tags in this documentation are provided without the *registry prefix*.
   Hence, one of the prefixes listed above needs to be used when actually pulling/using the images.
   See :ref:`User Guide <UserGuide>` for further details.

.. important::
   The table in :ref:`tools-and-images` shows the tools available in the default collection for the default
   architecture.
   Some tools are available in a subset of collections or for a subset of architectures only.
   Browse the registries and/or the Continuous Integration workflows for finding images available in collections other
   than the default.
