# Verilator consolidation

## Converted

`debian/verilator.dockerfile` → `debian/verilator/Dockerfile` + `debian/verilator/HDLC` (flat file deleted).

## HDLC layout

- `makedepends`: `autoconf bison flex help2man libfl-dev`
- `build()`: git clone verilator; `cd verilator`; `autoconf`; `./configure`; `make -j$(nproc)`; `make DESTDIR=/opt/verilator install`; then git clone `veripool/vcddiff` (from inside the verilator dir, preserving the exact relative-path behavior, no extra `cd`); `make -C vcddiff CC=$CC`; `cp -p vcddiff/vcddiff /opt/verilator/usr/local/bin/vcddiff`.
- `depends`: `clang make perl`
- No `FROM scratch AS version` stage (original has none).
- `ARG IMAGE="build/base"` preserved; runtime stage uses `FROM $REGISTRY/$IMAGE`; `CMD ["verilator"]`.
- Follows the irsim HDLC/Dockerfile conventions: `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC` in each stage, `${makedepends[@]}`/`${depends[@]}` on the `apt-get install` line, `COPY --from=build /opt/verilator /` for runtime and `/verilator` for the `FROM scratch AS pkg` stage.

## Dry-run (`pyHDLC -n build -a amd64 -c debian/bullseye -d verilator`)

```
Read images configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/images.yml (HDLC v0)
Read jobs configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/jobs.yml (HDLC v0)
· docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/verilator --build-arg REGISTRY=ghdl/hdl/amd64/... 
```

Actual emitted command:

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/verilator --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/verilator
```

Notes:

- Context resolves to `debian/verilator` (the tool's own dir), with the Dockerfile inside, so no `-f` flag is emitted (pyHDLC only passes `-f` when the dockerfile name has a suffix other than `Dockerfile`, see `__init__.py` `_NormaliseBuildParams`/`BuildImage`).
- No `--build-arg IMAGE=build/base` is emitted because verilator has no `images.yml` entry (`argimg` is `None`); the value is supplied by the dockerfile default `ARG IMAGE="build/base"`, so the runtime stage still resolves to `build/base` — functionally identical.

## Real build (`pyHDLC build -a amd64 -c debian/bullseye -d verilator -q`): FAIL

The build stage did not complete (test never ran). The conversion mechanics worked end to end: HDLC sourced in stage 2, makedepends installed (`autoconf bison flex help2man libfl-dev`), `git clone` + `autoconf` + `./configure` succeeded, and `make -j$(nproc)` compiled hundreds of objects before failing.

### Error summary

Upstream verilator master fails to build under the bulleye `clang++` (build/base sets `CC=clang`):

- `make[2]` in `/verilator/src/obj_dbg` and `/verilator/src/obj_opt` → `Error 1`
- Root cause, e.g. `V3ClassGraph.cpp:196:24: error: call to implicitly-deleted default constructor of 'V3ClassGraph'`
- `V3ClassGraph.h:43:5: note: explicitly defaulted function was implicitly deleted here` — `V3ClassGraph() = default;`
- `V3ClassGraph.h:41:9: note: default constructor ... deleted because field 'm_emptySet' of const-qualified type 'const std::unordered_set<AstCFunc *>' would not be initialized`

This is a source-level incompatibility of current verilator master with the compiler/standard-library used, not a conversion artifact: the original `debian/verilator.dockerfile` runs the exact same commands with the same `CC=clang`, so it would fail identically. Untouched: `test/verilator.sh`, `images.yml`, `jobs.yml`, and the image name `debian/bullseye/verilator`.

No retries performed (per task instructions).