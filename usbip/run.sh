#!/bin/sh

# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
#     <unai.martinezcorral@ehu.eus>
#
# Copyright Unai Martinez-Corral
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

# Install missing Alpine Linux kernel modules in the underlying VM of Docker for Mac/Windows
#
# This script is based on:
# * https://github.com/gw0/docker-alpine-kernel-modules
# * https://github.com/virtualhere/docker

cmd () {
  echo "> $@"
  "$@"
}

#---

# Build usbip kernel module and copy artifacts to subdir dist
module () {
docker run --name usbip -w //tmp/linux-src alpine sh -c "
apk add --no-cache --update ca-certificates curl gcc make musl-dev
curl -fsSL https://www.kernel.org/pub/linux/kernel/v4.x/linux-\$(uname -r | cut -d '-' -f 1).tar.gz | tar -xzf - --strip-components=1
make defconfig
([ ! -f /proc/1/root/proc/config.gz ] || zcat /proc/1/root/proc/config.gz > .config)
printf '%s\n' 'CONFIG_USBIP_CORE=m' 'CONFIG_USBIP_VHCI_HCD=m' 'CONFIG_USBIP_VHCI_HC_PORTS=8' 'CONFIG_USBIP_VHCI_NR_HCS=1' >> .config
make oldconfig modules_prepare
make M=drivers/usb/usbip modules
"

if [ ! -d dist ]; then
  mkdir -p dist;
fi
for f in usbip-core.ko vhci-hcd.ko Module.symvers; do
  docker cp usbip://tmp/linux-src/drivers/usb/usbip/$f ./dist/
done
docker rm -f usbip
}

#---

# Load kernel module in the underlying Alpine VM
load () {
cmd docker run --privileged --rm \
  -v /$(pwd)/dist://wrk -w //wrk \
  busybox sh -c "
insmod usbip-core.ko
insmod vhci-hcd.ko
lsmod | grep vhci
"
}

#---

# Build vhclient image
virtualhere () {
curl -fsSL https://www.virtualhere.com/sites/default/files/usbclient/vhclientx86_64 -o dist/vhclientx86_64

name="$1"
if [ "x$1" = "x" ]; then
  name="vhcli"
fi

base="$2"
if [ "x$1" = "x" ]; then
  base="busybox"
fi

docker build -t "$name" -f- . <<-EOF
FROM $base
COPY dist/vhclientx86_64 /opt/virtualhere/
COPY dist/*.ko /lib/modules/$(docker run --rm busybox uname -r)/
ENV HOME=/opt/virtualhere
ENV PATH=\$PATH:/opt/virtualhere
WORKDIR /opt/virtualhere
RUN echo -e '[General]\nAutoFind=0\n' > /opt/virtualhere/.vhui \
 && chmod +x /opt/virtualhere/vhclientx86_64
EOF
}

vhkill () {
cmd docker rm -f vhclient
}

#---

VHEXE="$(command -v winpty) docker exec -it vhclient"

case "$1" in
  -l) load        ;;
  -m) module      ;;
  -v)
    shift
    virtualhere "$@"
  ;;
  -s)
    vhkill
    shift
    img="$@"
    if [ "x$@" = "x" ]; then
      img="vhcli"
    fi
    cmd docker run -d --privileged --rm --name vhclient "$img" vhclientx86_64
  ;;
  -k)
    vhkill
  ;;
  -e)
    shift
    cmd $VHEXE "$@"
  ;;
  -c)
    shift
    clicmd="$@"
    if [ "x$@" = "x" ]; then
      clicmd="LIST"
    fi
    cmd $VHEXE vhclientx86_64 -t "$clicmd"
  ;;
  *)
    cat <<EOF
Usage:
-m
   build kernel module

-l
   load kernel module (privileged)

-v [NAME BASE]  (default: vhcli alpine)
   build vhclient image

-s [IMAGE]  (default: vhcli)
   start container named 'vhclient' (privileged)

-k
   kill/remove container 'vhclient'

-e ARGS
   interact with the running 'vhclient' container through 'docker exec'

-c "COMMAND"  (default: "LIST")
   interact with the VirtualHere client running in the container
EOF
esac
