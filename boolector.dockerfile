FROM hdlc/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    binutils \
    cmake \
    autoconf \
    git \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/boolector && cd /tmp/boolector \
 && curl -fsSL https://codeload.github.com/boolector/boolector/tar.gz/master | tar xzf - --strip-components=1 \
 && ./contrib/setup-btor2tools.sh \
 && ./contrib/setup-lingeling.sh \
 && ./configure.sh \
 && make -C build -j$(nproc) PREFIX=/usr/local/ \
 && mkdir -p /opt/boolector/usr/local/bin /opt/boolector/usr/local/lib \
 && cp build/bin/boolector build/bin/btor* deps/btor2tools/bin/btorsim /opt/boolector/usr/local/bin/ \
 && cp build/lib/libboolector.a /opt/boolector/usr/local/lib/

#---

FROM scratch
COPY --from=build /opt/boolector /boolector
