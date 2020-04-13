FROM alpine as get
RUN apk add --no-cache --update git \
 && git clone --recurse-submodules https://github.com/SymbiFlow/prjtrellis /tmp/prjtrellis \
 && cd /tmp/prjtrellis \
 && git describe --tags > libtrellis/git_version

#---

FROM symbiflow/build:dev AS build
COPY --from=get /tmp/prjtrellis /tmp/prjtrellis

ENV LDFLAGS "-Wl,--copy-dt-needed-entries"

RUN cd /tmp/prjtrellis/libtrellis \
 && cmake -DCURRENT_GIT_VERSION="$(cat git_version)" . \
 && make -j $(nproc) \
 && make DESTDIR=/opt/prjtrellis install

#---

FROM scratch AS pkg
COPY --from=build /opt/prjtrellis /prjtrellis

#---

FROM symbiflow/build:base
COPY --from=build /opt/prjtrellis /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libboost-all-dev \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
