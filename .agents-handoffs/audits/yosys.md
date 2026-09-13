# Audit: `yosys` on `debian/bullseye` (amd64)

- **Task**: `yosys`
- **Images**: `pkg/yosys`, `yosys`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev` (`8761c15` "AGENTS.md: document _anchors as loader-only config scaffolding")
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script)
- **Log**: `audits/logs/yosys.log`

## Overall result: FAIL

Both images fail at the shared `build` stage (Dockerfile step `[build 3/5]`) with `make: *** No
targets specified and no makefile found.` Tests never run.

---

## `pkg/yosys` — FAIL

Command (as printed by `BuildImage`):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/yosys \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target pkg debian/yosys
```

Exit status: 1 (docker build) → `CalledProcessError` raised by `BuildImage` (line 456,
`utils/pyHDLC/__init__.py`), logged as `=== FAIL pkg/yosys ... ===`. The audit script then marks
`ok=False`.

Error lines (from `audits/logs/yosys.log`):

```
#7 [build 3/5] RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build
#7 0.614 Cloning into '/tmp/yosys'...
#7 9.906 make: *** No targets specified and no makefile found.  Stop.
#7 9.906 make: *** No rule to make target 'install'.  Stop.
#7 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 2
...
ERROR: failed to build: failed to solve: ... exit code: 2
```

## `yosys` (runtime) — FAIL

Command:

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/yosys \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian/yosys
```

Exit status: 1 (same `CalledProcessError`; the runtime target reuses the same failing `build`
stage — step `[build 3/5]` — before its own `FROM $REGISTRY/build/build` runtime stage):

```
#9 [build 3/5] RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build
#9 0.355 Cloning into '/tmp/yosys'...
#9 7.706 make: *** No targets specified and no makefile found.  Stop.
#9 7.706 make: *** No rule to make target 'install'.  Stop.
#9 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 2
```

---

## Root-cause hypothesis

**Recipe** (upstream main-branch drift), not test, not runtime-deps, not environment.

- `debian/yosys/HDLC:40-45` `build()` clones unpinned upstream and builds with GNU Make:
  ```bash
  git clone https://github.com/YosysHQ/yosys.git /tmp/yosys
  cd /tmp/yosys
  make -j $(nproc)
  make DESTDIR=/opt/yosys install
  ```
- The clone itself succeeds; the checkout is clean and complete (verified locally against the same
  HEAD `0edda7a3`, "Merge pull request #6201 ...", `main`). The repo **no longer ships a root
  `Makefile`** at `main`: the tree now provides `CMakeLists.txt` only, and its prologue rejects
  in-tree builds (`"In-tree builds are not supported. Instead, run: cmake -B build ..."`),
  `cmake_minimum_required(VERSION 3.28)`. Hence `make` finds no default target and no `install`
  rule, i.e. exactly the two logged errors.
- The second `make` output line appears because the `build()` shell is `/bin/bash -c` without
  `set -e`, so the first `make` failure does not abort the RUN; both `make` errors log before the
  step exits 2.
- Same class of drift as the AGENTS.md note that unpinned clones are intentional — upstream `main`
  moved the build system, and the recipe has not caught up. `runtests()` (`HDLC:47-50`) also invokes
  `make test`, which would fail identically once a CMake build were in place.
- Environment is healthy: base deps stage `[build 2/5]` installed 205 packages from the bullseye
  snapshot (`snapshot.debian.org ... 20260824T000000Z`) with no 404s, and base images
  `ghcr.io/hdl/amd64/debian/bullseye/iverilog` / `build/build:latest` resolved from the registry.

## Investigation notes

- `job_images('yosys')` → `['pkg/yosys', 'yosys']`; both were attempted by the audit; both fail at
  the same step.
- Reproduced the clone outside docker to confirm the checkout shape: `git clone` of
  `https://github.com/YosysHQ/yosys.git` completes in ~8 s, exit 0, but `ls Makefile` →
  "No such file or directory"; `CMakeLists.txt` present; `git status` clean on branch `main`,
  up to date with `origin/main` (`0edda7a3`).
- Secondary observation for the fix (not the cause of today's failure): the CMake build requires
  `cmake >= 3.28`, but Debian 11 `bullseye` ships CMake 3.18 — a version-specific
  `debian-bullseye/yosys` recipe may be needed in addition to rewiring `build()`/`runtests()` to
  the CMake out-of-tree flow (`cmake -B build ... && cmake --build build && DESTDIR=... cmake
  --install build`).

## Recommended next step

Rewrite the unified `debian/yosys/HDLC` `build()` (and `runtests()`) for the CMake-only upstream:

1. **Preferred**: switch `build()` to the documented out-of-tree flow, e.g.
   `git clone ... /tmp/yosys && cd /tmp/yosys && cmake -B build -DCMAKE_INSTALL_PREFIX=/opt/yosys && cmake --build build -j$(nproc) && cmake --install build`,
   add `cmake` (and confirm no omitted bootstrap deps) to `makedepends`, and change `runtests()`
   to `make test` equivalents under the build dir only if upstream still exposes them.
2. Watch the CMake minimum (3.28) vs the bullseye archive (3.18): if bullseye cannot host the new
   build, gate via os-release or pin `yosys` in `jobs.yml` to newer collections, mirroring what was
   proposed for gtkwave.

Whichever path, re-run this audit command; both `pkg/yosys` and `yosys` must reach `=== PASS <img>
===`, which also requires `test/yosys.sh` (and `smoke-tests/yosys.sh`) to pass inside the container.