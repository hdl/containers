# AGENTS.md

## Repository Overview

This is a **recipe + CI-as-code** repository: it builds and tests OCI/Docker images of open-source EDA (Electronic Design Automation) tools. There is almost no application code — everything exists to feed `docker build`, the GitHub Actions CI, and the Sphinx docs.

- Images are pushed to `ghcr.io/hdl` and mirrored to Docker Hub (`docker.io/hdlc`, root namespace).
- `gcr.io/hdl-containers` was deprecated (shut down 2025) and removed from the codebase.
- Defaults in code: registry `ghcr.io/hdl`, collection `debian/bullseye` (still, in 2026), architecture `amd64`. The trixie-as-default change lives on dev branches only, so feature-branch checkouts may already default to `debian/trixie` (`__init__.py`, `utils/bin/dockerRelease`, `doc/CollectionsAndArchitectures.rst`).

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
| `.github/` | CI brain: `needs.dot`, `dispatch.py`, `watch.py`, `results.py`, `summary.py`, composite actions |
| `.github/workflows/` | `scheduler.yml`, `watch.yml`, `build-test-release.yml`, `doc.yml`, `formal.yml`, `impl.yml` |
| `doc/` | Sphinx docs; user-facing `doc/graph/*.dot` image maps |
| `usbip/` | USB/IP utils for Mac/Windows USB passthrough (tangential) |

## Core model

- **Namespaces.** Every image is `registry/architecture/collection/image`, e.g. `ghcr.io/hdl/amd64/debian/bullseye/yosys`. Optional segments are dropped for default collection/arch when mirroring (`dockerRelease`).
- **Tasks vs. images.** A *task* is a `needs.dot` node and `jobs.yml` key that expands to one or more images. Example: task `base` → `build/base`, `build/build`, `build/dev`; task `nextpnr` fans out over `ice40/ecp5/nexus/generic`.
- **Config-driven.** `utils/pyHDLC/jobs.yml` (`default`/`pkgonly`/`runonly`/`custom` sections) states which images×collections×architectures each task builds. `images.yml` holds per-image overrides of `dockerfile`/`target`/`argimg`. `pyHDLC jobs <task>` cross-products these into the GHA matrix.
- **pkg vs runtime.** Every tool yields two artifacts: a `pkg/<tool>` image (staged content from `FROM scratch AS pkg`) and the runtime tool image (`FROM <collection>.../base; COPY --from=build ...`). `pkgonly`/`runonly` build one, `default` builds both.
- **Base layering.** `build/base → build/build → build/dev` is the shared three-stage base (`debian/base.dockerfile`). The `base`/`build`/`dev` terms are reused as *namespace prefixes* (`build/impl`, `build/nextpnr/*`), which can be confusing.
- **Recipes.** `HDLC` files are sourced inside builds (`RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build`) and expose `makedepends`, `depends`, `testdepends`, `build()`, `runtests()`.

## Building Images

Use the pyHDLC CLI (installed via `utils/setup.sh`) or the Python API:

```bash
./utils/pyHDLC/cli.py build -a amd64 -c debian/bullseye -d yosys --test
```

```python
from pyHDLC import BuildImage, TestImage
BuildImage("yosys", collection="debian/bookworm", architecture="amd64", test=True)
```

Notes:
- `-d/--default` infers dockerfile/target/argimg from the image name; `-p/--pkg` targets the `pkg` stage.
- The Dockerfile is resolved inline in `BuildImage` (`__init__.py`, no helper function): it probes `debian-<version>/` first, then falls back to unified `debian/`. Images not in `debian/` (e.g. `formal`, `ghdl`, `impl`, `nextpnr`, `sim`) build only for bullseye/bookworm, **not** trixie; unified recipes resolve for any Debian version, but `jobs.yml` must wire them into a trixie-aware `sys` set (`magic`/`yosys`/`z3` are unified yet still wired to `SysDebianLegacy*` only; `gtkwave` was widened to `SysDebianDefaultArchSet` in the gtkwave-lts lane (its recipe refreshes the bundled `config.guess`/`config.sub` from automake so the riscv64 build can identify the platform) and verifies on bullseye/bookworm/trixie).
- Build args: `SYSIMAGE=<arch>/<collection>[:]` (base dockerfile, `/`→`:`), `REGISTRY=<registry>/<arch>/<collection>` (tool dockerfiles), `IMAGE=<argimg>`.
- Builds use `--platform linux/<arch>`; any `arm*` architecture label is normalized to `linux/arm64` (`_NormalisePlatform`). Cross-arch builds need `utils/setup.sh` (qus binfmt via `aptman/qus`).

## Testing Images

Tests run *inside* the container, never locally. `TestImage` bind-mounts `<repo>/test` at `//wrk` and invokes `//wrk/<script>.sh`:

```bash
docker run --rm -v /path/to/repo/test://wrk ghcr.io/hdl/amd64/debian/bullseye/yosys //wrk/yosys.sh
```

- Script names are the image name with `:`→`--` and `/`→`--` (e.g. `ghdl--llvm.sh` for `ghdl/llvm`).
- Package images are tested via `*.pkg.sh` through a dedicated `utils/pyHDLC/testpkg.dockerfile` wrapper (copies `/opt/<tool>` from the pkg image into an Alpine scratch test).
- Scripts source `test/_env.sh`, then call `./smoke-tests/<tool>.sh` from the submodule, then `./_todo.sh` (placeholder for pending tests).
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
- GitHub Actions still lacks YAML merge keys — config relies on anchors, and `build-test-release.yml:42-45` documents the workaround.
- `yamldataclassconfig` is pinned `<2` (`643caf49`).
- Tests depend on the `hdl/smoke-tests` submodule (pinned, last touched ~2022).
- **EOL Debian releases don't self-heal.** When a release goes EOL (bullseye: 2026-08-31), official `debian:*-slim` images keep pointing at `deb.debian.org` forever — never `archive.debian.org`. Pool `.debs` get drained from `deb.debian.org` mid-migration while the Packages index still advertises them → deterministic apt 404s (`libxml2 ...+deb11u10`). Fix: pin `snapshot.debian.org` and add `[check-valid-until=no]` per source (snapshot Release files keep the original `Valid-Until`, expired ~30 days after snapshot). Working pattern: `debian-bullseye/base.dockerfile` (flips comments in `/etc/apt/sources.list`, keeping the live-mirror lines as reference).
- **Unpinned `git clone` in HDLC recipes is intentional** — the repo's purpose is to continuously test upstream `main`/`master` branches of EDA tools, not pinned releases. This catches breakage early. Reproducibility is achieved via the `FROM scratch AS version` stage + `dist/` exports, not by pinning source commits.
- **Registry presence ≠ scheduling.** Whether an image exists in the registry can be verified from its GitHub package page — `github.com/hdl/containers/pkgs/container/<collection>/<image>` (the flattened mirror path uses `%2F`, e.g. `debian%2Ftrixie%2Fpkg%2Ficestorm`) — independent of whether it is scheduled in the current run's dispatch. Use it to confirm a `FROM`/`COPY --from` dependency (e.g. `prog` pulling `pkg/icestorm` and `build/base`) is published even when not part of the scheduled subgraph.

## Type hint conventions

- Modern Python 3.10+ syntax repo-wide: `str | None` (not `Optional[str]`), `str | List[str]` (not `Union[...]`).
- Return types: `-> None` for all void functions; explicit return annotation otherwise. Do not annotate `self`/`cls`.
- Variables: annotate module-level constants; annotate locals where beneficial; always annotate function parameters (`args: Namespace` in CLI handlers, `idx: str`, `data: Dict[str, Any]`, etc.).
- Imports: `from typing import Dict, List, Set, Tuple, Any` (+ `Callable`, `Namespace` where needed); remove unused imports when touching a file.
- Dependency assumption (user-declared): requirements are always installed first, so import-not-found should never occur for packages listed in utils/pyHDLC/requirements.txt (pyAttributes, yamldataclassconfig<2) and utils/map/requirements.txt (dockerfile, graphviz).
- Exception discovered: dockerfile is a compiled .so extension (dockerfile.abi3.so) — mypy reports import-not-found for it even when installed; it needs # type: ignore[import-not-found] (not import-untyped).
- yamldataclassconfig ships py.typed → no ignore needed at all when installed.
- setuptools never ships py.typed → `utils/setup.py:28` uses `# type: ignore[import-untyped]`.
- No `[tool.mypy]` config exists; verify manually with: `mypy --no-implicit-optional --check-untyped-defs --disallow-untyped-defs --warn-unused-ignores --enable-error-code=possibly-undefined --warn-return-any .github/*.py utils/pyHDLC/*.py utils/map/map.py utils/setup.py`
- .github scripts run in GHA where networkx/tabulate are installed → only import-untyped needed there.
