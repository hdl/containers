# Audit: `nextpnr-prjs` on `debian/bullseye` (amd64)

- **Task**: `nextpnr-prjs`
- **Images** (9): `pkg/nextpnr/ice40`, `nextpnr/ice40`, `nextpnr/icestorm`, `pkg/nextpnr/ecp5`, `nextpnr/ecp5`, `nextpnr/prjtrellis`, `pkg/nextpnr/nexus`, `nextpnr/nexus`, `nextpnr/prjoxide`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev` (`8761c15` "AGENTS.md: document _anchors as loader-only config scaffolding")
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl` (`ghcr.io/hdl/amd64/debian/bullseye`)
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script); log to `audits/logs/nextpnr-prjs.log`
- **Log**: `audits/logs/nextpnr-prjs.log`

## Overall result: FAIL

All 9 images fail at the per-arch `cmake ..` configure step of `debian-bullseye/nextpnr.dockerfile`
with the identical error: the freshly cloned (unpinned) nextpnr `master` `CMakeLists.txt:5` requires
CMake >= 3.25, but the `build/nextpnr/build` build image ships Debian bullseye's system CMake 3.18.4.
Builds abort before `make`/install, so `test=True` never runs a test. Exit status of the audit
harness: 1.

The upstream dependency `nextpnr-build` (`build/nextpnr/base`, `build/nextpnr/build`) **PASSES**
(unrelated prior audit log `audits/logs/nextpnr-build.log`, RESULT: PASS) because its `build`
stage only clones the source and installs `libeigen3-dev`/`libomp-dev` — it never invokes `cmake`.

---

## `pkg/nextpnr/ice40` — FAIL

Command (from log line 5):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/nextpnr/ice40 \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target pkg-ice40 \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1 (`subprocess.CalledProcessError` rethrown by `BuildImage`, `utils/pyHDLC/__init__.py:456`).

Symptoms / error lines:
```
#8 [build-ice40 3/3] RUN cd /tmp/nextpnr/build && cmake .. -DARCH=ice40 -DBUILD_GUI=OFF -DBUILD_PYTHON=ON -DUSE_OPENMP=ON && make && make DESTDIR=/opt/nextpnr install
#8 0.303 CMake Error at CMakeLists.txt:5 (cmake_minimum_required):
#8 0.303   CMake 3.25 or higher is required.  You are running version 3.18.4
#8 ERROR: process ... did not complete successfully: exit code: 1
```

## `nextpnr/ice40` — FAIL

Command (log line 82):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/nextpnr/ice40 \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target ice40 \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Identical error in `#10 [build-ice40 3/3]` — CMake 3.25 required, 3.18.4 present.

## `nextpnr/icestorm` — FAIL

Command (log line 166):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/nextpnr/icestorm \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target icestorm \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Identical error in `#10 [build-ice40 3/3]`.

## `pkg/nextpnr/ecp5` — FAIL

Command (log line 250):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/nextpnr/ecp5 \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target pkg-ecp5 \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Error in `#8 [build-ecp5 3/3]` — same CMake version mismatch
(`CMakeLists.txt:5`, `3.18.4 < 3.25`).

## `nextpnr/ecp5` — FAIL

Command (log line 327):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/nextpnr/ecp5 \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target ecp5 \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Error in `#10 [build-ecp5 3/3]` — same CMake version mismatch.

## `nextpnr/prjtrellis` — FAIL

Command (log line 412):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/nextpnr/prjtrellis \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target prjtrellis \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Error in `#10 [build-ecp5 3/3]` (reuses the ecp5 build stage) — same CMake version mismatch.

## `pkg/nextpnr/nexus` — FAIL

Command (log line 500):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/nextpnr/nexus \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target pkg-nexus \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Error in `#8 [build-nexus 3/3]` — same CMake version mismatch.

## `nextpnr/nexus` — FAIL

Command (log line 577):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/nextpnr/nexus \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target nexus \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Error in `#10 [build-nexus 3/3]` — same CMake version mismatch.

## `nextpnr/prjoxide` — FAIL

Command (log line 661):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/nextpnr/prjoxide \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target prjoxide \
  -f debian-bullseye/nextpnr.dockerfile debian-bullseye
```

Exit status: 1. Error in `#10 [build-nexus 3/3]` (reuses the nexus build stage) — same CMake version mismatch.

---

## Root-cause hypothesis

**Recipe / upstream-drift (a dependency bump the recipe has not absorbed)** — not a test problem,
not the registry, not a broken environment.

- `debian-bullseye/nextpnr.dockerfile:48` clones **unpinned** upstream master:
  `git clone --recursive https://github.com/YosysHQ/nextpnr.git /tmp/nextpnr` (intentional per repo
  policy — continuous testing of upstream `main`). Upstream `master` `CMakeLists.txt:5` now reads
  `cmake_minimum_required(VERSION 3.25)`.
- Every per-arch build stage (`build-ice40`, `build-ecp5`, `build-nexus`) is
  `FROM $REGISTRY/build/nextpnr/build`, i.e. the image produced by the (passing) `nextpnr-build`
  task. That image carries bullseye's system CMake:
  `cmake version 3.18.4` (`3.18.4-2+deb11u1`), verified by
  `docker run ... ghcr.io/hdl/amd64/debian/bullseye/build/nextpnr/build:latest cmake --version`.
  3.18.4 < 3.25 → hard failure at the `cmake_minimum_required` check, before anything else runs.
- CMake is sourced from the distro package `cmake` in the shared base
  (`debian-bullseye/base.dockerfile:60`); bullseye's archive offers **no** newer cmake (apt-cache
  candidate = installed = `3.18.4-2+deb11u1`), so there is no pure-apt path to >= 3.25 on bullseye.
- Blast radius is bullseye-only: `debian-bookworm/nextpnr.dockerfile` exists and bookworm's
  `build/nextpnr/build` ships `cmake 3.25.1` (verified locally), which satisfies the requirement.
  `nextpnr-prjs` is wired to `*SysDebianLegacyAmd64` in `utils/pyHDLC/jobs.yml:187` (bullseye +
  bookworm, amd64). `nextpnr` is not built for trixie.
- Environment is otherwise healthy: registry base images (`pkg/icestorm`,
  `pkg/prjtrellis`, `pkg/prjoxide`, `build/nextpnr/base`, `build/nextpnr/build`) all resolved/loaded,
  apt and `COPY --from` steps completed, and `nextpnr-build` passed just before in the audit series.

## Investigation notes

- `job_images('nextpnr-prjs')` → the 9 images above; the order attempted matches `jobs.yml`
  (`${arch}` first, then `${prj}`).
- The CMake error is emitted within 0.3 s of the configure RUN starting, i.e. it is the very first
  sanity check of `CMakeLists.txt` — the `-DARCH=ice40/ecp5/nexus` specific work never begins.
- All failure records in the log are `=== FAIL <img> (CalledProcessError: ... returned non-zero exit status 1.) ===` preceded by the matching `#N ERROR: ... failed to solve` block; `trailing traceback` shows `utils/pyHDLC/__init__.py` `BuildImage` → `_exec` → `subprocess.check_call`.
- Because configure aborts, `make`, `make DESTDIR=/opt/nextpnr install` and the `scratch`
  package copies never run → `pkg/nextpnr/*` and the runtime `nextpnr/*` images all die at the
  identical spot; no `test/` script executed for any image.

## Recommended next step

Provide CMake >= 3.25 in the bullseye build image for nextpnr (bullseye's apt has no such version):

1. **Preferred**: in `debian-bullseye/nextpnr.dockerfile`, add a CMake bootstrap to the `build`
   stage (the one that installs `libeigen3-dev`/`libomp-dev`): install `python3-pip` and
   `python3 -m pip install cmake` (pip wheels ship modern CMake). This `build` stage defines
   `build/nextpnr/build`, so the fix automatically reaches all `build-*` stages. The
   `python3-pip`+`pip install` pattern already exists in bullseye recipes
   (`debian-bullseye/formal.dockerfile:39-42`, `debian-bullseye/apicula/HDLC:29`). Confirm the
   pip-installed `cmake` wins over `/usr/bin/cmake` (e.g. install to a prefix and prepend `PATH`,
   or `pip install cmake` in bullseye places a `cmake` shim in `~/.local/bin`/`/usr/local/bin`).
2. **Alternative (cookbook-style)**: ship a pinned CMake binary (Kitware tarball) under
   `/opt/cmake` in the `build` stage and prepend it to `PATH`.
3. **Fallback**: pin `/tmp/nextpnr` clone to a commit/tag predating the 3.25 bump — but this
   contradicts the repo's unpinned-clone policy and would stop testing upstream `master`.

Re-run this exact audit heredoc afterwards; all 9 images must reach `=== PASS <img> ===` (which
requires the build to complete and `test/nextpnr--ice40.sh` etc. to run inside the containers —
untested here because configure aborts).