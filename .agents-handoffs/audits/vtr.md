# Audit: `vtr` on `debian/bullseye` (amd64)

- **Task**: `vtr`
- **Images**: `pkg/vtr`, `vtr`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev`
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script).
- **Log**: `audits/logs/vtr.log`
- **Audit runner exit**: 1 (`RESULT: FAIL`)

## Overall result: FAIL

Both images fail in the same Dockerfile build step `debian-bullseye/vtr.dockerfile:49` (`git clone` + cmake configure/build), at the `cmake -G "Ninja" ... ..` configure call, because the VTR repo is cloned **without** `--recursive` and its `libs/EXTERNAL/*` git submodules are therefore absent at configure time. Tests never run.

Matrix as returned by `job_images('vtr')` → `['pkg/vtr', 'vtr']`, matching `jobs.yml:106` (`vtr: *SysDebianBullseyeAmd64`, i.e. bullseye/amd64 only, consistent with the per-repo note that vtr is pinned to bullseye-amd64). `vtr` is not in `images.yml`, so both dockerfile/target resolve by default (`debian-bullseye/vtr.dockerfile`, no custom target for the `pkg` build other than the stage of the same name).

---

## `pkg/vtr` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 5):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/vtr \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  --target pkg -f debian-bullseye/vtr.dockerfile debian-bullseye
```

Exit status: 1 (`CalledProcessError` from `docker build`); the in-image step `[build 3/3]` failed with exit code 1. Logged as `=== FAIL pkg/vtr ... ===` (log line 1688).

Symptoms / error lines (log lines 1647-1740, `#6`):

```
CMake Error at libs/EXTERNAL/CMakeLists.txt:11 (add_subdirectory):
  The source directory /tmp/vtr/libs/EXTERNAL/libsdcparse does not contain a CMakeLists.txt file.
CMake Error at libs/EXTERNAL/CMakeLists.txt:14 (add_subdirectory):
  The source directory /tmp/vtr/libs/EXTERNAL/libcatch2 does not contain a CMakeLists.txt file.
CMake Error at libs/EXTERNAL/CMakeLists.txt:16 (add_subdirectory):
  The source directory /tmp/vtr/libs/EXTERNAL/yaml-cpp does not contain a CMakeLists.txt file.
CMake Error at libs/EXTERNAL/CMakeLists.txt:40 (add_subdirectory):
  The source directory /tmp/vtr/libs/EXTERNAL/sockpp does not contain a CMakeLists.txt file.
...
CMake Error at libs/EXTERNAL/CMakeLists.txt:186 (target_include_directories):
  Cannot specify include directories for target "Catch2" which is not built by this project.
CMake Error at libs/EXTERNAL/CMakeLists.txt:195 (target_include_directories):
  Cannot specify include directories for target "sockpp-static" which is not built by this project.
...
-- Configuring incomplete, errors occurred!
ERROR: process "/bin/bash -c git clone .../vtr-verilog-to-routing.git /tmp/vtr  && mkdir -p /tmp/vtr/build && cd /tmp/vtr/build && cmake -G \"Ninja\" -DCMAKE_INSTALL_PREFIX=\"/usr/local\" .. && cmake --build ./ && DESTDIR=/opt/vtr cmake --build ./ --target install" did not complete successfully: exit code: 1
```

Preceding stages healthy:
- `[build 2/3]` makedepends install OK (bison, build-essential, cmake, flex, fontconfig, gperf, libcairo2-dev, libgtk-3-dev, libfontconfig1-dev, liblist-moreutils-perl, libreadline-dev, libx11-dev, libxft-dev, ninja-build, tcl-dev, wget) — all fetched from `snapshot.debian.org`, no apt 404s. The bullseye-EOL mirror problem is NOT involved.
- `git clone` of VTR `main` OK (`v8.0.0-18148-ge422b08861`, 13937 files); the non-recursive clone leaves the `libs/EXTERNAL/{libsdcparse,libcatch2,yaml-cpp,sockpp,libezgl,yosys,yosys-slang}` submodule dirs empty.
- Mid-configure, VTR's own CMake self-heal (`git submodule update --init --recursive`, log lines 1698-1724) DID clone all submodules (libcatch2 @`317ac1ed` = **Catch2 3.16.0**, sockpp @`599f750`, the rest likewise) — but too late: those `add_subdirectory` calls had already failed in the same configure pass, so the later unconditional `target_include_directories(Catch2 ...)` (line 186) and `target_include_directories(sockpp-static ...)` (line 195) raise "not built by this project" and configure ends `Configuring incomplete`.

---

## `vtr` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 1708):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/vtr \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  -f debian-bullseye/vtr.dockerfile debian-bullseye
```

Exit status: 1 (`CalledProcessError` from `docker build`); the in-image step `[build 3/3]` failed with exit code 1. Logged as `=== FAIL vtr ... ===` (log line 2019).

Symptoms / error lines — identical to `pkg/vtr` (second independent configure, log lines 1852-2011, `#8`): the same four `add_subdirectory ... does not contain a CMakeLists.txt file` (libsdcparse/libcatch2/yaml-cpp/sockpp), the same mid-configure submodule self-heal on the pinned commits, then the same final `target_include_directories(Catch2)` / `target_include_directories(sockpp-static)` failures and `-- Configuring incomplete, errors occurred!`. Dockerfile:49 `>>>` dump shown in the error block matches exactly. The runtime stage's `libgtk-3-bin` install never ran (CANCELED once the build step failed).

---

## Root-cause hypothesis

**Recipe** (upstream drift vs. the pinned-to-legacy `debian-bullseye/vtr.dockerfile`), not test, not deps, not env.

`debian-bullseye/vtr.dockerfile:49` clones VTR **without** `--recursive`:

```
RUN git clone https://github.com/verilog-to-routing/vtr-verilog-to-routing.git /tmp/vtr \
 && mkdir -p /tmp/vtr/build \
 && cd /tmp/vtr/build \
 && cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="/usr/local" .. \
 ...
```

Current VTR upstream `main` (clone = `v8.0.0-18148-ge422b08861`) requires its `libs/EXTERNAL/*` submodules to be present **at CMake configure time**: `libs/EXTERNAL/CMakeLists.txt` (verified live at that commit) does `add_subdirectory(libsdcparse)` (line 11), `add_subdirectory(libcatch2)` (line 14), `add_subdirectory(yaml-cpp)` (line 16) and, under `VPR_USE_SERVER`, `add_subdirectory(sockpp)` (line 40) — all of which error immediately on an empty submodule dir. VTR's configure-time submodule self-heal (`git submodule update --init --recursive`) runs only *after* those calls have already failed, so the same-pass tail of the file — the **unguarded** `target_include_directories(Catch2 ...)` (line 186) and `target_include_directories(sockpp-static ...)` (line 195) — fails with "Cannot specify include directories for target ... which is not built by this project". Configure ends non-zero, `cmake --build` never starts, step exits 1.

Both pinned submodule targets are confirmed to exist when the subtree is actually present (so the second set of errors is a *consequence* of the missing-submodule first-pass failures, not a second independent upstream break):
- libcatch2 @`317ac1ed` (Catch2 **3.16.0**) — `src/CMakeLists.txt` defines `add_library(Catch2 ...)` and `add_library(Catch2::Catch2 ALIAS Catch2)`.
- sockpp @`599f750` — defines `sockpp-static` when `SOCKPP_BUILD_STATIC ON`, which VTR's `libs/EXTERNAL/CMakeLists.txt` forces right before `add_subdirectory(sockpp)`.

Env facts:
- `ghcr.io/hdl/amd64/debian/bullseye/build/dev:latest@sha256:f928b0f1...` resolved fine from the registry and was reused from cache; network, apt (`snapshot.debian.org`, `20260824T000000Z` pin) and the `git clone` itself all healthy — EOL-mirror or network issues are excluded.
- Secondary (non-fatal) configure notes in the same pass: TBB not found (libtatum → "VPR: will only support serial execution"), TCLTK/TK not found → VPR "graphics disabled"/EZGL off, Eigen3 not found, OpenMP not found (C and CXX) → "OpenMP: Disabled (requested but not found)", OpenSSL not found. All are feature-optional warnings that would degrade the build but not fail it.
- This is the repo's intentional unpinned-`main` design (AGENTS.md) catching upstream drift: a VTR change making submodule initialization mandatory at configure time vs. a recipe last touched by `0fc785e` (2025, registry migration) that predates it.

## Investigation notes

- `job_images('vtr')` → `['pkg/vtr', 'vtr']`; `jobs.yml:106` wires vtr to `*SysDebianBullseyeAmd64` (bullseye/amd64 only — no bookworm/trixie/riscv64 variant; the dockerfile lives in `debian-bullseye/`).
- `debian-bullseye/vtr.dockerfile` has no HDLC/`debian/vtr/` counterpart — the build steps are inline (lines 28-54), not `RUN .HDLC && build`. Fix is a one-spot change in the dockerfile.
- The log shows the submodule self-heal cloning all 7 submodules (including yosys + yosys-slang with nested `fmt` + `slang`) at `#6 91.23-129.7`, i.e. ~37 s of wasted work per image before configure aborts.
- Buildkit backend `fromAsCasing` warning (line 26 `FROM $REGISTRY/build/dev as build`) is cosmetic only.
- `test/vtr.sh` (runs `smoke-tests/vpr.sh` + `smoke-tests/odin_II.sh`) and `test/vtr.pkg.sh` exist, but neither the pkg tests nor the runtime tests were reached for either image.

## Recommended next step

Make the clone recursive in `debian-bullseye/vtr.dockerfile:49`, e.g.:

```
RUN git clone --recursive https://github.com/verilog-to-routing/vtr-verilog-to-routing.git /tmp/vtr \
 && mkdir -p /tmp/vtr/build \
 && cd /tmp/vtr/build \
 && cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="/usr/local" .. \
 ...
```

(this also clones the nested `fmt`/`slang` submodules of `yosys-slang`, matching what the configure-time self-heal wants). Re-run the same audit command; both images must reach `=== PASS pkg/vtr ===` and `=== PASS vtr ===`, which would also exercise `vtr.pkg.sh`/`vtr.sh` for the first time. If configure still trips on `Catch2`/`sockpp-static` with a *recursive* clone, then upstream `main` has a genuine libs/EXTERNAL↔submodule-pin mismatch and the report should be re-raised against upstream; the current evidence says the missing-`--recursive` is the sole blocker.