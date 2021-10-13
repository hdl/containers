ARG registry='gcr.io/hdl-containers/debian/bullseye'

FROM $registry/build/build AS build

ARG registry

COPY --from=$registry/pkg/icestorm /icestorm/usr/local/share/icebox /usr/local/share/icebox
