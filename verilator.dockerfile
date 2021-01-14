FROM hdlc/build:build AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    autoconf \
    bison \
    flex \
    libfl-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

FROM base AS build

RUN git clone https://github.com/verilator/verilator \
 && cd verilator \
 && autoconf \
 && ./configure \
 && make -j$(nproc) \
 && make DESTDIR=/opt/verilator install \
 && git clone https://github.com/veripool/vcddiff \
 && make -C vcddiff CC=$CC \
 && cp -p vcddiff/vcddiff /opt/verilator/usr/local/bin/vcddiff

#---

FROM scratch AS pkg
COPY --from=build /opt/verilator /verilator

#---

FROM hdlc/build:base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    perl \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/verilator /
CMD ["verilator"]
