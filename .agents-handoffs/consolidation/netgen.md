# netgen consolidation

## What was converted

`debian/netgen.dockerfile` → `debian/netgen/Dockerfile` + `debian/netgen/HDLC`.

The flat dockerfile was deleted. The image name, namespace, and default Dockerfile resolution are unchanged: pyHDLC resolves tool `netgen` as `debian/netgen/Dockerfile` with build context `debian/netgen` (this is what makes `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC` work). No test scripts, `images.yml`, or `jobs.yml` were touched; the image is still `debian/bullseye/netgen`.

## HDLC layout

`debian/netgen/HDLC` follows the irsim convention (`set -e`, arrays):

- `makedepends=( csh libcairo2-dev libglu1-mesa-dev libncurses-dev libx11-dev m4 python3-dev tcl tcl-dev tcl-expect tcsh tk-dev )` — the original build-stage package list.
- `build()` runs the original steps verbatim: `git clone git://opencircuitdesign.com/netgen /tmp/netgen; mkdir -p /opt/netgen/; cd /tmp/netgen; ./configure; make -j$(nproc); make install; make DESTDIR=/opt/netgen install`.
- `depends=( libcairo2 libglu1-mesa libncurses6 libx11-6 tcl tk )` — the original runtime-stage package list.

The Dockerfile keeps exactly the original three-stage structure minus what never existed:

- `FROM $REGISTRY/build/build AS build` — one RUN for makedepends via `${makedepends[@]}`, one `RUN ... && build`.
- `FROM scratch AS pkg` — `COPY --from=build /opt/netgen /netgen`.
- `FROM $REGISTRY/build/base` — runtime depends via `${depends[@]}`, `COPY --from=build /opt/netgen /`, `CMD ["netgen"]`.

No `FROM scratch AS version` stage (the original had none). No `ARG IMAGE` (the original had none). The extra author **Sai Charan Lanka** is preserved in BOTH the HDLC and Dockerfile author blocks. `CMD ["netgen"]` is preserved.

## pyHDLC dry-run

Command: `pyHDLC -n build -a amd64 -c debian/bullseye -d netgen`

Output (single docker command; `-f` is omitted because `debian/netgen/Dockerfile` is the default name within the context `debian/netgen`):

```
Read images configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/images.yml (HDLC v0)
Read jobs configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/jobs.yml (HDLC v0)
· docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/netgen --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/netgen
```

The build context resolves to the subdirectory `debian/netgen`, confirming the layout conversion works.

## Real build result

Command: `pyHDLC build -a amd64 -c debian/bullseye -d netgen -q`

**PASS** (build + test).

- Build stages all completed: makedepends install, `git clone` with autotools configure/make/install into `/opt/netgen`, pkg stage export, runtime layer, image tagged `ghcr.io/hdl/amd64/debian/bullseye/netgen:latest`.
- `docker inspect` confirmed `Architecture: amd64`, size 405941643 bytes.
- Test (`//wrk/netgen.sh`) ran inside the container: `/usr/local/bin/netgen` executed and reported `Netgen 1.5.323`, followed by the expected `_todo.sh` placeholder (`Ops! This test is not complete yet.`).
- The only "error" strings in the log are informational configure/make messages (`checking for library containing strerror`, "see files make.log"); no build failures (compiler warnings in `netcmp.c` are pre-existing upstream code warnings only).