.. USBIP:

USB/IP protocol support for Docker Desktop
##########################################

Virtual Machines used on Windows for running either Windows Subsystem for Linux (WSL) or Docker Desktop by default do
not support sharing USB devices with the containers.
Only those that are identified as storage or COM devices can be bind directly.
See `microsoft/WSL#5158 <https://github.com/microsoft/WSL/issues/5158>`__.
That prevents using arbitrary drivers inside the containers.
As a result, most container users on Windows do install board programming tools through MSYS2 (see `hdl/MINGW-packages <https://github.com/hdl/MINGW-packages>`__).

Nevertheless, USB/IP protocol allows passing USB device(s) from server(s) to client(s) over the network.
As explained at https://www.kernel.org/doc/readme/tools-usb-usbip-README[kernel.org/doc/readme/tools-usb-usbip-README],
on GNU/Linux, USB/IP is implemented as a few kernel modules with companion userspace tools.
However, the default underlying Hyper-V VM machine (based on `Alpine Linux <https://alpinelinux.org/>`__) shipped with
*Docker Desktop* (aka *docker-for-win*/*docker-for-mac*) does not include the required kernel modules.
Fortunately, privileged docker containers allow installing missing kernel modules.
The shell script in link:{repotree}usbip/[`usbip/`] supports customising the native VM in *Docker Desktop* for adding
USB over IP support.

.. code-block:: bash

   # Build kernel modules: in an unprivileged `alpine` container, retrieve the corresponding
   # kernel sources, copy runtime config and enable USB/IP features, build `drivers/usb/usbip`
   # and save `*.ko` artifacts to relative subdir `dist` on the host.
   ./run.sh -m
   
   # Load/insert kernel modules: use a privileged `busybox` container to load kernel modules
   # `usbip-core.ko` and `vhci-hcd.ko` from relative subdir `dist` on the host to the
   # underlying Hyper-V VM.
   ./run.sh -l
   
   # Build image `vhcli`, using `busybox` as a base, and including the
   # [VirtualHere](https://www.virtualhere.com) GNU/Linux client for x86_64 along with the
   # `*.ko` files built previously through `./run.sh -m`.
   ./run.sh -v

.. note::
   For manually selecting configuration options, building and inserting modules, see detailed procedure in `gw0/docker-alpine-kernel-modules#usage <https://github.com/gw0/docker-alpine-kernel-modules#usage>`__.

.. note::
   Modules will be removed when the Hyper-V VM is restarted (i.e. when the host or *Docker Desktop* are restarted). For a *permanent* install, modules need to be copied to ``/lib/modules`` in the underlying VM, and ``/stc/modules`` needs to be configured accordingly. Use ``$(command -v winpty) docker run --rm -it --privileged --pid=host alpine nsenter -t 1 -m -u -n -i sh`` to access a shell with full permissions on the VM.

.. note::
   USB/IP is supported in Renode too. See `renode.rtfd.io/en/latest/tutorials/usbip <https://renode.readthedocs.io/en/latest/tutorials/usbip.html>`__.
