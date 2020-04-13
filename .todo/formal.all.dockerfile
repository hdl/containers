FROM debian:buster-slim AS build

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    build-essential \
    clang \
    bison \
    flex \
    libreadline-dev \
    gawk \
    tcl-dev \
    libffi-dev \
    git \
    mercurial \
    graphviz \
    xdot \
    pkg-config \
    python \
    python3 \
    libftdi-dev \
    gperf \
    libboost-program-options-dev \
    autoconf \
    libgmp-dev \
    cmake \
    make \
    wget \
    libpython2.7 && \
    apt-get clean -y && \
    apt-get autoclean -y && \
    apt-get autoremove -y

ENV PREFIX=/opt/symbiyosys

RUN cd /home/symbiyosys && \
    git clone https://github.com/SRI-CSL/yices2.git yices2 && \
    cd yices2 && \
    autoconf && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    cd /home/symbiyosys && \
    git clone https://bitbucket.org/arieg/extavy.git && \
    cd extavy && \
    git submodule update --init && \
    mkdir build; cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    cp avy/src/avy $PREFIX/bin/ && \
    cp avy/src/avybmc $PREFIX/bin/ && \
    cd /home/symbiyosys && \
    git clone https://github.com/boolector/boolector && \
    git clone https://github.com/arminbiere/lingeling boolector/deps/lingeling && \
    git clone https://github.com/boolector/btor2tools boolector/deps/btor2tools && \
    ( cd boolector/deps/lingeling  && ./configure.sh -fPIC && make -j$(nproc); ) && \
    ( cd boolector/deps/btor2tools && ./configure.sh -fPIC && make -j$(nproc); ) && \
    ( cd boolector && ./configure.sh && cd build && make -j$(nproc); ) && \
    cp boolector/build/bin/boolector $PREFIX/bin/ && \
    cp boolector/build/bin/btor* $PREFIX/bin/ && \
    cp boolector/deps/btor2tools/bin/btorsim $PREFIX/bin/ && \
    cd /home/symbiyosys && \
    wget https://downloads.bvsrc.org/super_prove/super_prove-hwmcc17_final-2-d7b71160dddb-Ubuntu_14.04-Release.tar.gz && \
    tar xzf super_prove-hwmcc17_final-2-d7b71160dddb-Ubuntu_14.04-Release.tar.gz -C $PREFIX/ && \
    echo '#!/bin/bash' >> $PREFIX/bin/suprove && \
    echo 'tool=super_prove; if [ "$1" != "${1#+}" ]; then tool="${1#+}"; shift; fi' >> $PREFIX/bin/suprove && \
    echo 'exec $PREFIX/super_prove/bin/${tool}.sh "$@"' >> $PREFIX/bin/suprove && \
    chmod +x $PREFIX/bin/suprove

FROM ghdl/synth:beta

COPY --from=build /opt/symbiyosys /usr/local

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    tcl-dev \
    python \
    python3 \
    make \
    libpython2.7 && \
    apt-get clean -y && \
    apt-get autoclean -y && \
    apt-get autoremove -y

RUN mkdir work
VOLUME /home/symbiyosys/work
