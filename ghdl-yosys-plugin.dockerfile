FROM hdlc/yosys AS base

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-8 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists

#---

FROM base AS plugin

COPY --from=hdlc/pkg:ghdl /ghdl /opt/ghdl

RUN mkdir /tmp/ghdl-yosys-plugin && cd /tmp/ghdl-yosys-plugin \
 && curl -fsSL https://codeload.github.com/ghdl/ghdl-yosys-plugin/tar.gz/master | tar xzf - --strip-components=1

RUN cp -vr /opt/ghdl/* /usr/local \
 && cd /tmp/ghdl-yosys-plugin \
 && make \
 && cp ghdl.so /opt/ghdl/lib/ghdl_yosys.so

#---

FROM hdlc/pkg:ghdl AS pkg

COPY --from=plugin /opt/ghdl/lib/ghdl_yosys.so /ghdl/lib/ghdl_yosys.so

#---

FROM base

COPY --from=plugin /opt/ghdl /usr/local

RUN yosys-config --exec mkdir -p --datdir/plugins \
 && yosys-config --exec ln -s /usr/local/lib/ghdl_yosys.so --datdir/plugins/ghdl.so
