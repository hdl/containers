# Audit: `openroad` on `debian/bullseye` (amd64)

- **Task**: `openroad`
- **Images**: `pkg/openroad`, `openroad`, `pkg/openroad/gui`, `openroad/gui`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev` (`8761c15` "AGENTS.md: document _anchors as loader-only config scaffolding")
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script). The `#dir` pkg syntax is handled by `default=True`.
- **Log**: `audits/logs/openroad.log`
- **Audit runner exit**: 1 (`RESULT: FAIL`)

## Overall result: FAIL

All four images fail in the shared `build()` recipe step (`RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build`), at the very first command (the Boost download), with `gzip: stdin: not in gzip format`. Tests never run.

Matrix as returned by `job_images('openroad')` → `['pkg/openroad', 'openroad', 'pkg/openroad/gui', 'openroad/gui']`, matching `jobs.yml:202-208` (`sys: *SysDebianBullseyeAmd64`, i.e. bullseye/amd64 only, consistent with the per-repo note that openroad is pinned to bullseye-amd64).

---

## `pkg/openroad` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 5):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/openroad \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  --target pkg debian-bullseye/openroad
```

Exit status: 1 (`CalledProcessError` from `docker build`); the in-image step itself failed with exit code 2. Logged as `=== FAIL pkg/openroad ... ===`.

Symptoms / error lines:

```
#8 [build 1/1] RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build
#8 1.435 gzip: stdin: not in gzip format
#8 1.435 tar: Child returned status 1
#8 1.435 tar: Error is not recoverable: exiting now
#8 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 2
>  [build 1/1] ...
Dockerfile:46  >>> RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && build     (Dockerfile:46)
```

Preceding stages were healthy:
- `[setup 2/3]`: `makedepends` install OK — 39 packages from `snapshot.debian.org` (`20260824T000000Z` pin, `[check-valid-until=no]`), no apt 404s. The bullseye-EOL mirror problem is NOT involved.
- `[setup 3/3]`: `setup()` OK — `git clone --recursive` of OpenROAD `master` + submodules `src/sta` (OpenSTA), `third-party/abc`, `third-party/slang-elab` (povik/yosys-slang) with nested `fmt` + `slang`; version written to `/tmp/hdlc.openroad.version`.

---

## `openroad` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 444):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/openroad \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  --target openroad debian-bullseye/openroad
```

Exit status: 1 (`CalledProcessError`); in-image step exit code 2. Logged as `=== FAIL openroad ... ===`.

Symptoms / error lines (Dockerfile:46, `[build 1/1]`, `#11 1.194`):

```
#11 1.194 gzip: stdin: not in gzip format
#11 1.195 tar: Child returned status 1
#11 1.195 tar: Error is not recoverable: exiting now
#11 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 2
```

Same root cause as `pkg/openroad`; the `run` (runtime deps) stage install was already `CANCELED` once the failing `build` step was hit.

---

## `pkg/openroad/gui` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 524):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/openroad/gui \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  --target pkg-gui debian-bullseye/openroad
```

Exit status: 1 (`CalledProcessError`); in-image step exit code 2. Logged as `=== FAIL pkg/openroad/gui ... ===`.

Symptoms / error lines (Dockerfile:59, the `build` call inside `build-gui`, `#8 1.425`):

```
#8 1.425 gzip: stdin: not in gzip format
#8 1.425 tar: Child returned status 1
#8 1.425 tar: Error is not recoverable: exiting now
#8 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 2
```

The `build-gui` stage's `makedepends_gui` install (`qtbase5-dev` + ~90 qt/x11/gl packages) completed successfully before the shared `build()` call hit the same Boost download failure.

---

## `openroad/gui` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 1798 bis; build tail):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/openroad/gui \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  --target gui debian-bullseye/openroad
```

Exit status: 1 (`CalledProcessError`); in-image step exit code 2. Logged as `=== FAIL openroad/gui ... ===`.

Symptoms / error lines (Dockerfile:59, `[build-gui 2/2]`, `#13 1.160`):

```
#13 1.160 gzip: stdin: not in gzip format
#13 1.160 tar: Child returned status 1
#13 1.160 tar: Error is not recoverable: exiting now
#13 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 2
```

Same root cause as `pkg/openroad/gui` (both go through `build-gui`, which calls the same `build()`). The `depends_gui` runtime install was CANCELED once the `build-gui` step failed.

---

## Root-cause hypothesis

**Recipe** (upstream drift in the unpinned `git clone` of OpenROAD `master` + a decommissioned external download host), not test, not deps, not env.

`debian-bullseye/openroad/HDLC:50-76` `build()` downloads two tarballs through `curl ... | tar -xz`:

1. **Boost** (`HDLC:57`): `https://boostorg.jfrog.io/artifactory/main/release/${boostVersion}/source/boost_${boostVersion//./_}.tar.gz`
2. **or-tools** (`HDLC:69`): `https://github.com/google/or-tools/releases/download/v<major>/or-tools_amd64_debian-11_cpp_v${orToolsVersion}.tar.gz`

The failure is `gzip: stdin: not in gzip format`, i.e. non-gzip bytes flowed through the pipe. Two independent breakages converge on that:

- **The Boost host is dead.** `boostorg.jfrog.io/artifactory` has been decommissioned and now answers **any path** (verified live for both the versioned URL and a garbage path) with **HTTP 200** and an ~11 KB HTML "reactivate-server" landing page from `landing.jfrog.com`. `curl -fsSL` treats 200 as success, so the HTML is piped into `tar -xz` → instant gzip failure (~1.2-1.4 s into the step, matching the small 11 KB payload).
- **The version parsing is stale.** `HDLC:56`/`HDLC:68` extract versions with `grep boostVersionBig=`, `grep boostVersionSmall=`, `grep orToolsVersionBig=`, `grep orToolsVersionSmall=`. Current upstream `etc/DependencyInstaller.sh` renamed these to **uppercase** `BOOST_VERSION_BIG/SMALL` and `OR_TOOLS_VERSION_BIG/SMALL` (verified live: `BOOST_VERSION_SMALL="1.89.0"`, `OR_TOOLS_VERSION_SMALL="9.14.6206"`), so the greps match nothing and the derived version string collapses to `"."` → URL `https://boostorg.jfrog.io/artifactory/main/release/./source/boost_..tar.gz` (also returns the 200 HTML page). Even if the host had been alive, the parse break would still produce a broken URL today.

The **or-tools** URL itself is fine: `https://github.com/google/or-tools/releases/download/v9.14/or-tools_amd64_debian-11_cpp_v9.14.6206.tar.gz` returns HTTP 200 with a valid gzip payload (54 MB), but that step is never reached because Boost fails first. (Its version extraction is equally broken by the uppercase rename.)

Env facts:
- `ghcr.io/hdl/amd64/debian/bullseye/build/dev:latest@sha256:f928b0f1...` and `build/base:latest@sha256:23a040c6...` resolved fine from the registry; `setup` stages fully cached/reused.
- Network, apt (`snapshot.debian.org`, `20260824T000000Z` bullseye pin), and the recursive `git clone` all healthy — netgen/cvc-style EOL-mirror or network issues are excluded.
- This is the repo's intentional unpinned-`master` design (AGENTS.md: "Unpinned git clone in HDLC recipes is intentional ... This catches breakage early") catching two upstream/external drift events at once.

## Investigation notes

- `job_images('openroad')` → `['pkg/openroad', 'openroad', 'pkg/openroad/gui', 'openroad/gui']`; `jobs.yml:202-208` wires openroad to `*SysDebianBullseyeAmd64` (bullseye/amd64 only — no bookworm/trixie/riscv64 variant exists in `debian-bullseye/`; confirmed the upstream rename affects the `debian-bullseye/openroad/HDLC` copy).
- `setup()` (HDLC:43-48) succeeded; the version file was produced, so the checkin would have reached `version`/`dist` on success.
- Live URL probes (2026-09-15):
  - `https://boostorg.jfrog.io/artifactory/main/release/1.89.0/source/boost_1_89_0.tar.gz` → **200, `text/html`** (jfrog landing page, 11 447 B).
  - `https://boostorg.jfrog.io/artifactory/main/release/./source/boost_..tar.gz` → **200, `text/html`** (same landing page) — this is the URL the current recipe parses out of upstream `master`.
  - `https://archives.boost.io/release/1.89.0/source/boost_1_89_0.tar.gz` → **200, `application/octet-stream`**, valid gzip (190 MB) — the host current upstream itself uses (`DependencyInstaller.sh:511`).
  - `.../or-tools/releases/download/v9.14/or-tools_amd64_debian-11_cpp_v9.14.6206.tar.gz` → **200, `application/octet-stream`**, valid gzip (54 MB).
- Recipe last touched by `7bc4e9a` (2023-07-01) "extract boost and or-tools versions from DepencencyInstaller.sh" — predates both the jfrog decommission and the upstream variable rename.
- `test/openroad.sh` and GUI-related test scripts exist, but the `pkg`/`run` test stages were never reached for any of the four images.
- Note (non-blocking): the uppercase-renamed `OR_TOOLS_VERSION_SMALL="9.14.6206"` → existing recipe URL pattern still matches the live asset, so only the extraction needs fixing there.

## Recommended next step

Patch `debian-bullseye/openroad/HDLC` `build()`:

1. Read versions from the current upstream names (`BOOST_VERSION_SMALL`, `OR_TOOLS_VERSION_SMALL`, uppercase), e.g.
   `grep '^BOOST_VERSION_SMALL=' ... | sed ...` (or make the existing greps case-insensitive and keep both spellings) so the parsed versions are again non-empty.
2. Switch the Boost mirror from the dead `boostorg.jfrog.io` to the archive used by upstream today:
   `https://archives.boost.io/release/${boostVersion}/source/boost_${boostVersion//./_}.tar.gz`
   (`boostVersion` = `1.89.0` → `boost_1_89_0.tar.gz`, verified reachable and gzip).
3. Keep the or-tools URL pattern unchanged; only its version extraction needs the uppercase fix.

Then re-run the same audit command. All four images must reach their `=== PASS ... ===` markers, which would also exercise `test/` for the first time in this audit run.