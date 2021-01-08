FROM hdlc/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    binutils \
    autoconf \
    gperf \
    libgmp-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/yices2 && cd /tmp/yices2 \
&& curl -fsSL https://codeload.github.com/SRI-CSL/yices2/tar.gz/master | tar xzf - --strip-components=1 \
&& autoconf \
&& ./configure \
&& make -j$(nproc) \
&& make DESTDIR=/opt/yices2 install

#---

FROM scratch
COPY --from=build /opt/yices2 /yices2
