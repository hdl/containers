FROM symbiflow/build:base AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    binutils \
    g++ \
    make \
    python3-distutils \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && update-ca-certificates  \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/z3 && cd /tmp/z3 \
 && curl -fsSL https://codeload.github.com/Z3Prover/z3/tar.gz/master | tar xzf - --strip-components=1 \
 && python3 scripts/mk_make.py \
 && cd build \
 && make \
 && make DESTDIR=/opt/z3 install \
 && tar -zcvf /tmp/z3.tgz -C /opt/z3/usr/ .

#---

FROM scratch
COPY --from=build /opt/z3 /z3
