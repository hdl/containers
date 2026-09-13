# Audit: `xyce` on `debian/bullseye` (amd64)

- **Task**: `xyce`
- **Images**: `pkg/xyce`, `xyce`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev`
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script).
- **Log**: `audits/logs/xyce.log`
- **Audit runner exit**: 1 (`RESULT: FAIL`)

## Overall result: FAIL

`pkg/xyce` fails at the Xyce build step because upstream Xyce master no longer ships the autotools `bootstrap` script — the project has migrated to CMake. The runtime `xyce` image assembles from a stale **pre-published** `pkg/xyce` in the registry (bypassing the local build failure), so it builds and its smoke test passes, but the pkg artifact itself cannot be rebuilt.

Matrix as returned by `job_images('xyce')` → `['pkg/xyce', 'xyce']`, matching `jobs.yml:108` (`xyce: *SysDebianLegacyAmd64`, i.e. bullseye/amd64). `xyce` is not in `images.yml`, so the dockerfile resolves to `debian-bullseye/xyce.dockerfile` and the default `pkg` target.

---

## `pkg/xyce` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 42226):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/xyce \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  --target pkg -f debian-bullseye/xyce.dockerfile debian-bullseye
```

Exit status: 1 (`CalledProcessError` from `docker build`); the in-image step `[build 7/7]` failed with exit code 127. Logged as `=== FAIL pkg/xyce ... ===` (log line 42206).

Symptoms / error lines (log lines 42175-42181):

```
#10 [build 7/7] RUN cd Xyce && ./bootstrap  && mkdir xyce-build && cd xyce-build  && ...
#10 0.224 /bin/bash: line 1: ./bootstrap: No such file or directory
#10 ERROR: process "/bin/bash -c cd Xyce && ./bootstrap ..." did not complete successfully: exit code: 127
------
 > [build 7/7] RUN cd Xyce && ./bootstrap ...
107 | >>> RUN cd Xyce && ./bootstrap \
108 | >>>  && mkdir xyce-build && cd xyce-build \
...
------
```

Preceding stages healthy:
- `[build 1/7]` FROM `ghcr.io/hdl/amd64/debian/bullseye/build/build:latest` — CACHED.
- `[build 2/7]` apt-get of build-deps (autoconf, automake, bison, cmake, gfortran, libfftw3-dev, libsuitesparse-dev, libblas-dev, liblapack-dev, libtool) — all fetched from `snapshot.debian.org` (`20260824T000000Z` pin); no apt 404s. EOL bullseye-mirror problem is NOT involved.
- `[build 3/7]` `WORKDIR /tmp/build/` — OK.
- `[build 4/7]` `curl` of Trilinos release tarball (`trilinos-release-12-12-1.tar.gz`) + `tar xz` — OK (3.1s).
- `[build 5/7]` Trilinos cmake + `make DESTDIR=/tmp/xyce/ -j$(nproc) install` — completed in 933.6s; installed all Trilinos libraries and headers into `/tmp/xyce/usr/local/`.
- `[build 6/7]` `curl` of Xyce master tarball + `tar xz` — OK (3.1s); 1901 files extracted into `Xyce/`.
- `[build 7/7]` `cd Xyce && ./bootstrap` — **FAIL** (exit 127). The `Xyce/` directory contains `CMakeLists.txt` at the root but no `bootstrap` script.

---

## `xyce` — PASS

Exact `docker build` as resolved by `BuildImage` (log line 42226):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/xyce \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  -f debian-bullseye/xyce.dockerfile debian-bullseye
```

Exit status: 0. Docker build completed in ~26s. The runtime stage pulled the **pre-published** `pkg/xyce` from the registry (`FROM ghcr.io/hdl/amd64/debian/bullseye/pkg/xyce:latest@sha256:92da97af86d7a9c01c8b317bd8ccf1d0af367f186b4caa04cbbaa0891440e3e0`), not from the failed local build. The runtime dockerfile (`debian-bullseye/xyce.dockerfile:129`) declares `FROM $REGISTRY/pkg/xyce AS pkg-xyce`, which resolves to the **registry** image, so the local `pkg/xyce` build failure is invisible to the runtime stage.

Test result (log lines 42398-42403):

```
docker run --rm -v .../test://wrk ghcr.io/hdl/amd64/debian/bullseye/xyce //wrk/xyce.sh
CC:
CXX:
/usr/local/bin/Xyce
Xyce DEVELOPMENT-202408090219-opensource
Ops! This test is not complete yet.
Submit a PR! https://github.com/hdl/containers/compare
```

The smoke test passes, but it is a **placeholder** (`Ops! This test is not complete yet.`) — no meaningful functional verification is performed. The `xyce` runtime image is buildable only because it is backed by a stale published `pkg/xyce` from a prior CI run when `bootstrap` still existed.

---

## Root-cause hypothesis

**Recipe** (upstream drift vs. the pinned recipe), not test, not deps, not env.

`debian-bullseye/xyce.dockerfile:107` invokes `cd Xyce && ./bootstrap`:

```
RUN cd Xyce && ./bootstrap \
 && mkdir xyce-build && cd xyce-build \
 && xyceBuildDir=/opt/Xyce/xyce-build/ \
 && ../configure \
      CXXFLAGS="-O3" \
      LDFLAGS="-Wl,-rpath=$xyceBuildDir/utils/XyceCInterface -Wl,-rpath=$xyceBuildDir/lib" \
      CPPFLAGS="-I/usr/include/suitesparse" \
      ARCHDIR=$XYCE_OUTDIR \
      --enable-shared \
      --enable-xyce-shareable \
      --enable-stokhos \
      --enable-amesos2 \
 && make DESTDIR=/tmp/xyce/ -j$(nproc) install
```

Upstream Xyce master (`Xyce/Xyce`) has migrated from autotools to CMake. A live check of the master tarball (1901 files) confirms:
- **No `bootstrap` script** at any path.
- **No `configure.ac`** or `configure` at any path.
- **45 `CMakeLists.txt` files** across the tree, with the root `CMakeLists.txt` being the build entry point.

The recipe fetches `https://codeload.github.com/Xyce/Xyce/tar.gz/master` (line 102-104) without any commit/branch pin, so it tracks upstream `main` continuously — exactly the repo's intended design. When Xyce's build system changed from autotools to CMake, the `bootstrap` invocation became a dead reference (exit 127 = command not found).

This is the repo's intentional unpinned-`main` design (AGENTS.md) catching upstream drift: a Xyce change migrating the build system from autotools to CMake, vs. a recipe last written when autotools was still in use.

---

## Investigation notes

- `job_images('xyce')` → `['pkg/xyce', 'xyce']`; `jobs.yml:108` wires xyce to `*SysDebianLegacyAmd64` (bullseye/amd64 only; no bookworm/trixie/riscv64 variant; the dockerfile lives in `debian-bullseye/`).
- `debian-bullseye/xyce.dockerfile` has no HDLC/`debian/xyce/` counterpart — all build steps are inline (lines 28-119), not `RUN .HDLC && build`.
- The pre-published `pkg/xyce` image in the registry (`92da97af...`) was built at a time when Xyce master still had the `bootstrap` script. Its contents are still valid for the runtime image's `COPY --from=pkg-xyce /xyce/ /`, but cannot be regenerated.
- The test script (`test/xyce.sh`) is a placeholder — it runs `smoke-tests/xyce.sh` which prints version + "Ops! This test is not complete yet." No real functional test is performed.
- Trilinos build (step 5/7) completed successfully in 933.6s; the failure is isolated to the Xyce build step.

## Recommended next step

Rewrite the Xyce build step in `debian-bullseye/xyce.dockerfile:107-119` to use CMake instead of the removed autotools `bootstrap`/`configure` flow. The current step:

```dockerfile
RUN cd Xyce && ./bootstrap \
 && mkdir xyce-build && cd xyce-build \
 && xyceBuildDir=/opt/Xyce/xyce-build/ \
 && ../configure \
      CXXFLAGS="-O3" \
      LDFLAGS="-Wl,-rpath=$xyceBuildDir/utils/XyceCInterface -Wl,-rpath=$xyceBuildDir/lib" \
      CPPFLAGS="-I/usr/include/suitesparse" \
      ARCHDIR=$XYCE_OUTDIR \
      --enable-shared \
      --enable-xyce-shareable \
      --enable-stokhos \
      --enable-amesos2 \
 && make DESTDIR=/tmp/xyce/ -j$(nproc) install
```

...should be replaced with an equivalent CMake build. The Xyce CMake configuration exposes options like `-DXyce_STOKHOS=ON`, `-DXyce_AMESOS2=ON`, etc. Exact flag mapping requires reading Xyce's root `CMakeLists.txt` and any `cmake/` option definitions. Check the [Xyce CMake documentation](https://github.com/Xyce/Xyce) for the current list of build options.

Also consider whether the `autoconf`, `automake`, `libtool` packages in the makedepends (line 29-44) are still needed once the build is migrated to CMake, since the autotools-based `bootstrap` script is gone. The `cmake` package is already listed as a build dependency. Re-run the same audit command; both images must reach `=== PASS pkg/xyce ===` and `=== PASS xyce ===`, which would also exercise the (still-placeholder) `test/xyce.sh`.
