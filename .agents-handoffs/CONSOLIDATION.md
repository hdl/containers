# CONSOLIDATION

> Working knowledge for the "hdl/containers" repo about consolidating Debian tool
> recipes into the unified `debian/` directory, and about extending tool coverage
> to the bookworm (and, recently, trixie) collections. This file complements AGENTS.md.
> It is a living document: keep it in sync when recipes are consolidated or collections
> are changed. No commit-hash or SHA references are used on purpose; identify work by
> collection/tool/path/label instead.

## Goal

- Audit, consolidate and **unify** Dockerfile recipes for as many EDA tools as possible.
  This removes by-tool, per-version duplication and makes the toolset easier to maintain.
- Extend the set of tools that are built for the **bookworm** collection (and, recently,
  the **trixie** collection), reducing the number of tools pinned to the legacy bullseye
  collection.
- Consolidation is the *mechanism* used to achieve the broader goal of widening tool
  coverage; the two are intentionally tackled together.

## The resolution model

This is the key rule. For an image `<collection>/<image>` (e.g.
`debian/bookworm/yosys`), the build tool resolves the dockerfile in this order:

1. Version-specific directory first: `debian-<version>/<image>.<recipe>`.
2. If absent, the unified directory: `debian/<image>.<recipe>`.

It is implemented inline in `BuildImage` (`utils/pyHDLC/__init__.py`, no helper
function): a loop probes `debian-<version>/` before falling back to `debian/`.

Versions are bullseye, bookworm and trixie encoded as `debian-bullseye/`,
`debian-bookworm/` and `debian-trixie/` subdirectories; `debian/` is the unified
collection for recipes shared by all versions.

`ARG REGISTRY` is the build-time registry base, resolved per collection and version in
`utils/pyHDLC/jobs.yml` (arch anchors like `*SysDebian*`). Version-specific recipes
(`debian-<version>/<tool>/Dockerfile`) default to their own version:

- bullseye: `ghcr.io/hdl/debian/bullseye`
- bookworm: `ghcr.io/hdl/debian/bookworm`
- trixie: `ghcr.io/hdl/debian/trixie`

Unified recipes (`debian/<tool>/Dockerfile`) always default to `ghcr.io/hdl/debian/bullseye`.
They are only relevant when building the image directly with docker (e.g. testing a
recipe outside CI). The CI always passes `REGISTRY` as a build argument.

## Consolidation mechanics

- Recipes are moved from `debian-<version>/` into `debian/` using `git mv` (which records
  the rename), then consolidated into a single recipe if the content is not
  version-dependent.
- If a tool needs a version-specific variant (e.g. a different apt package name), the
  unified recipe is kept for the common case and a version-specific recipe is added only
  for the diverging version.
- Alternatively, when the divergence is limited to a few package names, a single unified
  HDLC can detect the collection via `case "$REGISTRY"` and set `HDLC_*` variables
  consumed by the arrays. This avoids version-specific directories entirely. The
  Dockerfile must re-declare `ARG REGISTRY` after each `FROM` that sources the HDLC
  (a pre-`FROM` ARG is only visible in `FROM` instructions). Error on unknown collections.
- Wiring:
  - `utils/pyHDLC/jobs.yml`: the `default`/`runonly` section (and the `pkg`/`pkg/pkg`
    tasks) map each tool to an arch anchor. `*SysDebianBullseyeAmd64` is
    bullseye+amd64 only; `*SysDebianAmd64` (or the collection-default equivalent)
    builds the tool on all supported versions for a given arch set. See "Jobs wiring
    to widen" for what changing an anchor does.
  - `utils/pyHDLC/images.yml` (and by-tool overrides) defines the Dockerfile to use, with
    the dockerfile routed by the resolution rule above.
  - `.github/needs.dot` defines the dependency DAG from which the scheduler derives the
    build order recipes; `formal`, `prog`, etc. are resolved per collection but the graph
    is version-agnostic.
  - `.github/workflows/scheduler.yml` `HDLC_PUSH` lists the set of jobs that a push runs
    instead of the scheduled dispatch (used for TEST/consolidation runs).
- A document describing the DAG/scheduler mechanics, dispatch syntax (`F`, `T>`, `>T`, …)
  and further consolidation pattern documentation is in `doc/dev/GraphGeneration.rst`,
  `doc/dev/CI.rst` and the accompanying `CONSOLIDATION.md`-adjacent developer docs.

When consolidating, keep the unified recipe the *default* (using the version-agnostic
package names), and use version-specific overrides only for genuine divergence.

**Recipes use unpinned `git clone` of upstream `main`/`master` by design** — the repo's
purpose is to continuously test upstream branches of EDA tools and catch breakage early.
Reproducibility comes from the `FROM scratch AS version` stage + `dist/` exports, not from
pinning source commits. When a recipe breaks against an unpinned clone, treat it as
expected upstream drift and fix the recipe (or its dependencies), don't pin the clone.

`debian-bullseye/base.dockerfile` is a *temporary* keep-alive, not a version-specific
inheritance: bullseye reached EOL (2026-08-31), yet official `debian:*-slim` images keep
pointing at `deb.debian.org`, so the base pins `snapshot.debian.org` (+
`[check-valid-until=no]`) in `sources.list`. This keeps bullseye buildable only until the
remaining bullseye-only tools graduate to bookworm/trixie; bullseye will then be removed
entirely.

## The consolidation commit history (reference)

The following steps were performed on the consolidations that have been merged:

- `icestorm`, `gtkwave`, `magic`, `yosys`, `z3`: consolidated from bullseye+bookworm
  into `debian/` via git-moves. `icestorm` and `gtkwave` have their `jobs.yml` anchors
  widened to `*SysDebianDefaultArchSet` (the default set includes bookworm and trixie;
  `gtkwave` also refreshes its bundled `config.guess`/`config.sub` from automake so the
  riscv64 build can identify the platform);
  `magic`, `yosys`, `z3` remain on the `*SysDebianLegacy*` anchors until their trixie
  builds are verified (follow-up).
- `prog`: consolidated from bullseye into `debian/` (recipe renamed to
  `debian/prog.dockerfile`), jobs anchor widened.
- `ghdl`, `ghdl/llvm`: built on bullseye/bookworm/trixie via version-specific recipes
  with HDLC extraction (kept un-consolidated — gnat/llvm/backtrace diverge; toolchain
  facts in "Migrating to trixie"), `jobs.yml` anchor widened to `*SysDebianAmd64`.
- `nvc`, `cvc`, `klayout`: consolidated from `debian-{bullseye,bookworm,trixie}/` into
  unified `debian/<tool>/` recipes with a single HDLC that detects the collection via
  `case "$REGISTRY"` (patterns `*bullseye)`/`*bookworm)`/`*trixie)`, plus an erroring
  `*)` for unknown collections). The Dockerfile re-declares `ARG REGISTRY` after each
  `FROM` that sources the HDLC. Version-dependent packages: nvc (`libllvm11/14/19`),
  cvc (`openjdk-11/17`), klayout (`libgit2-1.1/1.5/1.9`, `libpython3.9/3.11/3.13`).
- The bullseye pins for other tools remain.

## Tools only in the bullseye set

Some tools are only available on bullseye (not bookworm nor trixie) and are listed below,
with the reason they were not ported yet.

| Tool | Bullseye-pinned because... | Status |
|---|---|---|
| formal | depends on `pono` and `superprove` (both bullseye-only), plus python2.7 | blocked by deps |
| superprove | needs python2.7 toolchain (removed on bookworm/trixie) | hard block (python2) |
| pono | build/makedeps hoisted earlier (try on bookworm failed) | try again |
| openroad | or-tools binary/debian-11-pinned; build needs newer libboost+libomp; only bullseye-amd64 images exist | blocked (or-tools/prebuilt deps) |
| f4pga/apidga | never attempted (large conda/f4pga stack) | not attempted |
| vtr | never attempted (only bullseye-amd64 currently) | not attempted |

(The full bullseye audit — 47 tasks, 29 PASS / 18 FAIL, with per-task failure reports —
is tracked in `audits/README.md`.)

(`conda`, `cvc`, `verible`, `xyce`, `verilator` and `apicula` are also
`*SysDebianLegacy*`-pinned — the table above is the intentionally blocked set, not the
exhaustive legacy set.)

Facts to remember:

- Bullseye is the only collection with `python2` and `openjdk-11` for the formal-ish tools.
- `formal` is bullseye-only because it is composed of `pono` + `superprove` (and
  `superprove` needs python2), so widening it requires both of its dependents to move
  first; `formal` therefore stays pinned to bullseye.
  - `formal` was attempted for bookworm (and `superprove`/`pono`/`openroad`), but the
    attempt was dropped from bookworm and lives in a `bookworm-failing` branch. That is
    why they are bullseye-pinned. This is a known, documented reason; do not spend effort
    re-deriving it.
- `openroad` is bullseye-amd64-pinned because it needs a prebuilt or-tools binary (the
  `or-tools_amd64_debian-11_cpp_v<X>.tar.gz` asset on github releases), which only ships
  for debian-11; and old swig/libboost in the build. Also its apt makedepends use
  `libpython3.9`/`libomp-11-dev` (bullseye-specific).
- `vtr` is bullseye-amd64-pinned simply because nobody has ported it; it has no
  bullseye-specific apt dependency. It is the easiest to port; it is also the only one
  that is *currently* scheduled per bullseye only.
- `formal`/`superprove` are bullseye-pinned via `jobs.yml` runonly anchors
  (`*SysDebianBullseyeAmd64`).

## Jobs wiring to widen

Modifying `utils/pyHDLC/jobs.yml`:

- Widening an anchor from bullseye-only to the default arch set multiplies the job across
  bullseye, bookworm and trixie (read the anchors in `jobs.yml` to know which arch sets
  apply).
- For an image (`default`/`runonly`/`pkg`), the *dependency* sets (e.g. which base/pkg
  images must be pulled/built) are not widened by changing the tool's own anchor; they are
  scheduled by inner anchors / the graph. That is usually what you want, but be aware
  when a tool's `FROM $REGISTRY/build/…` or `COPY --from=$REGISTRY/pkg/…` dependency is
  not scheduled in the same subgraph (see below).

## The registry as source of truth for image existence

Whether an image exists in the registry is independent of whether it is scheduled in a
given run. The reliable source of truth is each image's GitHub package page:

`github.com/hdl/containers/pkgs/container/<collection>/<image>`

(For the flattened mirror path — default collection/arch — the flattened name is the
flat registry path, expressed with `%2F`, e.g. `debian%2Ftrixie%2Fpkg%2Ficestorm`.)
This can be used to verify that a `FROM`/`COPY --from` dependency of an image already
exists in the registry, even though it is not scheduled in the current dispatch (e.g. a
bare task dispatch or a consolidation run). If the dependency image is not present at
build time, the build fails at the `FROM`/`COPY --from` step; otherwise the built image
can be published independently of the DAG.

Notes:

- A request for building/tagging an image alone (`prog`, `>prog`, etc.) doesn't pull its
  ancestors; each collection/arch is a separate FROM-independent subgraph. This is
  intentional for TEST/consolidation runs, but the FROM dependencies are only satisfiable
  when the corresponding images are already in the registry (published by a previous
  scheduled push) — see above about the package page.
- For the scheduler (see `dispatch.py` and `needs.dot`), a dispatch like `prog>` includes
  `prog` and its dependents; `>prog` includes `prog` and its ancestors (this is how
  registry presence can be verified locally, and how a bare `prog` behaves in TEST).

## Migrating to trixie

- Trixie is becoming the default collection (on dev branches); `debian-trixie/` is already
  populated with version-specific recipes for tools that need them. Unified `debian/`
  recipes resolve for trixie too.
- For `prog` on trixie, the apt package is `libftdi1` (not `libftdi1-2`, which is the
  source-package name on bullseye/bookworm). `libftdi1-2` also exists on trixie, and the
  unified recipe installs `libftdi1-2`; hence a trixie-specific variant is *not* required.
- `ghdl` is intentionally **not unified**: it keeps three version-specific recipes
  (`debian-bullseye/ghdl/Dockerfile`, `debian-bookworm/ghdl/Dockerfile`,
  `debian-trixie/ghdl/Dockerfile`) with version-specific HDLC files because the
  gnat/llvm/backtrace package sets and configure flags diverge per release — yet it is
  wired for trixie (`jobs.yml` anchor `*SysDebianAmd64`), the deliberate exception to
  the unified-recipe-default rule.
  Ada/Debian facts learned while porting it (`libbacktrace-dev` ships **only on trixie**;
  GHDL master currently accepts LLVM up to 19 — `configure check_version`):

  | collection | gnat | llvm | backtrace (`--with-backtrace-lib=`) |
  |---|---|---|---|
  | bullseye | `gnat-9` | `llvm-11-dev` | `$(dpkg -L libgcc-9-dev \| grep libbacktrace.a)` |
  | bookworm | `gnat-12` | `llvm-14-dev` | `$(dpkg -L libgcc-12-dev \| grep libbacktrace.a)` |
  | trixie | `gnat-14` (+ `ln -s gnatmake-14 gnatmake`: no unversioned alternative) | `llvm-19-dev`/`llvm-config-19`/`libllvm19` | `$(dpkg -L libbacktrace-dev \| grep libbacktrace.a)` |

  - `gnat-<N>` pulls in `gcc-<N>` → `libgcc-<N>-dev`, which is where the
    `libbacktrace.a` static archive lives on bullseye/bookworm.
  - GHDL `configure --default-pic` is passed explicitly: the upstream PIC auto-detect
    keys off `gcc` defaults, while the build toolchain is clang (the recipe never sets
    `CC=gcc`).

## Open follow-ups

- Restore the `jobs.yml` runonly `formal`/`sim` anchors to the correct
  `*SysDebianLegacy*` after stopping to use a bare-task TEST dispatch (not a current
  change, but a known foot-gun when building TEST branches that rely on a pre-published
  registry).
- Reattempt the 4 bookworm-failing tools (`formal`, `superprove`, `pono`, `openroad`) if
  their blockers are lifted upstream (or-tools debian-12 binaries; python2
  alternatives; boost/libomp unification). They remain bullseye-only until then.
- `prog` on trixie is split between bullseye (very recent) and the unified recipe; verify
  the trixie build once the scheduler restores the full collection run.
- `ghdl-yosys-plugin` is still `*SysDebianLegacyAmd64`-pinned (blocker: its build
  breaks against GHDL master API skew — see `audits/ghdl-yosys-plugin.md`). `ghdl` itself
  is amd64-only; arm64 widening across the three collections is still open.

## How to test after a consolidation

Ensure the venv is set up and pyHDLC is available (see AGENTS.md "Prerequisites" and
"Getting Started"). Then:

1. Build the image locally for the affected versions (e.g.
   `pyHDLC build -c debian/bullseye -d prog`, etc.).
2. Verify the built image has the expected content (version fingerprint in
   `/opt/…`, `pkg`/runtime split) — smoke tests are in `test/`.
3. Use a TEST scheduler run (bare task) only if the FROM dependencies are already in the
   registry; otherwise run a `>task` window or run the full collection so the DAG builds
   the prerequisites first.
4. Confirm via the package page that the produced images were actually pushed (see
   "registry as source of truth").
