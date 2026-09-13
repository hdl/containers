# GHDL Cosim ↔ hdl/containers Consolidation Notes

Handoff from the research pass (Oct 2026, plan mode). Nothing here modifies the repo.

## Scope

| repo | path | notes |
|---|---|---|
| ghdl/ghdl-cosim | `docker/*.dockerfile` (py, vunit-cocotb, matplotlib, octave, xyce, mcode) | the recipe sources |
| ghdl/docker | `.github/workflows/cosim.yml` + `run.sh:236` | the thing that actually builds the `ghdl/cosim:*` tags |
| ghdl/ghdl | `scripts/ci-run.sh` | `--docker`/`-d` option analysis (1 Jan 2023 state) |

States explored:
- **1 Jan 2021** (ghdl-cosim `64f8493a`, docker `c6e69453`, ghdl `b423d311`) — reconstructed how
  `ghdl/ghdl:buster-llvm-7` was built (mcode→llvm-7 tier; `scripts/ci-run.sh` lived in `dist/`).
- **1 Jan 2023** (ghdl-cosim `cc9a12bf`, docker `7b1cba12`, ghdl `ddf587a7`) — `ci-run.sh`
  relocated to `scripts/`, gained `-d/--docker`; ghdl/docker `run.sh` is its only consumer.
- **Current master** (researched for this doc) — ghdl-cosim `74c2e51` (2024-06-06), docker
  `6f9c182` (2024-11-20), ghdl `858569681`.

## The ghdl/cosim image set (9 tags)

Recipe/layering (from `ghdl-cosim/docker/*.dockerfile` + `ghdl/docker` cosim.yml base/build jobs):

| tier | dockerfile | tag | content |
|---|---|---|---|
| base | mcode | `mcode` | ghdl/ghdl:buster-**mcode** + gcc. **No python.** |
| base | py | `py` | ghdl/ghdl:buster-**llvm-7** + curl, python3, python3-pip; pip −U pip setuptools wheel + **pytest** |
| base | vunit-cocotb | `vunit-cocotb` | `py` + libpython3.7-dev + **VUnit** (master wheel) + **cocotb** (stable/1.4 wheel) |
| build | matplotlib | `matplotlib-slim` | `py` + ImageMagick + libssl-dev + **matplotlib + numpy** (pip) |
| build | (vunit-cocotb tier) | `matplotlib` | `matplotlib-slim` + VUnit + cocotb |
| build | octave | `octave-slim` | `py` + **Octave** (apt) |
| build | (vunit-cocotb tier) | `octave` | `octave-slim` + VUnit + cocotb |
| build | xyce | `xyce-slim` | `py` + **Xyce** (master; Trilinos 12.12.1 build) + libamd2 libgfortran5 libfftw3-3 libblas3 liblapack3 libsuitesparseconfig5 + tox + pytest |
| build | (vunit-cocotb tier) | `xyce` | `xyce-slim` + VUnit + cocotb |

Cosim base-tier images `mcode, py, vunit-cocotb` are built straight; each `build` tier
image is `${img}-slim` then `${img}` (`vunit-cocotb.dockerfile` with `IMAGE=<img>-slim`).

### Tools per ghdl/cosim image

**mcode** — GHDL (mcode backend), gcc, make, zlib1g-dev (no Python).

**py** — GHDL (llvm backend), Python 3.7, pip, pytest, curl, gcc, make, GNAT runtime, zlib1g-dev, libllvm7.

**vunit-cocotb** — everything in py + VUnit + cocotb + libpython3.7-dev. (g++, git, python3-dev are build-stage only.)

**matplotlib-slim** — py + ImageMagick + libssl-dev + matplotlib + numpy.

**matplotlib** — matplotlib-slim + VUnit + cocotb.

**octave-slim** — py + GNU Octave.

**octave** — octave-slim + VUnit + cocotb.

**xyce-slim** — py + Xyce + Trilinos 12.12.1 libs + runtime math libs + tox + pytest.

**xyce** — xyce-slim + VUnit + cocotb.

## The hdl/containers sim family (this repo)

`utils/pyHDLC/images.yml` sim block + `utils/pyHDLC/jobs.yml` cosim/gnuplot/osvb jobs.

| image | dockerfile | FROM / layers | tools |
|---|---|---|---|
| `sim` (base) | debian-bullseye/sim.dockerfile | ghdl/llvm + pkg/nvc, pkg/verilator, pkg/iverilog | GHDL(LLVM), NVC, Verilator, Icarus Verilog, binutils, libdw1, libzstd1, make, perl, python3-pip, tcl |
| `sim/osvb` | debian-bullseye/osvb.dockerfile | = `sim` + build wheels (cocotb, VUnit) + OSVMMLibs clone | + **VUnit, cocotb, OSVVM libs**, libpython3-dev |
| `sim/scipy-slim` | debian-bullseye/scipy.dockerfile | `sim` + imagemagick + libssl-dev + matplotlib + numpy | + ImageMagick, libssl-dev, **matplotlib, numpy** (pip) |
| `sim/scipy` | debian-bullseye/osvb.dockerfile (`argimg: sim/scipy-slim`) | `scipy-slim` + osvb layers | `scipy-slim` + VUnit + cocotb + OSVMMLibs |
| `sim/octave-slim` | debian-bullseye/octave.dockerfile | `sim` + octave | + GNU Octave (apt) |
| `sim/octave` | debian-bullseye/osvb.dockerfile (`argimg: sim/octave-slim`) | `octave-slim` + osvb layers | `octave-slim` + VUnit + cocotb + OSVMMLibs |
| `sim/octave/gnuplot` | debian-bullseye/gnuplot.dockerfile | `sim/octave` + gnuplot | + gnuplot, ghostscript, fonts-freefont-otf |

### Jobs wiring (jobs.yml)

- **osvb** job: builds `sim/osvb` (bullseye-only, `*SysDebianLegacyAmd64`).
- **cosim** job: builds `sim/${prj}-slim` + `sim/${prj}` for `prj: [scipy, octave]`.
- **gnuplot** job: builds `sim/octave/gnuplot` (bullseye-only).
- **xyce** job: `xyce: *SysDebianLegacyAmd64` — but **NOT in `images.yml`** (no `sim/xyce` entry).
  The dockerfile (`debian-bullseye/xyce.dockerfile`) exists but is orphaned.

## Closest-match mapping

| ghdl/cosim tag | closest hdl/containers image | how close |
|---|---|---|
| `py` | `sim` | **closest** — cosim:py base = ghdl/llvm + python3+pip+pytest. Local `sim` is that *plus* NVC/Verilator/Icarus (extra HDL simulators); no python-only sibling exists locally → `sim` is the python base of every sim/* here |
| `vunit-cocotb` | `sim/osvb` | **1:1 concept** — both = py/base + VUnit + cocotb; local `osvb` additionally stages OSVMMLibs (extra) |
| `matplotlib-slim` | `sim/scipy-slim` | **near-identical** — both add ImageMagick + libssl-dev + matplotlib + numpy to the python base (cosim names it "matplotlib", local "scipy"; same tool floor) |
| `matplotlib` | `sim/scipy` | **1:1** — `matplotlib`/`scipy` tile = slim + VUnit + cocotb (+ OSVMMLibs locally) |
| `octave-slim` | `sim/octave-slim` | **identical** — both `python-base + apt octave` |
| `octave` | `sim/octave` | **1:1** — same tiling, +VUnit+cocotb(+OSVMMLibs) |
| `xyce-slim` | — (no local `sim/xyce`) | **gap** — local `debian-bullseye/xyce.dockerfile` exists (Trilinos 12.12.1 + Xyce master, same source approach) but is **NOT wired** into `images.yml`/`jobs.yml` (no `sim/xyce`/`sim/xyce-slim` targets) |
| `xyce` | — | **gap** — same as above |
| `mcode` | — | **gap/no-analogue** — no mcode-base sim image; local sim family is llvm-based. Closest conceptual peer = GHDL mcode image target |
| — (extra) | `sim/octave/gnuplot` | local-only; ghdl/cosim has no gnuplot tag |

## Key deltas & open questions

1. **xyce is authored but orphaned locally.** `debian-bullseye/xyce.dockerfile` matches
   cosim's Xyce build (Trilinos 12.12.1 → Xyce master, `--enable-xyce-shareable`) yet
   `images.yml`/`jobs.yml` build no `sim/xyce`/`sim/xyce-slim`. ghdl/cosim keeps xyce wired;
   hdl/containers dropped it. Decision point: re-enable `sim/xyce` (matches upstream 1:1) or drop.

2. **Naming drift:** cosim `matplotlib(-slim)` ≙ local `scipy(-slim)` (identical tools,
   different key), cosim `py` ≙ local `sim`.

3. **mcode absence:** cosim ships a python-free GHDL-mcode variant; hdl/containers `sim`
   family is entirely llvm-based → no direct equivalent.

4. **OSVMMLibs extra:** local `sim/osvb` stages OSVVM libs (compile-osvvm.sh) unlike cosim
   vunit-cocotb. This is a purposeful addition (OSVVM = VHDL verification standard library).

5. **python3.7 pinned locally, python3.7-dev locally:** both cosim and hdl/containers are
   buster/bullseye-locked (python3.7 / python3.9 respectively, since bullseye → python3.9).
   cosim buster = 3.7; hdl bullseye = 3.9. No py3.10+ yet.

6. **`libssl-dev` present in both:** cosim matplotlib-slim and local scipy-slim both install
   `libssl-dev` (for cryptography library builds).

7. **VUnit/cocotb versions:**
   - cosim pins cocotb `stable/1.4` (branch), VUnit `master` (rolling).
   - local osvb pins both cocotb and VUnit to `master` (rolling) — version lock differs.
   - cosim uses `setup.py bdist_wheel`; local uses the same.

8. **Local nvc/verilator/iverilog:** the local `sim` base adds three extra HDL simulators
   (NVC, Verilator, Icarus) via `COPY --from=pkg/*`. These are not in cosim:py; they make
   the local `sim` image broader (multi-simulator) vs cosim's single-GHDL approach.

9. **CI consumers:** ghdl-cosim's own `Pipeline.yml` tests `ghdl/cosim:matplotlib` and
   `ghdl/cosim:xyce` via a single pytest (`tests/test.py`). hdl/containers' test scripts
   (`test/sim--*.sh`) run different suites per image.

---

*Generated 2026-10-07 during plan-mode research session.*
