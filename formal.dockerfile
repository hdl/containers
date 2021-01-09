FROM hdlc/ghdl:yosys

COPY --from=hdlc/pkg:z3 /z3 /
COPY --from=hdlc/pkg:yices2 /yices2 /
COPY --from=hdlc/pkg:boolector /boolector /
COPY --from=hdlc/pkg:symbiyosys /symbiyosys /

RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    python3 \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
