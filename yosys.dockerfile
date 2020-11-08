FROM hdlc/build:build AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libffi-dev \
    libreadline-dev \
    tcl-dev \
    graphviz \
    xdot \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

#---

FROM base AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    bison \
    flex \
    gawk \
    gcc \
    git \
    iverilog \
    pkg-config \
    zlib1g-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/yosys && cd /tmp/yosys \
 && curl -fsSL https://codeload.github.com/cliffordwolf/yosys/tar.gz/master | tar xzf - --strip-components=1 \
 && make -j $(nproc) \
 && make DESTDIR=/opt/yosys install \
 && make test

#---

FROM scratch AS pkg
COPY --from=build /opt/yosys /yosys

#---

FROM base

COPY --from=build /opt/yosys /
CMD ["yosys"]
