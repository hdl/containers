ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

# WORKAROUND: this is required because 'COPY --from' does not support ARGs
FROM $REGISTRY/pkg/icestorm AS pkg-icestorm

FROM $REGISTRY/build/build AS build

COPY --from=pkg-icestorm /icestorm/usr/local/share/icebox /usr/local/share/icebox
