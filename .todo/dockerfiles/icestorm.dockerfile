FROM symbiflow/build:build AS build

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    pkg-config

RUN mkdir /tmp/icestorm \
 && cd /tmp/icestorm \
 && curl -fsSL https://codeload.github.com/cliffordwolf/icestorm/tar.gz/master | tar xzf - --strip-components=1 \
 && ICEPROG=0 make -j $(nproc) \
 && ICEPROG=0 make DESTDIR=/opt/icestorm install

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libftdi1-dev

RUN cd /tmp/icestorm/iceprog \
 && make -j $(nproc) \
 && make DESTDIR=/opt/iceprog install

#---

FROM scratch AS pkg
COPY --from=build /opt/iceprog /iceprog
COPY --from=build /opt/icestorm /icepricestormog

#---

FROM symbiflow/build:base
COPY --from=build /opt/icestorm /
