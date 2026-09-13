# GHDL testsuite.sh — handoff

Status: planning. Integration decisions pending (see "Open decisions").

## Purpose

Run GHDL's upstream testsuite (`testsuite/testsuite.sh`) inside our container
build/test flow, mirroring ghdl/ghdl CI (`Build-Ubuntu.yml` + `Test-GHDL.yml`).

## Upstream pipeline

### Build-Ubuntu.yml (build job, per backend)

- inputs: `ubuntu_version`, `ghdl_backend`, `ghdl_version`, `testsuites`
  (`'all'`/`'none'`/space-separated list), `testsuite_xml_artifact`,
  `ubuntu_artifact`, `libghdl_artifact`, `python_version` (default 3.14),
  `pyunit_testsuites` (default `testsuite/pyunit`), `unittesting` (default
  true), `unittest_xml_artifact`, `coverage` (default true),
  `coverage_sqlite_artifact`.
- job: checkout; setup python (+ pytest for mcode); install deps (`gcc g++ gnat`
  or `+llvm clang` + `libbacktrace(-dev)`); configure (`--with-llvm-config`,
  `--with-backtrace-lib`); make; `make install` to `install/`; `ghdl version`;
  step "🚦 Run testsuite: 'sanity'" (`export
  GHDL=$PWD/install/bin/ghdl; cd testsuite; ./testsuite.sh sanity`); pyunit
  step (mcode only, needs python3 + pytest + `testsuite/requirements.txt`);
  upload artifacts.

### Test-GHDL.yml (test job)

- checkout; download ghdl artifact to `install/`; prepare env: `sudo xargs
  --no-run-if-empty -a ./install/ubuntu.requirements -- apt-get install -y
  --no-install-recommends` (libgnat-N, libllvm-N, gcc, libc-dev, zlib1g-dev);
  `PATH=$PWD/install/bin:$PATH`.
- run: `cd testsuite; ./testsuite.sh sanity gna vests synth vpi vhpi`
  (`testsuites='all'`; comment `# no pyunit`).

### testsuite.sh mechanics

- in repo at `testsuite/testsuite.sh` (bash, `set -e`), sources
  `scripts/bash_toolbox.sh`.
- resolves GHDL via env `GHDL` or `$prefix/bin/ghdl`; requires `diff`
  (diffutils) + GNU coreutils.
- `./testsuite.sh [suite …]` (default set includes pyunit — pass an explicit
  list to skip it); unknown args → exit 2.
- Suites = dirs (`sanity gna vests synth vpi vhpi pyunit`) driven by
  `suite_driver.sh` / `testenv.sh`; `_vests()` = `cd vests; ./testsuite.sh >
  vests.log` (VESTS compliance suite, vendored in-tree).
- Writes JUnit-style `all.testresult` (REPORT_PREFIX + xml_escape).

## This repo's current state

- Recipes `debian-{bullseye,bookworm,trixie}/ghdl/Dockerfile` + `HDLC`:
  build-mcode/
  build-llvm clone ghdl master (`/tmp/ghdl`, unpinned by design), configure
  `--default-pic` + `--with-llvm-config` + per-release backtrace, `make
  GNATMAKE="gnatmake -j$(nproc)"`, `make DESTDIR=/opt/ghdl install`; runtime
  `mcode`/`llvm` `COPY /opt/ghdl /` → ghdl+ghwdump at /bin; `pkg-mcode`/
  `pkg-llvm` → /ghdl.
- Versions: bullseye gnat-9/llvm-11, bookworm gnat-12/llvm-14, trixie
  gnat-14/llvm-19 (+ `ln -s gnatmake-14 gnatmake`); output GHDL 7.0.0-dev
  (6.0.0.r512.g858569681).
- Tests: `test/ghdl.sh`, `test/ghdl--llvm.sh`, `*.pkg.sh` — smoke
  (`_env.sh` + `smoke-tests/ghdl.sh`) + `_todo.sh` placeholder; TODO in
  `test/ghdl.sh`: "get the testsuite matching the version in the container and
  run it".
- ghdl master has NO `.gitmodules` (vests vendored) → plain clone includes
  `testsuite/` (unlike hdl/containers, which pins hdl/smoke-tests).

## Gap analysis vs our mcode/llvm builds

Covered: full-history clone (git describe versioning), deps (gnat-N +
zlib1g-dev; llvm-N-dev/libllvm-N/libbacktrace(-dev); clang via ENV
CC/CXX), configure + install.

Missing:

- [G1] testsuite sources absent in runtime images (build-stage clone discarded).
- [G2] no testsuite execution: neither build-time `sanity` gate nor full
  test-phase run (`sanity gna vests synth vpi vhpi`).
- [G3] mcode runtime lacks vpi/vhpi C deps (gcc, libc-dev, zlib1g-dev);
  llvm runtime has them; `diff`/diffutils unverified on both.
- [G4] pyunit lane (python+pytest+pyGHDL/lib, mcode-only) absent — deferred.
- Cosmetic: `--default-pic` is our clang workaround (upstream defaults gcc);
  `CXX=clang++` comes via ENV, not the configure line.

## Proposed plan

1. **Build-time sanity gate**: in the HDLC `build()` or a dedicated `runtests()`
   function, after `make DESTDIR=/opt/ghdl install`, run
   `cd /tmp/ghdl/testsuite && GHDL=/opt/ghdl/bin/ghdl ./testsuite.sh sanity`
   (+ `diffutils` in `makedepends`). Early failure prevents broken image publication.
   The Dockerfile calls this via `RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && runtests`.
2. **Ship testsuite**: `COPY --from=build-mcode /tmp/ghdl/testsuite
   /opt/ghdl/testsuite` (+ llvm) → runtime `/testsuite` (commit-matched,
   offline). Measure `du` first (gna+vests heavy).
3. **Runtime deps**: mcode += `gcc libc-dev zlib1g-dev diffutils`; llvm +=
   `diffutils`.
4. **Test scripts**: keep smoke, then `cd /testsuite && GHDL=/bin/ghdl
   ./testsuite.sh sanity gna vests synth vpi vhpi` (explicit list skips
   pyunit); drop `_todo.sh` for ghdl; pkg tests unchanged.
5. **No jobs.yml/needs.dot changes** — tests live on the 6 existing runtime images.

## Open decisions

- **Suite scope**: full `sanity gna vests synth vpi vhpi` (faithful, slow —
  vests ≈ 30–60 min/image) vs incremental start (`sanity gna synth`).
- **Embed** testsuite in images (recommended) vs clone-at-test-time.
- **pyunit** now (mcode-only, needs python+pytest in runtime image) vs later.

## Reference

- https://github.com/ghdl/ghdl/blob/master/.github/workflows/Build-Ubuntu.yml
- https://github.com/ghdl/ghdl/blob/master/.github/workflows/Test-GHDL.yml
- https://raw.githubusercontent.com/ghdl/ghdl/master/testsuite/testsuite.sh
- `debian-{bullseye,bookworm,trixie}/ghdl/Dockerfile` + `HDLC`
- `test/ghdl.sh`, `test/ghdl--llvm.sh`, `test/_todo.sh`
- `debian/base.dockerfile`
