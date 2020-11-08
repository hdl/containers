FROM hdlc/yosys AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-8 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#--

FROM ghdl/pkg:buster-mcode AS build

# TODO Build GHDL on hdlc/build:build instead of picking ghdl/pkg:buster-mcode

#--

FROM hdlc/build:base AS run

COPY --from=build / /opt/ghdl

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-8 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#---

FROM base AS plugin

COPY --from=build / /opt/ghdl

RUN mkdir /tmp/ghdl-yosys-plugin && cd /tmp/ghdl-yosys-plugin \
 && curl -fsSL https://codeload.github.com/ghdl/ghdl-yosys-plugin/tar.gz/master | tar xzf - --strip-components=1

RUN cp -vr /opt/ghdl/* /usr/local \
 && cd /tmp/ghdl-yosys-plugin \
 && make \
 && cp ghdl.so /opt/ghdl/lib/ghdl_yosys.so

#---

FROM base

COPY --from=plugin /opt/ghdl /usr/local

RUN yosys-config --exec mkdir -p --datdir/plugins \
 && yosys-config --exec ln -s /usr/local/lib/ghdl_yosys.so --datdir/plugins/ghdl.so
