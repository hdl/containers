# Audit: `cvc` on `debian/bullseye` (amd64)

- **Task**: `cvc`
- **Images**: `pkg/cvc` (single image; `pkgonly` task)
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev` (`b1c2f4e` "gtkwave: build upstream master (meson)")
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script)
- **Log**: `audits/logs/cvc.log`

## Overall result: FAIL

Build of `pkg/cvc` fails in the recipe `build()` step inside the `build` stage. Tests never run.

---

## `pkg/cvc` — FAIL

Command (as resolved by `BuildImage`, `default=True`, no `--target`/`--pkg` override):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/cvc \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye debian-bullseye/cvc
```

Exit status: 1 (`CalledProcessError` from `docker build`, logged as `=== FAIL pkg/cvc ... ===`; audit runner exited 1, `RESULT: FAIL`).

Symptoms / error lines:

```
#8 [build 3/3] RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build
#8 0.579 Cloning into '/tmp/cvc5'...
#8 27.74 Deleted tag 'latest' (was f294265c2b)
#8 27.78 *** configure.sh: no build type specified (try -h)
#8 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 1
```

Mechanism:
- `debian-bullseye/cvc/HDLC:40-48` `build()` clones `https://github.com/cvc5/cvc5.git` (default branch,
  unpinned `main`), deletes the fake `latest` tag, derives a version, then runs
  `./configure.sh --auto-download` (line 45).
- Upstream cvc5 `main` `configure.sh` now requires **exactly one build type**: `Usage: $0 <build type> ...`
  with `Build types (exactly one must be specified): unrestricted | stable | safe | debug | testing | competition`,
  and dies with `*** configure.sh: no build type specified (try -h)` when omitted. The recipe passes no
  build type, so the die() fires (upstream `die ()` prints that exact `*** configure.sh: ...` prefix).
- Unlike the older `configure.sh` (e.g. `cvc5-1.2.1`, 2024), where the build type was optional and `production`
  was documented, current `main` also retired `production` ("Use 'unrestricted' to have the previous behavior.").

Env facts:
- `ghcr.io/hdl/amd64/debian/bullseye/build/build` resolved from registry
  (`@sha256:2efef5e68e7b8604469bad05f262ac6b72fc4c0864de26b12c3851b6db9f00a8`).
- `makedepends` install (`[build 2/3]`) succeeded: 51 packages from `snapshot.debian.org`
  (`20260824T000000Z` pin, `[check-valid-until=no]` pattern from `debian-bullseye/base.dockerfile`)
  including `cmake 3.18.4`, `openjdk-11-jre-headless`, `flex`, `libgmp-dev`, `python3-venv` — no apt
  404s. So the bullseye-EOL mirror problem is NOT involved.
- `git clone` succeeded; `git tag -d latest` printed `Deleted tag 'latest' (was f294265c2b)`; the version
  derivation step after it did not fail.

## Root-cause hypothesis

**Recipe** (upstream drift in an unpinned `git clone`, by design per AGENTS.md), not test, not deps, not env.

- `debian-bullseye/cvc/HDLC:45` calls `./configure.sh --auto-download` with no build type; current cvc5
  `main` makes the build type mandatory, so configure aborts before CMake ever runs.
- The recipe's last change was `fee39c5` "cvc: needs venv" — it predates the upstream `configure.sh` API
  change, which is why this only surfaces now on unpinned `main`.
- Environment is healthy (apt, network, base image all fine); the failure is a 3-line abort inside the
  recipe build function, i.e. purely the configure invocation.

## Investigation notes

- `jobs_images('cvc')` → `['pkg/cvc']`; jobs wiring is `jobs.yml:114` `cvc: *SysDebianLegacyAmd64`
  (bullseye + bookworm, amd64 only; no riscv64/trixie). No `images.yml` entry → `default=True` infers
  the dockerfile from the name.
- The same broken invocation exists in the bookworm variant: `debian-bookworm/cvc/HDLC:45`
  (`./configure.sh --auto-download`). There is no unified `debian/cvc` recipe and no
  `debian-trixie/cvc`. Any fix must be applied to both `debian-bullseye/cvc` and `debian-bookworm/cvc`.
- `test/cvc.pkg.sh` exists, but the `testpkg` wrapper was never reached — the failure aborts the build
  stage, so no test verdict was produced.
- Upstream `configure.sh` (`raw.githubusercontent.com/cvc5/cvc5/main/configure.sh`) confirms the new
  mandatory build type and the `production`→`unrestricted` rename ("Use 'unrestricted' to have the
  previous behavior."). The old optional-build-type behavior is retained in `cvc5-1.2.1`.

## Recommended next step

Add a build type to the configure invocation in both recipes, using the equivalent of the previous
default (`production`, now renamed `unrestricted`):

```
./configure.sh --auto-download unrestricted
```

Apply to `debian-bullseye/cvc/HDLC:45` and `debian-bookworm/cvc/HDLC:45` (identical line). This is the
repo's expected response to unpinned-main drift. Then re-run this audit command; `pkg/cvc` must reach
`=== PASS pkg/cvc ===` (which also runs `test/cvc.pkg.sh` via the testpkg wrapper, currently untested).