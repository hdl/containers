FROM hdlc/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    binutils \
    cmake \
    ninja-build \
    python-setuptools \
    python-pip \
    python-wheel \
    python-dev \
    git \
    zlib1g-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/superprove && cd /tmp/superprove \
 && git clone --recursive https://github.com/sterin/super-prove-build . \
 && mkdir build && cd build \
 && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local -G Ninja .. \
 && ninja \
 && ninja package \
 && mkdir -p /opt/superprove/usr/local \
 && tar -C /opt/superprove/usr/local -xzf super_prove*.tar.gz --strip 1 \
 && echo '#!/usr/bin/env bash' > /opt/superprove/usr/local/bin/suprove \
 && echo 'tool=super_prove; if [ "$1" != "${1#+}" ]; then tool="${1#+}"; shift; fi' >> /opt/superprove/usr/local/bin/suprove \
 && echo 'exec ${tool}.sh "$@"' >> /opt/superprove/usr/local/bin/suprove \
 && chmod +x /opt/superprove/usr/local/bin/suprove

#---

FROM scratch
COPY --from=build /opt/superprove /superprove
