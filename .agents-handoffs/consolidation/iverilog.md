# Handoff: convert `debian/iverilog.dockerfile` → `debian/iverilog/`

## What was converted

Flat recipe `debian/iverilog.dockerfile` was converted to the HDLC subdirectory pattern:

- `debian/iverilog/HDLC` — the build logic (makedepends/depends arrays + `build()` function), sourced inside each `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC` instruction.
- `debian/iverilog/Dockerfile` — the build recipe, now consuming the HDLC script.
- `debian/iverilog.dockerfile` was **deleted**.

The image name remains `debian/bullseye/iverilog`. No changes to `test/`, `images.yml`, or `jobs.yml`.

## HDLC layout

```
# HDLC iverilog
...
set -e

makedepends=( autoconf automake bison flex gperf libreadline-dev zlib1g-dev )

build() {
  git clone https://github.com/steveicarus/iverilog /tmp/iverilog
  cd /tmp/iverilog
  autoconf
  ./configure
  make -j$(nproc) check
  make DESTDIR=/opt/iverilog install
}

depends=( perl )
```

- `makedepends`: `autoconf`, `automake`, `bison`, `flex`, `gperf`, `libreadline-dev`, `zlib1g-dev`.
- `build()`: clones iverilog, `autoconf`, `./configure`, `make -j$(nproc) check` (preserved exactly), then `make DESTDIR=/opt/iverilog install`.
- `depends`: `perl` (runtime image installs it).
- No `FROM scratch AS version` stage and no `ARG IMAGE` (original had neither).
- Runtime stage ends with `CMD ["iverilog"]` on `$REGISTRY/build/base` — preserved from the original.

## Dry-run output

`pyHDLC -n build -a amd64 -c debian/bullseye -d iverilog` produced:

```
· docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/iverilog --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/iverilog
```

- Context resolves to `debian/iverilog` ✓
- No explicit `-f` flag is emitted. This is expected: pyHDLC only adds `-f` when the dockerfile path has a suffix (see `__init__.py:462`, `*(["-f", str(dockerfilePath)] * bool(dockerfilePath.suffix))`). A subdirectory recipe is `<context>/Dockerfile` with no suffix, so docker uses it as the default Dockerfile name. Behavior is identical to the already-consolidated `irsim` (compare with the flat `gnuplot`: `-f debian/gnuplot.dockerfile debian`).
- No `version` export step is printed because iverilog has no `FROM scratch AS version` stage.

## Real build result

`pyHDLC build -a amd64 -c debian/bullseye -d iverilog -q`:

**Build: PASS**

- Stage `build 2/3` (`RUN . /tmp/ctx/HDLC && apt-get install ${makedepends[@]} ...`): makedepends installed successfully from the sourced HDLC.
- Stage `build 3/3` (`RUN . /tmp/ctx/HDLC && build`): sourced HDLC correctly, `build()` ran end-to-end — git clone, `autoconf`, `./configure`, `make -j$(nproc) check`, then `make DESTDIR=/opt/iverilog install` (iverilog + iverilog-vpi installed under `/opt/iverilog/usr/local/bin/`).
- `stage-1 (FROM scratch)` `COPY --from=build /opt/iverilog /iverilog` succeeded.
- Runtime stage installed `depends` (`perl`), `COPY --from=build /opt/iverilog /`, `CMD ["iverilog"]`.
- Image `ghcr.io/hdl/amd64/debian/bullseye/iverilog:latest` exported (manifest sha256:17b498fa99092306af9a9b0ba30ec848d2743b1a5885e14704ba37fdd340f2ad). Size: 308214282 bytes, Architecture amd64.

**Test: PASS**

```
· docker run --rm -v /home/umarcor/ghdl-hdlc/test://wrk ghcr.io/hdl/amd64/debian/bullseye/iverilog //wrk/iverilog.sh
· iverilog help: exit code 1 | OK
· iverilog-vpi help: exit code 0 | OK
· vvp help: exit code 0 | OK
```

ivtest smoke tests passed (`iverilog help` exit 1 is expected), then `_todo.sh` placeholder ran. The mechanical step of sourcing `debian/iverilog/HDLC` worked end-to-end ✓.

## Notes for follow-up

- None. Full `default` build (pkg + runtime) with tests green; the conversion is a faithful port of the original flat recipe.