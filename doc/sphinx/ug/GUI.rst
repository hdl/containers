.. GUI:

Tools with GUI
##############

By default, tools with Graphical User Interface (GUI) cannot be used in containers, because there is no graphical
server.
However, there are multiple alternatives for making an `X11 <https://en.wikipedia.org/wiki/X_Window_System>`__ or
`Wayland <https://en.wikipedia.org/wiki/Wayland_(display_server_protocol)>`__ server visible to the container.
`mviereck/x11docker <https://github.com/mviereck/x11docker>`__ and `mviereck/runx <https://github.com/mviereck/runx>`__ are
full-featured helper scripts for setting up the environment and running GUI applications and desktop environments in OCI
containers.
GNU/Linux and Windows hosts are supported, and security related options are provided (such as cookie authentication).
Users of GTKWave, KLayout, nextpnr and other tools will likely want to try x11docker (and runx).

* `x11docker: Run GUI applications in Docker containers; Journal of Open Source Hardware <https://joss.theoj.org/papers/10.21105/joss.01349>`__.

[#img-x11docker]
.Execution of KLayout in a container on Windows 10 (MSYS2/MINGW64) with https://github.com/mviereck/x11docker[mviereck/x11docker], https://github.com/mviereck/runx[mviereck/runx] and https://sourceforge.net/projects/vcxsrv/[VcxSrv].
[link=img/x11docker_klayout.gif]
image::x11docker_klayout.gif[x11docker_klayout, align="center"]

.. |SHIELD:WorkflowTest| image:: https://img.shields.i
   :alt: '#img-x11docker'
   :height: 22
   :target: https://hub.docker.com/u/hdlc 