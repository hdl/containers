# Audit: `gtkwave` on `debian/bullseye` (amd64)

- **Task**: `gtkwave`
- **Images**: `pkg/gtkwave`, `gtkwave`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev` (`b1c2f4e` "gtkwave: build upstream master (meson)")
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script)
- **Log**: `audits/logs/gtkwave.log`

## Overall result: FAIL

Both images fail at the `pkg`/`build` stage with `E: Unable to locate package libgtk-4-dev`. Tests never run.

---

## `pkg/gtkwave` — FAIL

Command:

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/gtkwave \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target pkg debian/gtkwave
```

Exit status: 1 (logged `SystemExit`/`CalledProcessError` from `BuildImage` → exit code 100 of the build step).

Mechanism:
- `debian/gtkwave/Dockerfile` stage `build`, run `[build 2/3]`, sources `/tmp/ctx/HDLC` and runs
  `apt-get -y install --no-install-recommends ${makedepends[@]}`.
- `debian/gtkwave/HDLC:34` `makedepends` includes `libgtk-4-dev`.
- `debian/bullseye` (Debian 11) apt pool has no `libgtk-4-dev` (GTK4 only landed in Debian 12/bookworm).
- Error lines:
  ```
  #7 2.326 E: Unable to locate package libgtk-4-dev
  #7 ERROR: ... did not complete successfully: exit code: 100
  ```

## `gtkwave` (runtime) — FAIL

Command:

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/gtkwave \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/gtkwave
```

Exit status: 1 (same `CalledProcessError`; the runtime image reuses the same `build` stage and dies there before the `depends` runtime stage).

Identical error lines:
```
#9 2.879 E: Unable to locate package libgtk-4-dev
#10 [stage-3 2/3] ... (depends install) → CANCELED
```

---

## Root-cause hypothesis

**Recipe** (not test, not deps-at-runtime semantics, not environment).

- GTK4 dev/runtime packages (`libgtk-4-dev`, and runtime `libgtk-4-1`, `HDLC:58`) do not exist on
  Debian 11 `bullseye`, only on bookworm (12) and trixie (13).
- `debian/gtkwave/HDLC` is a **unified** recipe (shared by bullseye/bookworm/trixie), so it must fit
  the oldest collection it is wired to. It currently cannot.
- The failing expressions were introduced in the **latest head commit** `b1c2f4e`
  ("gtkwave: build upstream master (meson)", 2026-09-14): the previous recipe (`b1c2f4e^`)
  built the `lts` branch with autotools and only needed GTK3 (`libgtk-3-dev`), which bullseye has.
- `jobs.yml:72`, `gtkwave: *SysDebianDefaultArchSet` → builds for `debian/trixie`, `debian/bookworm`
  **and** `debian/bullseye` — hence bullseye is hit by the GTK4 requirement.
- No version-specific override exists: `debian-bookworm/gtkwave`, `debian-bullseye/gtkwave`,
  `debian-trixie/gtkwave` are all absent (Glob returned nothing).
- Environment itself is healthy: the build reaches the recipe step and apt resolves fine
  (base images `ghcr.io/hdl/amd64/debian/bullseye/build/{base,build}:latest` loaded), it is purely
  the package not existing in the bullseye archive.

## Investigation notes

- `jobs_images('gtkwave')` → `['pkg/gtkwave', 'gtkwave']`; both were attempted by the audit.
- `docker build` runs inside buildkit; `apt-get update -qq` succeeds (no 404 / snapshot issues seen),
  so this is not the bullseye-EOL mirror problem — it is a genuine unavailability of the package.
- The runtime `depends` array (`debian/gtkwave/HDLC:55-62`) also requires `libgtk-4-1`, which would
  fail the same way once the build stage is passed.
- `work/gtkwave/` contains a full gtkwave checkout (pre-existing from prototype/build work), unrelated
  to this audit's failure.

## Recommended next step

Date the unified recipe so it only needs GTK3 on bullseye, or restrict where the GTK4 build runs:

1. **Preferred (minimal)**: keep jobs.yml broad and make the recipe conditional, e.g. set the GTK
   deps based on `$(. /etc/os-release; echo $VERSION_CODENAME)` — `bullseye` → GTK3 only; otherwise
   GTK3+GTK4 — and likewise split the `depends` override into `debian-bullseye/gtkwave` vs unified.
   Note the default collection on this branch still resolves to `debian/bullseye`
   (`utils/pyHDLC/__init__.py`).
2. **Alternative (cookbook-style)**: keep the meson master recipe as unified GTK4 recipe and add a
   `debian-bullseye/gtkwave` override that reverts to the previous autotools `lts` GTK3 recipe
   (`git show b1c2f4e^:debian/gtkwave/HDLC`), or pin `gtkwave` in `jobs.yml` to
   `SysDebianBookwormDefaultArchSet` + `SysDebianTrixieDefaultArchSet` (i.e. drop bullseye).

Whichever path, re-run this audit command; both `pkg/gtkwave` and `gtkwave` must reach
`=== PASS <img> ===` (which now means `BuildImage(..., test=True)` completes, i.e. `test/gtkwave.sh`
runs inside the container — currently untested because the build aborts).