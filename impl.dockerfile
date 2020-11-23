FROM hdlc/nextpnr

COPY --from=hdlc/pkg:ghdl-yosys-plugin /ghdl /
COPY --from=hdlc/pkg:yosys /yosys /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libffi-dev \
    libgnat-8 \
    libreadline-dev \
    tcl-dev \
    graphviz \
    xdot \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists \
 && yosys-config --exec mkdir -p --datdir/plugins \
 && yosys-config --exec ln -s /usr/local/lib/ghdl_yosys.so --datdir/plugins/ghdl.so
