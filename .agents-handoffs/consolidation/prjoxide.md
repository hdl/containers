# Consolidation: `prjoxide`

## What was converted

`debian/prjoxide.dockerfile` → `debian/prjoxide/{Dockerfile,HDLC}`

- `debian/prjoxide.dockerfile` was **deleted**.
- `debian/prjoxide/HDLC` holds the build recipe (bash, sourced inside the build via `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build`).
- `debian/prjoxide/Dockerfile` is the unified single-file recipe; pyHDLC resolves image `prjoxide` → `debian/prjoxide/Dockerfile` with build context `debian/prjoxide` (its own directory).
- Image name unchanged (`debian/bullseye/prjoxide`); no changes to `test/`, `images.yml`, or `jobs.yml`.

## HDLC layout

Build-only recipe. Structurally:

- `makedepends`: **absent** — `rustup.sh` self-installs the Rust toolchain into `$HOME` (no `apt-get` for build deps in the build stage).
- `build()`: `curl sh.rustup.rs` → `source "$HOME/.cargo/env"` → `git clone --recurse-submodules prjoxide` → `cargo install --path prjoxide --root /opt/prjoxide/usr/local`. The `curl`/`git`/build essentials come from the `build/build` base image.
- `depends`: **absent** — runtime image is `build/base` with the prefix-COPY `/opt/prjoxide`; prjoxide is a fully static-cargo binary needing no runtime packages.
- No `FROM scratch AS version` stage (the original had none).
- No `ARG IMAGE` (the original had none).

## Dry-run output

`pyHDLC -n build -a amd64 -c debian/bullseye -d prjoxide`:

```
Read images configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/images.yml (HDLC v0)
Read jobs configuration file /home/umarcor/ghdl-hdlc/utils/pyHDLC/jobs.yml (HDLC v0)
· docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/prjoxide --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/prjoxide
```

Note: no `-f` flag is emitted because `debian/prjoxide/Dockerfile` sits at the root of the build context (`Dockerfile` has no suffix, so pyHDLC's `-f`-only-if-suffix logic skips it — `utils/pyHDLC/__init__.py:444-462`). The context resolves to the tool's own directory, which is what makes the `/tmp/ctx/HDLC` bind-mount work.

## Real build result: PASS

`pyHDLC build -a amd64 -c debian/bullseye -d prjoxide -q` exited 0.

- Build stage: rustup 1.98.1 installed in ~19s; prjoxide v0.1.0 compiled (release) and installed to `/opt/prjoxide/usr/local/bin/prjoxide` in ~25s. Only upstream lifetime-elision warnings.
- `FROM scratch AS pkg`: `COPY --from=build /opt/prjoxide /prjoxide`.
- Runtime stage: `COPY --from=build /opt/prjoxide /` onto `build/base`.
- Test (`-q`) PASS: `docker run ... ghcr.io/hdl/amd64/debian/bullseye/prjoxide //wrk/prjoxide.sh` → `prjoxide help: exit code 0 | OK` (remaining `_todo.sh` placeholder "Ops! This test is not complete yet.").
- Image: amd64, size 200259041 bytes (~200 MB).

Version note: upstream `cargo install` reports `prjoxide v0.1.0`; the recipe has no version stage, so no `dist/hdlc.prjoxide.version` is produced (matches the original recipe).