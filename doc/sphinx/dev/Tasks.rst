.. _Development:tasks:

Tasks
#####

The strategical priorities are the following:

*  Add the missing ASIC tools to collection ``debian/bullseye``.
Following the order in `efabless/openlane: OpenLANE Design Stages <https://github.com/efabless/openlane#openlane-design-stages>`__
is suggested.

*  Add the missing tools to collection ``centos/7``.
This collection is currently empty (it contains the base dockerfile only).
It was added because OpenLane containers are based on ``centos:7``, but may be updated to ``centos:8``.
Moreover, some DARPA users might be constrained to ``centos:6``.
We should confirm that.

*  Setup cross-triggering between CI workflows.
Currently, all workflows are triggered at the same time.
That produces some races and some tools are built twice in the same run (`moby/buildkit#1930 <https://github.com/moby/buildkit/issues/1930>`__).
That is not critical because we do know how to solve it (:ghsrc:`github/trigger.sh <github/trigger.sh>`).
We didn't implement it yet because we'd like it to be automatically sychronised with the graphs (see :ref:`Graph generation/parsing <Development:graph-generation>`).

*  Coordinate with Antmicro/SymbiFlow for using self-hosted runners provided by Google and their orchestration plumbing.

*  Enhance the (atomic) `smoke-tests <https://github.com/hdl/smoke-tests>`__, which are currently placeholders mostly.

*  Provide multiarch manifests.
See `dbhi/qus <https://github.com/dbhi/qus>`__ and `Multi-arch build and images, the simple way <https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/>`__.

*  Versioning. Currently, images are not versioned explicitly. Images are only pushed when builds and tests are successful.
   Users which cannot afford breaking changes can use the image by digest, instead of doing it by name.
   However, we should probably leverage manifests for publishing some *versioned ecosystems*, impliying that we run a 
   full test suite on an specific group of images and we then tag them all together as a *nicely behaving family/release*.

.. note::

   These are all in no particular order, although most of them are closely related to each other.
   It you want to tackle any of them, `let us know <https://github.com/hdl/containers/issues/new>`__ or `join the chat <https://gitter.im/hdl/community>`__!
   