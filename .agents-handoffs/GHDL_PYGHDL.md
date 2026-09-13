# GHDL pyGHDL image — plan + handoff

Status: planning. Awaiting decisions on the open questions (bottom).

## Goal

Add a `ghdl/pyGHDL` image to hdl/containers: a GHDL **mcode** runtime that also ships
the `pyGHDL` Python bindings, and that is verified by running upstream's **pyunit**
testsuite at build time (mirroring `ghdl/ghdl`'s `Build-Ubuntu.yml`).

References: https://github.com/umarcor/osvb,
https://github.com/ghdl/ghdl/blob/master/.github/workflows/Build-Ubuntu.yml

## Key facts established

### Python floor: ≥3.11 → bullseye excluded
- `pyGHDL` setup.py declares `pythonVersions=("3.11", ...)`.
- `pyVHDLModel ~= 0.39.0` (pyGHDL dependency) requires `>=3.11` (PyPI).
- `pytest ~= 9.1` requires `>=3.10` (PyPI), `pytest-cov ~=7.1`, `Coverage ~=7.15`.
- Bullseye ships Python 3.9 → **pyGHDL image only on bookworm (3.11) + trixie (3.13), amd64 only** (ghdl is `*SysDebianAmd64`-wired). Trixie ships 3.13, bookworm 3.11 — both OK.

### How upstream builds/tests pyGHDL (`Build-Ubuntu.yml`)
- Build job (per backend): checkout w/ full history (git describe versioning), deps
  (`gcc g++ gnat` / `+llvm clang`, backtrace per distro), configure
  (`--with-llvm-config CXX=clang++`, mcode: none), make with `GNATMAKE/MAKE -jN`,
  `make install` into `install/`; step "🚦 Run testsuite: 'sanity'":
  `GHDL=$PWD/install/bin/ghdl; cd testsuite; ./testsuite.sh sanity`.
- The `ubuntu.requirements` file (runtime deps) lists `libgnat-<N>` (+ `libllvm<N>`) and for
  gcc/llvm backends also `gcc libc-dev zlib1g-dev`.
- For mcode + pyunit/coverage:
  1. strips `install/lib` down to the libghdl artifact (removes bin/include/`lib/ghdl/vendors`,
     `*.a`, `*.link`, `libghdlvpi.so`, `libghw.so`), copies system `libgnat-<N>.so` into `install/lib`;
  2. `cp -r install/lib/* pyGHDL/lib` — populates the binding's in-tree resource dir;
  3. `python -m pip install tomli` + `python -m pip install -r testsuite/requirements.txt`;
  4. step "🚦 Testsuite: 'pyunit'": `export PYTHONPATH=$(pwd)`, then
     `python -m pytest -raP --color=yes <testsuite/pyunit>` (plain unit mode) — **no pip install
     of pyGHDL itself; it runs in-source via `PYTHONPATH`**.
- `Test-GHDL.yml` (downstream job) does **not** rerun pyunit (only `sanity gna vests synth vpi
  vhpi`). pyunit is a Build-job-only gate.

### testsuite/pyunit mechanics (ghdl master `858569681`)
- `testsuite/testsuite.sh` pyunit branch (line ~160):
  `PYTHONPATH=$(pwd)/.. ${PYTHON:-python3} -m pytest -vsrA pyunit` (cwd = `testsuite/`).
- `testsuite/pyunit/` contains `pytest.ini` (`python_files=*`, `python_functions=test_*`) plus
  `libghdl/`, `dom/`, `lsp/` test dirs mirroring the package.
- Root `pyproject.toml` contributes `[tool.pytest]` (`--tb=native`,
  `filterwarnings = ["error::DeprecationWarning", ...]`, junit cfg) — keep it in the image so
  pytest rootdir behavior matches upstream.

### pyGHDL internals
- `pyGHDL/lib/` is an empty-in-repo resource package (only `__init__.py`); bindings load
  `libghdl-<version>.so` via ctypes. `pyGHDL/libghdl/_get_libghdl_path()` search order:
  1. `GHDL_PREFIX` env, 2. `GHDL` env, 3. `VUNIT_GHDL_PATH`, 4. the `pyGHDL/lib` package
  resource dir (in-source: `pyGHDL/libghdl/../../lib`), 5. `which ghdl`. We populate #4
  (upstream-exact) and set `GHDL=/bin/ghdl`.
- Loading `libghdl-*.so` needs its DT_NEEDED (`libgnat-<N>.so`, `libgcc_s.so.1`) — both present
  in the existing mcode runtime (`libgnat-N` + pulled `libgcc-s1`). No gcc needed.
- Optional wheel route: `setup.py` packages `pyGHDL/lib/**` (`lib*.so`, `libghdl/**/*.{vhdl,cf}`)
  into a platform wheel, via build-backend deps `setuptools>=83` + `pyTooling~=8.19`
  (pyproject `[build-system]`). Not needed for the recommended in-source mode.

### pip dependencies (pyunit + pyGHDL runtime)
From `testsuite/requirements.txt`, which `-r`s `../pyGHDL/requirements.txt`:
- `pyTooling[terminal] ~= 8.19`
- `pyVHDLModel ~= 0.39.0`  (≥3.11)
- `pytest ~= 9.1`  (≥3.10)
- `pytest-cov ~= 7.1`
- `Coverage ~= 7.15`
System: `python3-pip python3-venv` (python3 itself already in `debian/base.dockerfile` base).

### Local precedent / repo state
- `work/upstream/`: `ghdl` (commit `858569681`, matches image version), `ghdl-cosim`, `ghdl/docker`
  cloned. **`osvb` NOT cloned** — its `.github/Dockerfile` (cocotb/vunit wheels on deprecated
  `ghdl/cosim:py`) was read via raw fetch; weak pattern, optionally clone later.
- `debian-*/sim.dockerfile` is the PEP668 pattern to reuse: `python3 -m venv /opt/venv` +
  `ENV VIRTUAL_ENV=/opt/venv` + `ENV PATH="$VIRTUAL_ENV/bin:$PATH"`. (Bookworm+ marks the system
  python `externally-managed`, so bare `pip3 install` fails without `--break-system-packages`
  or a venv — use the venv.)
- `ghdl` images are wired via `images.yml` targets `mcode`/`llvm`/`pkg-mcode`/`pkg-llvm`;
  jobs.yml task `ghdl` uses `*SysDebianAmd64` (all 3 collections) → a per-image collection
  restriction requires a **separate task**.
- `needs.dot` already has `base->ghdl` and a `sim->osvb` chain; pyghdl is a new leaf.

## Design decisions (recommended)

1. **In-source `PYTHONPATH` install** (not pip wheel) — exactly mirrors upstream Build job;
   no pyTooling build-backend risk; users get `import pyGHDL` via `ENV PYTHONPATH=/opt/pyGHDL`.
2. **Scope: bookworm + trixie, amd64 only.** Bullseye is impossible (Python 3.9 < 3.11).
3. **Separate task `ghdl-pyghdl`** in jobs.yml with inline
   `sys: {<<: *SysDebianBookwormAmd64, <<: *SysDebianTrixieAmd64}`.
4. **Build-time pyunit gate** inside the `pyghdl` stage (upstream runs pyunit in the Build job,
   not Test job).
5. **Venv at `/opt/venv`** (sim.dockerfile idiom) to satisfy PEP668.
6. **Test-phase**: smoke only (`_env.sh` + `smoke-tests/ghdl.sh` + import + optional quick pyunit).
7. Naming: image `ghdl/pyghdl`, dockerfile `ghdl`, target `pyghdl`; source at `/opt/pyGHDL`.

## Implementation plan (file by file)

> **Note:** As of the ghdl HDLC extraction, build logic lives in `HDLC` files and
> Dockerfiles define stages + image setup. The plan below follows this pattern.

### 1. `debian-{bookworm,trixie}/ghdl/HDLC`

Add at the end of the HDLC file:

```bash
depends_pyghdl=(
  python3-pip
  python3-venv
)

runtests() {
  cd /opt/pyGHDL/testsuite
  PYTHONPATH=$(pwd)/.. python3 -m pytest -vsrA pyunit
}
```

Notes: `depends_pyghdl` is separate from `depends` (mcode runtime) to keep the base
mcode image lean. `runtests()` is the pyunit gate — if more files are needed later
(e.g. full `testsuite.sh pyunit` for JUnit), also copy `testsuite/testsuite.sh` +
`scripts/bash_toolbox.sh` + add `diffutils` to `makedepends`.

### 2. `debian-{bookworm,trixie}/ghdl/Dockerfile`

Append after the `llvm` stage (before EOF):

```dockerfile
#---

FROM mcode AS pyghdl

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    ${depends_pyghdl[@]} \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build-mcode /tmp/ghdl/pyGHDL                     /opt/pyGHDL/pyGHDL
COPY --from=build-mcode /tmp/ghdl/testsuite/pyunit           /opt/pyGHDL/testsuite/pyunit
COPY --from=build-mcode /tmp/ghdl/testsuite/requirements.txt /opt/pyGHDL/testsuite/requirements.txt
COPY --from=build-mcode /tmp/ghdl/pyproject.toml             /opt/pyGHDL/pyproject.toml

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV \
 && $VIRTUAL_ENV/bin/pip install -r /opt/pyGHDL/testsuite/requirements.txt
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/opt/pyGHDL
ENV GHDL=/bin/ghdl

RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && runtests
```

Key points:
- `FROM mcode AS pyghdl` — inherits the mcode runtime + ghdl binary.
- `COPY --from=build-mcode` pulls pyGHDL source + pyunit from the same clone (version-aligned).
- `VIRTUAL_ENV` + `PATH` follows the PEP668 venv idiom from `sim.dockerfile`.
- The trailing `runtests` RUN is the build-time pyunit gate (fails the build on regression).
- Bullseye is untouched (Python 3.9 < 3.11 requirement).

### 3. `utils/pyHDLC/images.yml` (in the `# GHDL` block, after `ghdl/llvm`)
```yaml
  ghdl/pyghdl: { dockerfile: ghdl, target: pyghdl }
```

### 4. `utils/pyHDLC/jobs.yml` (new task under `default:`)
```yaml
  ghdl-pyghdl:
    images:
      - ghdl/pyghdl
    sys:
      # pyGHDL/pytest require Python >=3.11: bullseye (3.9) excluded
      <<: *SysDebianBookwormAmd64
      <<: *SysDebianTrixieAmd64
```

### 5. `.github/needs.dot`
Add `base -> ghdl-pyghdl;` as a leaf edge (the dockerfile self-builds mcode; no ghdl-task
dependency needed).

### 6. `test/ghdl--pyghdl.sh` (new)
```sh
. ./_env.sh
./smoke-tests/ghdl.sh
cd /opt/pyGHDL/testsuite
PYTHONPATH=$(pwd)/.. python3 -m pytest -vsrA pyunit
```
(upgrade to full pyunit in test phase is an open question — see below)

### 7. Verification
`pyHDLC jobs ghdl-pyghdl` (matrix = bookworm/trixie × amd64),
build+test both with `-d ghdl/pyghdl --test`, `-n` dry-run first, then real builds.

## Open questions
1. Test-time pyunit too (full repeat in `ghdl--pyghdl.sh`), or build-gate + smoke only?
2. In-source `PYTHONPATH` (recommended) vs pip wheel install?
3. Clone `umarcor/osvb` into `work/upstream/osvb` at implementation (reference-only)?
4. Write a `GHDL_PYGHDL` handoff note into `GHDL_COSIM_CONSOLIDATION.md` / AGENTS.md too?

## Gotchas
- Debian bookworm/trixie block pip in system python (PEP668) → venv required.
- `pyproject.toml` `filterwarnings=error::*DeprecationWarning` can fail pyunit if a pinned dep
  warns — keep the file to stay upstream-faithful; gate with upstream command verbatim.
- ghdl `libghdl-<version>.so` name must match `_get_libghdl_name()` — guaranteed because both
  come from the same clone/commit in build-mcode.
- Do NOT add a `pkg/ghdl/pyghdl`; pyGHDL is a full runtime image, not a pkg artifact.
