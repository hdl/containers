.. _UserGuide:GUI:

Tools with GUI
##############

By default, tools with Graphical User Interface (GUI) cannot be used in containers, because there is no graphical
server.
However, there are multiple alternatives for making an :wikipedia:`X11 <X_Window_System>` or
:wikipedia:`Wayland <Wayland_(display_server_protocol)>` server visible to the container.
:gh:`mviereck/x11docker` and :gh:`mviereck/runx` are full-featured helper scripts for setting up the environment and
running GUI applications and desktop environments in OCI containers.
GNU/Linux and Windows hosts are supported, and security related options are provided (such as cookie authentication).
Users of GTKWave, KLayout, nextpnr and other tools will likely want to try x11docker (and runx).

.. figure:: ../_static/img/x11docker_klayout.gif
  :alt: Block diagram of the OSVB
  :width: 100%
  :align: center

  Execution of KLayout in a container on Windows 10 (MSYS2/MINGW64) with
  :gh:`mviereck/x11docker`, :gh:`mviereck/runx` and `VcxSrv <https://sourceforge.net/projects/vcxsrv/>`__.

* `x11docker: Run GUI applications in Docker containers; Journal of Open Source Hardware <https://joss.theoj.org/papers/10.21105/joss.01349>`__
