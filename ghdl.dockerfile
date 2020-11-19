FROM ghdl/pkg:buster-mcode AS build

# TODO Build GHDL on hdlc/build:build instead of picking ghdl/pkg:buster-mcode

#---

FROM scratch AS pkg

COPY --from=build / /ghdl/

#--

FROM hdlc/build:base

COPY --from=build / /usr/local/

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libgnat-8 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists


