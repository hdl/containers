# Audit: `ghdl-yosys-plugin` on `debian/bullseye` (amd64)

- **Task**: `ghdl-yosys-plugin`
- **Images**: `pkg/ghdl-yosys-plugin#ghdl`, `ghdl/yosys`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev` (`8761c15` "AGENTS.md: document _anchors as loader-only config scaffolding")
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script; `job_images('ghdl-yosys-plugin')` → `['pkg/ghdl-yosys-plugin#ghdl', 'ghdl/yosys']`)
- **Log**: `audits/logs/ghdl-yosys-plugin.log`

## Overall result: FAIL

Both images fail during the `make` of the plugin C++ source (`stage plugin` 3/3) with a GHDL synthesis-API mismatch: `src/ghdl.cc` from the unpinned upstream `master` tarball references identifiers that do not exist in the `synth.h`/`synth_gates.h` headers shipped by the published `ghcr.io/hdl/amd64/debian/bullseye/pkg/ghdl:latest` image. The test step never runs.

---

## `pkg/ghdl-yosys-plugin#ghdl` — FAIL

Command (echoed by `BuildImage`):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/ghdl-yosys-plugin \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target pkg \
  -f debian-bullseye/ghdl-yosys-plugin.dockerfile debian-bullseye
```

Exit status: 1 (`subprocess.CalledProcessError` from the `docker build` step → step exit code 2 = `make` failure).

Stage `plugin` 3/3 (`RUN cp -vr /opt/ghdl/* / && cd /tmp/ghdl-yosys-plugin && make && cp ghdl.so ...`) fails compiling `src/ghdl.cc`:

```
#10 src/ghdl.cc:74:7: error: use of undeclared identifier 'Sname_System'; did you mean 'Sname_User'?
#10 /usr/local/include/ghdl/synth.h:84:21: note: 'Sname_User' declared here
#10   enum Sname_Kind { Sname_User, Sname_Artificial, Sname_Version };
#10 src/ghdl.cc:76:7: error: use of undeclared identifier 'Sname_Unique'
#10 src/ghdl.cc:82:7: error: use of undeclared identifier 'Sname_Field'; did you mean 'Sname_User'?
#10 src/ghdl.cc:84:7: error: use of undeclared identifier 'Sname_Index'; did you mean 'Sname_User'?
#10 src/ghdl.cc:85:65: error: use of undeclared identifier 'get_sname_index'; did you mean 'get_sname_kind'?
#10 src/ghdl.cc:105:7: error: use of undeclared identifier 'Sname_System'; did you mean 'Sname_User'?
#10 src/ghdl.cc:696:11: error: use of undeclared identifier 'get_input_idx'
#10 src/ghdl.cc:840:8: error: use of undeclared identifier 'Id_Bmux'; did you mean 'Id_Pmux'?
#10 /usr/local/include/ghdl/synth_gates.h:56:4: note: 'Id_Pmux' declared here
#10 src/ghdl.cc:840:8: error: duplicate case value 'Id_Pmux'
#10 src/ghdl.cc:1141:8: error: use of undeclared identifier 'Id_Bmux'; did you mean 'Id_Pmux'?
#10 src/ghdl.cc:1373:13: error: no type named 'synth_instance_type' in namespace 'GhdlSynth'
#10 src/ghdl.cc:1383:9: error: use of undeclared identifier 'create_pval2'
#10 src/ghdl.cc:1385:9: error: use of undeclared identifier 'create_pval4'
#10 src/ghdl.cc:1397:5: error: use of undeclared identifier 'write_pval'
#10 src/ghdl.cc:1404:10: error: ... 'push_back': cannot convert initializer list ... to 'const Pval_Cstring_tuple'
#10 fatal error: too many errors emitted, stopping now [-ferror-limit=]
#10 20 errors generated.
#10 make: *** [Makefile:29: ghdl.o] Error 1
```

## `ghdl/yosys` — FAIL

Command (echoed by `BuildImage`):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/ghdl/yosys \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  -f debian-bullseye/ghdl-yosys-plugin.dockerfile debian-bullseye
```

Exit status: 1 (`subprocess.CalledProcessError`; step exit code 2 = `make` failure). Identical failure to `pkg/...`: the shared stage `plugin` 3/3 aborts in `make` with the same 20 `src/ghdl.cc` errors shown above (log lines 621–729). Because the dependent `pkg` stage can never succeed, the runtime stage is never produced.

## Environment facts

- Dockerfile: `debian-bullseye/ghdl-yosys-plugin.dockerfile` — **version-specific only**; no unified `debian/ghdl-yosys-plugin.dockerfile` exists (resolved per AGENTS.md probe order: `debian-<version>/` first → `debian-bullseye/` it is).
- Base: `ghcr.io/hdl/amd64/debian/bullseye/yosys:latest@sha256:58c0c80e41fd96b4b90da53c730aa3c43051f0cf2a6c6e336bd012281479df22` — pulls/extracts fine, apt step 2/2 installs `libgnat-9` from `deb.debian.org` successfully (EOL trap not hit: the pool still serves `libgnat-9 9.3.0-22`). Environment itself is healthy.
- GHDL dependency: `ghcr.io/hdl/amd64/debian/bullseye/pkg/ghdl:latest@sha256:30c818edbc27bf81103bcb07ab11a7645fcf50d5ff9f4e3ad18a7dc4b6a0dd8b` (CACHED, loads fine). It installs headers where:
  - `synth.h` enum `Sname_Kind` is only `{ Sname_User, Sname_Artificial, Sname_Version }` and offers `get_sname_kind` (no index/prefix variants);
  - `synth_gates.h` has `Id_Pmux` but **no** `Id_Bmux`;
  - `GhdlSynth` namespace has **no** `synth_instance_type`;
  - there is **no** `create_pval2`/`create_pval4`/`write_pval`.
  - GHDL runtime lib shipped by that image: `libghdl-5_0_0_dev.so`.
- Plugin source: downloaded unpinned from `https://codeload.github.com/ghdl/ghdl-yosys-plugin/tar.gz/master` (stage `plugin` 2/3, succeeds; per repo policy unpinned master = continuous testing of upstream). Its `src/ghdl.cc` uses all of the identifiers above — i.e. the API of a newer GHDL than the one in the pinned published `pkg/ghdl`.
- `fatal: not a git repository (or any of the parent directories): .git` at make start (log line 293/619) — the plugin Makefile's `git describe` probe for `GHDL_VER_HASH` falls back to `"unknown"`; harmless, not the failure.
- Test harness never reached: `test/ghdl--yosys.sh` exists (and is the only image of the two with a script; `pkg/ghdl-yosys-plugin#ghdl` would be exercised via the `#ghdl` package-location selector / `*.pkg.sh` path), but `BuildImage(test=True)` aborts before any image is produced.
- Wiring: `jobs.yml:147-149  ghdl-yosys-plugin: ... pkg/ghdl-yosys-plugin#ghdl ...`; `images.yml:60  ghdl/yosys: { dockerfile: ghdl-yosys-plugin }`.

## Root-cause hypothesis

**Recipe vs. dependency version skew (upstream-skew) — not test, not runtime-deps, not environment.**

- The plugin build compiles **unpinned upstream `ghdl-yosys-plugin` master** (`src/ghdl.cc`) against the **fixed, published `pkg/ghdl:latest` headers** for bullseye. Handler/plugin `master` has advanced its synthesis-client code to a GHDL C API that does not exist in the GHDL headers frozen in the published bullseye `pkg/ghdl` (digest `30c818ed...`, carrying `libghdl-5_0_0_dev.so`).
- Symptoms are unambiguous mismatches, not bugs in this repo's recipe logic: every missing symbol (`Sname_System/Unique/Field/Index`, `get_sname_index`, `get_input_idx`, `Id_Bmux`, `synth_instance_type`, `create_pval2/4`, `write_pval`, the `Pval_Cstring_tuple` braced-init) is a specific GHDL-synthesis-API addition that the installed `synth.h`/`synth_gates.h` simply do not have. The `duplicate case 'Id_Pmux'`/`'Sname_User'` notes clinch it: the plugin source *does* define those cases, they are just not in the header the plugin was compiled against.
- This is the intrinsic tension documented in AGENTS.md: unpinned upstream clones are intentional, but the plugin/ghdl pair must advance *in lockstep*; here `ghdl-yosys-plugin` master outran the bullseye `pkg/ghdl` lane.
- bullseye EOL apt is not a factor (apt step succeeds); compilers are the base yosys image's toolchain and are not implicated (pure C++ name-resolution errors).

## Investigation notes

- `job_images('ghdl-yosys-plugin')` → `['pkg/ghdl-yosys-plugin#ghdl', 'ghdl/yosys']`; both images attempted, both fail identically at the shared `plugin 3/3` stage — single root cause.
- Download/untar of plugin master (stage 2/3) and apt install of `libgnat-9` (step 2/2) both succeed (CACHED for the second image); the only failing step is `make` in stage `plugin 3/3`. No `=== PASS ===` reached for either image.
- Version stage never executes; no `dist/hdlc.<image>.version` produced this run.
- Parity check to try next: build the plugin source against a *newer* `pkg/ghdl` (e.g. bookworm/trixie or a freshly built local `pkg/ghdl` from `debian/ghdl` master) to confirm the API surface exists there; conversely, pin `ghdl-yosys-plugin` to the commit matching the bullseye `pkg/ghdl` header set.
- `fatal: not a git repository` from the Makefile git probe is pre-existing behavior, unrelated to the failure.

## Recommended next step

Re-sync the plugin with the GHDL it compiles against. Options, in order of preference:

1. **Advance `pkg/ghdl` for bullseye** so the published `synth.h`/`synth_gates.h` catch up to `ghdl-yosys-plugin` master: verify the missing identifiers (`Sname_*` extras, `Id_Bmux`, `synth_instance_type`, `*pval*`) exist in a newer GHDL head, then rebuild/publish `pkg/ghdl` (and the `ghdl` lane) on bullseye and re-run this audit.
2. **Pin `ghdl-yosys-plugin` to the commit whose `src/ghdl.cc` matches the bullseye `pkg/ghdl` headers** (or download a tagged release tarball instead of `master`) in `debian-bullseye/ghdl-yosys-plugin.dockerfile:43-44`.
3. **Re-wire the task to a newer collection** (bookworm/trixie) if that is where the matching (newer) `pkg/ghdl` lives; note the whole `ghdl`/`sim` family is currently wired to bullseye/bookworm only per jobs.yml, so this is a config change with downstream parity implications.

Whichever path, re-run this audit command; both `pkg/ghdl-yosys-plugin#ghdl` and `ghdl/yosys` must reach `=== PASS ===` and, with `test=True`, exercise `test/ghdl--yosys.sh`.