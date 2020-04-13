FROM debian:buster-slim
COPY --from=symbiflow/pkg:icestorm /iceprog /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libftdi1-2 \
    openocd \
    usbutils \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
