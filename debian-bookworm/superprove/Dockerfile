# Authors:
#   Unai Martinez-Corral
#     <umartinezcorral@antmicro.com>
#     <unai.martinezcorral@ehu.eus>
#   Torsten Meissner
#   Sverre Hamre
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

ARG REGISTRY='gcr.io/hdl-containers/debian/bookworm'

#---

FROM $REGISTRY/build/build AS build

# Create a francendebian with python2.7 from debian bulseye
RUN curl -O http://ftp.debian.org/debian/pool/main/libf/libffi/libffi7_3.3-6_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/o/openssl/libssl1.1_1.1.1w-0+deb11u1_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/p/python2.7/libpython2.7-minimal_2.7.18-8+deb11u1_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/p/python2.7/python2.7-minimal_2.7.18-8+deb11u1_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/p/python2.7/libpython2.7-stdlib_2.7.18-8+deb11u1_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/p/python2.7/python2.7_2.7.18-8+deb11u1_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/p/python2.7/libpython2.7-dev_2.7.18-8+deb11u1_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/p/python2.7/python2.7-dev_2.7.18-8+deb11u1_amd64.deb
RUN curl -O http://ftp.debian.org/debian/pool/main/p/python2.7/libpython2.7_2.7.18-8+deb11u1_amd64.deb

RUN apt-get update -qq \
&& apt-get -y install mime-support libexpat1-dev

RUN dpkg -i libffi7_3.3-6_amd64.deb 
RUN dpkg -i libssl1.1_1.1.1w-0+deb11u1_amd64.deb 
RUN dpkg -i libpython2.7-minimal_2.7.18-8+deb11u1_amd64.deb 
RUN dpkg -i python2.7-minimal_2.7.18-8+deb11u1_amd64.deb 
RUN dpkg -i libpython2.7-stdlib_2.7.18-8+deb11u1_amd64.deb 
RUN dpkg -i python2.7_2.7.18-8+deb11u1_amd64.deb 
RUN dpkg -i libpython2.7_2.7.18-8+deb11u1_amd64.deb
RUN dpkg -i libpython2.7-dev_2.7.18-8+deb11u1_amd64.deb 
RUN dpkg -i python2.7-dev_2.7.18-8+deb11u1_amd64.deb 
# End francendebian installs


RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends ${makedepends[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/* 
 #\
 #&& prepare

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build

#---

FROM scratch AS version
COPY --from=build /tmp/hdlc.superprove.version /

#---

FROM scratch
COPY --from=build /opt/superprove /superprove
