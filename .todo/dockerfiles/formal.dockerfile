ARG IMAGE="ghdl/synth:beta"

FROM $IMAGE

COPY --from=symbiflow/pkg:z3 /z3 /
COPY --from=symbiflow/pkg:symbiyosys /symbiyosys /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python3 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
