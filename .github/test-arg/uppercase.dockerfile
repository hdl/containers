ARG REGISTRY='gcr.io/hdl-containers/debian/bullseye'

FROM $REGISTRY/build/build AS build

ARG REGISTRY

COPY --from=$REGISTRY/pkg/icestorm /icestorm/usr/local/share/icebox /usr/local/share/icebox
