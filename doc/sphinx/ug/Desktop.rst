.. Desktop:

Desktop
#######

Example session
===============

How to connect a *Docker Desktop* container to *VirtualHere USB Server for Windows*.

* Start `vhusbdwin64.exe <https://www.virtualhere.com/sites/default/files/usbserver/vhusbdwin64.exe>`__ on the host
* Ensure that the firewall is not blocking it.

.. code-block:: bash

   # Start container named 'vhclient'
   ./run.sh -s
   # List usb devices available in the container
   ./run.sh -e lsusb
   # LIST hubs/devices found by vhclient
   ./run.sh -c "LIST"
   # Manually add to the client the hub/server running on the host
   ./run.sh -c "MANUAL HUB ADD,host.docker.internal:7575"
   
   sleep 10
   
   ./run.sh -c "LIST"
   # Use a remote device in the container
   ./run.sh -c "USE,<SERVER HOSTNAME>.1"
   
   sleep 4
   
   # Check that the device is now available in the container
   ./run.sh -e lsusb

.. important::
   There is an issue/bug in *Docker Desktop* (`docker/for-win#4548 <https://github.com/docker/for-win/issues/4548>`__) that prevents the container where the USB device is added from seeing it. The workaround is to execute the board programming tool in a sibling container. For example: ``docker run --rm --privileged */prog iceprog -t``.

Alternatives
============

.. important::
   Using `VirtualHere <https://www.virtualhere.com>`__ is the only solution we could successfully use in order to share FTDI devices (`icestick <https://www.latticesemi.com/icestick>`__ boards) between a Windows 10 host and a Docker Desktop container running on the same host. However, since the USB/IP protocol is open source, we'd like to try any other (preferredly open and free source) server for Windows along with the default GNU/Linux usbip-tools. Should you know about any, please `let us know <https://github.com/hdl/containers/issues/new>`__!

   We are aware of `cezuni/usbip-win <https://github.com/cezuni/usbip-win>`__. However, it seems to be in very early development state and the install procedure is quite complex yet.


Serial (COM) devices can be shared with open source tools. On the one hand, `hub4com <https://sourceforge.net/projects/com0com/files/hub4com/>`__ from project http://com0com.sourceforge.net/[com0com] allows to publish a port through a RFC2217 server. On the other hand, ``socat`` can be used to link the network connection to a virtual ``tty`` device.

[source]
----
                   HOST                                           CONTAINER
        ---------------------------                 -------------------------------------
USB <-> | COMX <-> RFC2217 server | <-> network <-> | socat <-> /dev/ttySY <-> app/tool |
        ---------------------------                 -------------------------------------
----

.. code-block:: cmd

   REM On the Windows host
   com2tcp-rfc2217.bat COM<X> <PORT>

.. code-block:: bash

   # In the container
   socat pty,link=/dev/ttyS<Y> tcp:host.docker.internal:<PORT>

It might be possible to replace ``hub4com`` with `pyserial/pyserial <https://github.com/pyserial/pyserial>`__. However, we did not test it.

* https://pyserial.readthedocs.io/en/latest/examples.html#single-port-tcp-ip-serial-bridge-rfc-2217
* `espressif/esp-idf#204 <https://github.com/espressif/esp-idf/issues/204>`__
