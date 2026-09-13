# Handoff: convert `debian/sby.dockerfile` → `debian/sby/`

## What was converted

Flat recipe `debian/sby.dockerfile` was converted to the HDLC subdirectory pattern:

- `debian/sby/HDLC` — the build logic (makedepends array + `build()` function), sourced inside each `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC` instruction.
- `debian/sby/Dockerfile` — the build recipe, now consuming the HDLC script.
- `debian/sby.dockerfile` was **deleted**.

The image name remains `debian/bullseye/sby`. No changes to `test/`, `images.yml`, or `jobs.yml`.

## HDLC layout

```
# HDLC sby
...
set -e

makedepends=( binutils g++ make python3-setuptools )

build() {
  mkdir /tmp/sby && cd /tmp/sby
  curl -fsSL https://codeload.github.com/YosysHQ/sby/tar.gz/main | tar xzf - --strip-components=1
  make DESTDIR=/opt/sby install
}
```

- `makedepends`: `binutils`, `g++`, `make`, `python3-setuptools`.
- `build()`: downloads sby tarball, `make DESTDIR=/opt/sby install`.
- No `depends`, no runtime image stage (matches original: pkg-only).
- No `FROM scratch AS version` stage and no `ARG IMAGE` (original had neither).
- Final stage is `FROM scratch; COPY --from=build /opt/sby /sby` — the resulting image is the scratch/"pkglike" image only. Note: this stage is an **unnamed** `FROM scratch` (no `AS pkg`), mirroring the original flat file.

## Dry-run output

`pyHDLC -n build -a amd64 -c debian/bullseye -d sby` produced:

```
· docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/sby --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/sby
```

- Context resolves to `debian/sby` ✓
- No explicit `-f` flag is emitted. This is expected: pyHDLC only adds `-f` when the dockerfile path has a suffix (see `__init__.py:462`, `*(["-f", str(dockerfilePath)] * bool(dockerfilePath.suffix))`). A subdirectory recipe is `<context>/Dockerfile` with no suffix, so docker uses it as the default Dockerfile name. Behavior is identical to the already-consolidated `irsim` (verify with `pyHDLC -n build -a amd64 -c debian/bullseye -d irsim`).
- Only one build step is printed (the `version` export step of tools like `irsim` is absent because sby has no version stage).

## Real build result

`pyHDLC build -a amd64 -c debian/bullseye -d sby -q`:

**Build: PASS**

- Stage `build 2/3` (`RUN . /tmp/ctx/HDLC && apt-get install ${makedepends[@]} ...`): makedepends installed successfully (37 packages).
- Stage `build 3/3` (`RUN . /tmp/ctx/HDLC && build`): sourced HDLC correctly, `build()` ran — sbysrc python files copied to `/opt/sby/usr/local/share/yosys/python3/`, `sby` script generated at `/opt/sby/usr/local/bin/sby` (`SBY v0.69`).
- `stage-1 (FROM scratch)` `COPY --from=build /opt/sby /sby` succeeded.
- Image `ghcr.io/hdl/amd64/debian/bullseye/sby:latest` exported. Size: 348947 bytes.

The mechanical step of sourcing `debian/sby/HDLC` worked end-to-end ✓.

**Test: FAIL** (expected, not a build problem)

```
· docker run --rm -v /home/umarcor/ghdl-hdlc/test://wrk ghcr.io/hdl/amd64/debian/bullseye/sby //wrk/sby.sh
docker: Error response from daemon: ... exec: "//wrk/sby.sh": stat //wrk/sby.sh: no such file or directory
```

There is no `test/sby.sh` script. Adding one was out of scope for this conversion (task states test/ scripts are not to be touched). `pyHDLC` aborted with `CalledProcessError` 127 after the successful build.

## Notes for follow-up

- If a `test/sby.sh` is desired, it would follow the standard pattern (source `test/_env.sh`, call `./smoke-tests/sby.sh` if present in the submodule, then `./_todo.sh`).
- The current image is pkg-only content at `/sby` (scratch). The original flat recipe had the same structure, so this is a faithful conversion.