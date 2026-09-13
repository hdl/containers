# AGENTS.md

## Repository Overview

This is a **recipe + CI-as-code** repository: it builds and tests OCI/Docker images of open-source EDA (Electronic Design Automation) tools. There is almost no application code — everything exists to feed `docker build`, the GitHub Actions CI, and the Sphinx docs.

- Images are pushed to `ghcr.io/hdl` and mirrored to Docker Hub (`docker.io/hdlc`, root namespace).
- `gcr.io/hdl-containers` was deprecated (shut down 2025) and removed from the codebase.
- Defaults in code are branch-dependent. This checkout defaults to `debian/trixie` (verify in `Defaults` in `utils/pyHDLC/__init__.py`, mirrored in `utils/bin/dockerRelease` and `doc/CollectionsAndArchitectures.rst`).

## Prerequisites

The following host tools are expected. If any are missing, inform the user.

- `docker` — image builds and tests
- `python3` + `python3-venv` — pyHDLC environment
- `make` — misc host-side tasks
- `curl` — fetching
- `grep`, `rg` (ripgrep) — codebase search
- `git` — version control, submodules

## Getting Started

A `venv/` directory is expected in the repo root. Create it if absent:

```bash
python3 -m venv venv
source venv/bin/activate
utils/setup.sh
```

`utils/setup.sh` installs pyHDLC in editable mode and verifies the import. Do not
source it; execute it after activating the venv.

## Layout & Key Files

| Path | Role |
|---|---|
| `debian/` | **Unified recipes** shared by all Debian versions (base, bom, and a subset of tools) |
| `debian-bullseye/`, `debian-bookworm/`, `debian-trixie/` | Version-specific recipes if the shared one does not fit |
| `rockylinux-8/` | Non-Debian collection (`base.dockerfile` only; built for the `base` task) |
| `utils/pyHDLC/` | Python CLI wrapping all docker ops; config in `images.yml` + `jobs.yml` |
| `utils/bin/` | `dockerRelease` (mirror matrix), `dockerDive` |
| `utils/map/` | `map.py`: parses Dockerfiles → graphviz dot of the image dependency graph |
| `test/` | One shell script per image; helpers `_env.sh`, `_todo.sh`, `_tree.sh`, `*.pkg.sh`; `smoke-tests/` submodule (`hdl/smoke-tests`) |
| `.agents-handoffs/audits/` | Bullseye audit status table, per-task FAIL reports, build logs |
| `.github/` | CI brain: `needs.dot`, `dispatch.py`, `watch.py`, `results.py`, `summary.py`, composite actions |
| `.github/workflows/` | `scheduler.yml`, `watch.yml`, `build-test-release.yml`, `doc.yml`, `formal.yml`, `impl.yml` |
| `doc/` | Sphinx docs; user-facing `doc/graph/*.dot` image maps |

## Core model

- **Namespaces.** Every image is `registry/architecture/collection/image`, e.g. `ghcr.io/hdl/amd64/debian/bullseye/yosys`. Optional segments are dropped for default collection/arch when mirroring (`dockerRelease`).
- **Tasks vs. images.** A *task* is a `needs.dot` node and `jobs.yml` key that expands to one or more images. Example: task `base` → `build/base`, `build/build`, `build/dev`; task `nextpnr` fans out over `ice40/ecp5/nexus/generic`.
- **Config-driven.** `utils/pyHDLC/jobs.yml` (`default`/`pkgonly`/`runonly`/`custom` sections) states which images×collections×architectures each task builds. `images.yml` holds per-image overrides of `dockerfile`/`target`/`argimg`. `pyHDLC jobs <task>` cross-products these into the GHA matrix. Both config files open with a loader-only `_anchors:` section; its meaning is documented on the `_anchors` fields of `ConfigImages`/`ConfigJobs` in `utils/pyHDLC/__init__.py`. Anchor aliases like `*SysDebianLegacyAmd64` are knowingly opaque — resolve a task's effective collection×arch matrix with `pyHDLC jobs <task>`.
- **pkg vs runtime.** Every tool yields two artifacts: a `pkg/<tool>` image (staged content from `FROM scratch AS pkg`) and the runtime tool image (`FROM <collection>.../base; COPY --from=build ...`). `pkgonly`/`runonly` build one, `default` builds both.
- **Base layering.** `build/base → build/build → build/dev` is the shared three-stage base (`debian/base.dockerfile`). The `base`/`build`/`dev` terms are reused as *namespace prefixes* (`build/impl`, `build/nextpnr/*`), which can be confusing.
- **Recipes.** `HDLC` files are sourced inside builds (`RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build`) and expose `makedepends`, `depends`, `testdepends`, `build()`, `runtests()`. Multi-variant tools (e.g. `ghdl`, `openroad`) define variant-specific arrays (`makedepends_llvm`, `depends_llvm`) and entry points (`build_mcode()`, `build_llvm()`), with a shared `build()` that receives configure flags via `"$@"`.

## Dockerfile conventions

- **`update-ca-certificates`** only in `base.dockerfile` (`debian/base.dockerfile` and `debian-bullseye/base.dockerfile`). All other Dockerfiles inherit certificates from the base layer.
- **`apt-get install`** lines must include `DEBIAN_FRONTEND=noninteractive`, `-y`, and `--no-install-recommends`. No `apt install` (without `-get`).
- **Package listing** after `--no-install-recommends`:
  - Single argument on the same line: OK (HDLC variable or literal package).
  - Multiple arguments on the same line: must all be HDLC array variables (`${depends[@]}`, `${makedepends[@]}`, `${testdepends[@]}`, etc.).
  - Literal package names go on subsequent lines (one per line).
- **Version detection via `ARG REGISTRY`**: `ARG` declared before `FROM` is only in scope for `FROM` instructions. To expose it as an environment variable to HDLC scripts, re-declare it after `FROM`:
  ```dockerfile
  FROM $REGISTRY/build/build AS build
  ARG REGISTRY
  ```
  This allows `case "$REGISTRY"` in the HDLC to set version-specific packages.
- **Unified Dockerfile pattern**: When version-specific Dockerfiles differ only in `ARG REGISTRY` but HDLC packages differ, collapse to a single `debian/<tool>/Dockerfile` + `debian/<tool>/HDLC` with `case "$REGISTRY"` detection. Examples: `nvc`, `cvc`, `klayout`.

## Building Images

Use the pyHDLC CLI (after activating the venv — see Getting Started):

```bash
source venv/bin/activate
pyHDLC build -a amd64 -c debian/bullseye -d yosys -q
```

Prefer the CLI for building and testing. The Python API (`BuildImage`, `TestImage`
in `pyHDLC`) exists but mirrors the CLI; reach for it only when the CLI cannot express
the operation.

Notes:
- `-d/--default` infers dockerfile/target/argimg from the image name; `-p/--pkg` targets the `pkg` stage; `-q`/`--test` tests each image right after building.
- `-n/--noexec` prints the exact `docker` commands without running them — the safe way to verify what a `build`/`test`/`pull`/`push`/`jobs` call would do.
- Dockerfile resolution (`debian-<version>/` first, then unified `debian/`), per-tool consolidation status, and the non-unified images list are documented in `.agents-handoffs/CONSOLIDATION.md`. `ghdl`, `nvc`, `cvc`, `klayout` use unified recipes (`debian/<tool>/Dockerfile` + `HDLC`) with `case "$REGISTRY"` collection detection (`HDLC_GNAT`/`HDLC_LLVM`/`HDLC_BACKTRACE_PKG` per version).
- Build args: `SYSIMAGE=<arch>/<collection>[:]` (base dockerfile, `/`→`:`), `REGISTRY=<registry>/<arch>/<collection>` (tool dockerfiles), `IMAGE=<argimg>`.
- Builds use `--platform linux/<arch>`; any `arm*` architecture label is normalized to `linux/arm64` (`_NormalisePlatform`). Cross-arch builds need `utils/setup.sh <arch>` (qus binfmt via `aptman/qus`; the arch arg is optional — bare `utils/setup.sh` still installs pyHDLC).

## Testing Images

Tests run *inside* the container, never locally. `TestImage` bind-mounts `<repo>/test` at `//wrk` and invokes `//wrk/<script>.sh`:

```bash
docker run --rm -v /path/to/repo/test://wrk ghcr.io/hdl/amd64/debian/bullseye/yosys //wrk/yosys.sh
```

- Script names are the image name with `:`→`--` and `/`→`--` (e.g. `ghdl--llvm.sh` for `ghdl/llvm`).
- Package images are tested via `*.pkg.sh` through a dedicated `utils/pyHDLC/testpkg.dockerfile` wrapper (copies `/opt/<tool>` from the pkg image into an Alpine scratch test).
- Scripts run `test/_env.sh` first, then call `./smoke-tests/<tool>.sh` from the submodule, then `./_todo.sh` (placeholder for pending tests).
- Added a tool? Add its test script here too.
- The build-only tasks `impl-build` and `nextpnr-build` (images `build/impl`, `build/nextpnr/base`, `build/nextpnr/build`) have **no** `test/` scripts; running them with `--test` fails (TestImage would look for `//wrk/build--impl.sh` etc.).

## Versioning & Releases

- A `FROM scratch AS version` stage writes image version to a file; `BuildImage` exports it to `dist/` (`__init__.py`).
- `PushImage` reads `dist/hdlc.<image>.version` and tags versioned mirrors (`<name>:<version>`) for non-Docker registries.
- `dockerRelease` implements the **mirror matrix**: full `ghcr.io/hdl/<arch>/<collection>/<img>` + flattened `ghcr.io/hdl/<img>` and `docker.io/hdlc` for the default collection/arch only. No multi-arch manifests are produced (the `(future manifest?)` comments are historical).

## CI/CD Flow

1. `scheduler.yml` reacts to push/schedule/workflow_dispatch; `dag.setup.sh` installs networkx+pygraphviz.
2. `dispatch.py` reads `.github/needs.dot` (a graphviz DAG of **tasks**), validates acyclicity, selects a subgraph from the triggering task list (supports `F`, `F>T`, `F>`, `>T` windows and `task:T`/`task:R` skip-test/skip-release suffixes), then dispatches `build-test-release.yml` runs in dependency order (Kahn's algorithm).
3. `watch.yml` polls running runs, reruns failures (max `rerun` attempts), and cascades dependents.
4. `build-test-release.yml` — one run per task: `generate-matrix` (`pyHDLC jobs <key>`) → parallel `jobs` (composite action `build-test-release`) → `results.py`/`summary.py` render summaries.
5. `formal.yml`/`impl.yml` still exist as standalone workflows because the scheduler cannot yet express `pull` lists (TODO in both).

## Gotchas from the repo's history

- **Do not add per-tool workflow files** — the static workflows were deleted (Aug 2026) and replaced by the DAG scheduler. Add tools via `debian/` recipes + `images.yml`/`jobs.yml` + a `needs.dot` node + `test/` script.
- **`#` is overloaded**: `image#dir` = package-location selector for tests; `#A`/`#C` = mirror placeholders in `PushImage` (`__init__.py`).
- **Two graph sources that must not be confused**: `.github/needs.dot` (task scheduling) vs `doc/graph/*.dot` / `utils/map` (image dependency map). They overlap but are maintained independently.
- `doc/context.json` is not a repo file — the `buildthedocs/btd` action in `doc.yml` generates it and `doc/conf.py` seeds `html_context` from it (safe locally thanks to the `is_file()` guard).
- **`jobs.yml` arch realities**: `riscv64` exists only for trixie (no riscv64 bullseye/bookworm images); several tools are pinned to bullseye-amd64 (e.g. `vtr`, `openroad`, `formal`, `superprove`); per-tool arch exclusions are recorded as inline comments.
- Tests depend on the `hdl/smoke-tests` submodule (pinned, last touched ~2022).
- **Registry presence ≠ scheduling.** Whether an image exists in the registry can be verified from its GitHub package page — `github.com/hdl/containers/pkgs/container/<collection>/<image>` (the flattened mirror path uses `%2F`, e.g. `debian%2Ftrixie%2Fpkg%2Ficestorm`) — independent of whether it is scheduled in the current run's dispatch. Use it to confirm a `FROM`/`COPY --from` dependency (e.g. `prog` pulling `pkg/icestorm` and `build/base`) is published even when not part of the scheduled subgraph.

## Type hint conventions

- Modern Python 3.10+ syntax repo-wide: `str | None` (not `Optional[str]`), `str | List[str]` (not `Union[...]`).
- Return types: `-> None` for all void functions; explicit return annotation otherwise. Do not annotate `self`/`cls`.
- Variables: annotate module-level constants; annotate locals where beneficial; always annotate function parameters (`args: Namespace` in CLI handlers, `idx: str`, `data: Dict[str, Any]`, etc.).
- Imports: `from typing import Dict, List, Set, Tuple, Any` (+ `Callable`, `Namespace` where needed); remove unused imports when touching a file.
- When mypy reports `import-not-found` for a compiled `.so` (e.g. `dockerfile.abi3.so`), use `# type: ignore[import-not-found]`. For packages without `py.typed`, use `# type: ignore[import-untyped]`.
- No `[tool.mypy]` config exists; verify manually with: `mypy --no-implicit-optional --check-untyped-defs --disallow-untyped-defs --warn-unused-ignores --enable-error-code=possibly-undefined --warn-return-any .github/*.py utils/pyHDLC/*.py utils/map/map.py utils/setup.py`
