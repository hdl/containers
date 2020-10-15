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

RUN mkdir /tmp/symbiyosys && cd /tmp/symbiyosys \
 && curl -fsSL https://codeload.github.com/YosysHQ/SymbiYosys/tar.gz/master | tar xzf - --strip-components=1 \
 && make DESTDIR=/opt/symbiyosys install

#---

FROM scratch
COPY --from=build /opt/symbiyosys /symbiyosys
