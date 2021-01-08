FROM hdlc/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    binutils \
    python3-distutils \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/z3 && cd /tmp/z3 \
 && curl -fsSL https://codeload.github.com/Z3Prover/z3/tar.gz/master | tar xzf - --strip-components=1 \
 && python3 scripts/mk_make.py \
 && cd build \
 && make PREFIX=/usr/local \
 && make DESTDIR=/opt/z3 install

#---

FROM scratch
COPY --from=build /opt/z3 /z3
