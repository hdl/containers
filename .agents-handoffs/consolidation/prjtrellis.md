# prjtrellis consolidation

Converted the flat recipe `debian/prjtrellis.dockerfile` into the subdirectory pattern:
`debian/prjtrellis/{Dockerfile,HDLC}`. The flat file was deleted. No changes to
`test/`, `images.yml` or `jobs.yml` (image name stays `debian/bullseye/prjtrellis`).

## HDLC layout

`debian/prjtrellis/HDLC` contains a `build()` function and `depends=()`:

- **build()**: clones `https://github.com/YosysHQ/prjtrellis` with `--recurse-submodules`,
  configures libtrellis with `-DCURRENT_GIT_VERSION="$(git describe --tags)"`, builds and
  installs with `make DESTDIR=/opt/prjtrellis install`.
- **depends=()**: `libboost-all-dev` and `make` — runtime deps installed in the final stage
  via the HDLC-sourced apt-get pattern.
- **No makedepends / no apt-get RUN for makedepends**: the build stage is
  `FROM $REGISTRY/build/dev AS build`, which provides cmake/make and the boost headers.
- **No `FROM scratch AS version`** stage (original had none).
- **`ENV LDFLAGS="-Wl,--copy-dt-needed-entries"`** is kept as an ENV in the Dockerfile
  build stage (not inside `build()`), matching the original.

`debian/prjtrellis/Dockerfile` stages: `build` (dev) → `pkg` (scratch, `/opt/prjtrellis` →
`/prjtrellis`) → runtime (`build/base` + HDLC apt-get for `${depends[@]}` +
`COPY --from=build /opt/prjtrellis /`). No `ARG IMAGE`.

## Dry-run

```
pyHDLC -n build -a amd64 -c debian/bullseye -d prjtrellis

Read images configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/images.yml (HDLC v0)
Read jobs configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/jobs.yml (HDLC v0)
· docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/prjtrellis --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/prjtrellis
```

The build context resolves to `debian/prjtrellis` with the standard `Dockerfile` name
(no `-f` flag needed). The HDLC bind-mount
(`RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC`) picks up
`debian/prjtrellis/HDLC` from that context.

## Real build

```
pyHDLC build -a amd64 -c debian/bullseye -d prjtrellis -q
```

**PASS.** Build completed (from-source cmake compile of libtrellis, ~142 s build stage),
image exported as `ghcr.io/hdl/amd64/debian/bullseye/prjtrellis:latest`
(arch amd64, ~1.27 GiB), and the `-q` test run passed:

- `ecpbram help` → exit 0 | OK
- `ecpmulti help` → exit 0 | OK
- `ecppack help` → exit 0 | OK
- `ecppll help` → exit 0 | OK
- `ecpunpack help` → exit 0 | OK
- followed by the standard `_todo.sh` "Test is not complete yet" note.