# Handoff: convert `debian/openfpgaloader.dockerfile` → `debian/openfpgaloader/`

## What was converted

Flat recipe `debian/openfpgaloader.dockerfile` was converted to the HDLC subdirectory pattern:

- `debian/openfpgaloader/HDLC` — the build logic (makedepends/depends arrays + `build()` function), sourced inside each `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC` instruction.
- `debian/openfpgaloader/Dockerfile` — the build recipe, now consuming the HDLC script.
- `debian/openfpgaloader.dockerfile` was **deleted**.

The image name remains `debian/bullseye/openfpgaloader`. No changes to `test/`, `images.yml`, or `jobs.yml`.

## HDLC layout

```
# HDLC openfpgaloader
...
set -e

makedepends=( cmake libftdi1-2 libftdi1-dev libhidapi-dev libudev-dev pkg-config zlib1g-dev )

build() {
  git clone --recurse-submodules https://github.com/trabucayre/openFPGALoader /tmp/openFPGALoader
  cd /tmp/openFPGALoader
  mkdir build
  cd build
  cmake ../
  cmake --build .
  make DESTDIR=/opt/openFPGALoader install
  mkdir -p /opt/openFPGALoader/etc/udev/rules.d
  cp ../99-openfpgaloader.rules /opt/openFPGALoader/etc/udev/rules.d/
}

depends=( libftdi1-2 libhidapi-libusb0 udev zlib1g )
```

- `makedepends`: `cmake`, `libftdi1-2`, `libftdi1-dev`, `libhidapi-dev`, `libudev-dev`, `pkg-config`, `zlib1g-dev` (note: `libftdi1-2` kept in makedepends as in the original).
- `build()`: clones openFPGALoader with `--recurse-submodules`, cmake configure/build, `make DESTDIR=/opt/openFPGALoader install`, then copies the udev rules file into `/opt/openFPGALoader/etc/udev/rules.d/` (preserved exactly from the original).
- `depends`: `libftdi1-2`, `libhidapi-libusb0`, `udev`, `zlib1g` (runtime image installs them).
- Build stage changed from `FROM $REGISTRY/build/dev AS build` (keep) — the original had no apt-get install in the original beyond makedepends; the flat recipe's `apt-get update/install/autoclean` lines were folded into the HDLC-sourced `RUN`.
- No `FROM scratch AS version` stage and no `ARG IMAGE` (original had neither).
- Runtime stage: `FROM $REGISTRY/build/base`, `COPY --from=build /opt/openFPGALoader /`, then HDLC-sourced install of `depends`, ending with the trailing `# NOTE:` udevadm reload/trigger comment block preserved verbatim.

## Dry-run output

`pyHDLC -n build -a amd64 -c debian/bullseye -d openfpgaloader` produced:

```
· docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/openfpgaloader --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/openfpgaloader
```

- Context resolves to `debian/openfpgaloader` ✓ (the tool's own directory, which is what makes `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC` work).
- No explicit `-f` flag is emitted. This is expected: pyHDLC only adds `-f` when the dockerfile path has a suffix (see `__init__.py:462`, `*(["-f", str(dockerfilePath)] * bool(dockerfilePath.suffix))`). A subdirectory recipe is `<context>/Dockerfile` with no suffix, so docker uses it as the default Dockerfile name. Behavior is identical to the already-consolidated `irsim`, verified via `pyHDLC -n build -a amd64 -c debian/bullseye -d irsim`.
- No `version` export step is printed because openfpgaloader has no `FROM scratch AS version` stage.

## Real build result

`pyHDLC build -a amd64 -c debian/bullseye -d openfpgaloader -q`:

**Build: PASS**

- Stage `build 2/3` (`RUN . /tmp/ctx/HDLC && apt-get install ${makedepends[@]} ...`): makedepends installed successfully from the sourced HDLC (cmake, libftdi1-2, libftdi1-dev, libhidapi-dev, libudev-dev, pkg-config, zlib1g-dev).
- Stage `build 3/3` (`RUN . /tmp/ctx/HDLC && build`): sourced HDLC correctly, `build()` ran end-to-end — git clone with submodules, cmake configure (found libftdi1 1.5, libusb-1.0, hidapi-libusb, zlib, libudev; libgpiod not found → gpiod disabled), `cmake --build .` compiled all 31 CXX objects, `make DESTDIR=/opt/openFPGALoader install`, and the udev rules file copy (installed bit.gz files + binary to `/opt/openFPGALoader/usr/local/`).
- `stage-1 (FROM scratch)` `COPY --from=build /opt/openFPGALoader /openfpgaloader` succeeded.
- Runtime stage installed `depends` (`libftdi1-2`, `libhidapi-libusb0`, `udev`, `zlib1g`), `COPY --from=build /opt/openFPGALoader /`, and the trailing `# NOTE:` udevadm block is preserved.
- Image `ghcr.io/hdl/amd64/debian/bullseye/openfpgaloader:latest` exported (manifest sha256:84f3a0dcade29dac6ed5c1e92a5be1c58b5de33e42216c70ef1b1ef4b12328ba). Size: 221467579 bytes, Architecture amd64.

**Test: PASS**

```
· docker run --rm -v /home/umarcor/ghdl-hdlc/test://wrk ghcr.io/hdl/amd64/debian/bullseye/openfpgaloader //wrk/openfpgaloader.sh
· openFPGALoader help: exit code 0 | OK
Ops! This test is not complete yet.
Submit a PR! https://github.com/hdl/containers/compare
```

`openFPGALoader help` smoke test passed (`exit code 0 | OK`), then the `_todo.sh` placeholder ran. The mechanical step of sourcing `debian/openfpgaloader/HDLC` worked end-to-end ✓.

## Notes for follow-up

- None. Full `default` build (pkg + runtime) with tests green; the conversion is a faithful port of the original flat recipe.