.. _Development:package-images:

Package images
##############

.. role:: blue

Each EDA tool/project is built once only for each collection and architecture in this image/container ecosystem.
However, some (many) of the tools need to be included in multiple images for different purposes.
Moreover, it is desirable to keep build recipes separated, in order to better understand the dependencies of each
tool/project.
Therefore, ``REGISTRY/[ARCHITECTURE/][COLLECTION/]pkg/`` images are created/used (coloured :blue:`BLUE` in the
:ref:`Graphs <Development:graphs>`).
These are all based on ``scratch`` and are not runnable.
Instead, they contain pre-built artifacts, to be then added into other images through ``COPY --from=``.

Since ``pkg`` images are not runnable *per se*, but an intermediate utility, the usage of environment variables
``PREFIX`` and ``DESTDIR`` in the dockerfiles might be misleading.
All the tools in the ecosystem are expected to be installed into ``/usr/local``, the standard location for user built
tools on most GNU/Linux distributions.
Hence:

* ``PREFIX`` should typically not need to be modified.
  Most of the tools will default to ``PREFIX=/usr/local``, which is correct.
  Yet, some tools might default to ``/`` or ``/usr``.
  In those cases, setting it explicitly is required.

* ``DESTDIR`` must be set to an empty location when calling ``make install`` or when copying the artifacts otherhow.
  The content of the corresponding package images is taken from that empty location.
  Therefore, if ``DESTDIR`` was unset, the artifacts of the tool might potentially be mixed with other existing assets
  in ``/usr/local``.
  In most of the dockerfiles, ``/opt/TOOL_NAME`` is used as the temporary empty location.

Despite the usage of these variables being documented in `GNU Coding Standards <https://www.gnu.org/prep/standards/html_node/index.html>`__,
``DESTDIR`` seems not to be very used, except by packagers.
As a result, contributors might need to patch the build scripts upstream.
Sometimes ``DESTDIR`` is not supported at all, or it is supported but some lines in the makefiles are missing it.
Do not hesitate to reach for help through the issues or the chat!
