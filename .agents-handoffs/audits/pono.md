# Audit Report: `pono` (debian/bullseye, amd64)

| Field | Value |
|---|---|
| **Task** | `pono` (pkgonly) |
| **Date** | 2026-09-15T06:47:38Z |
| **Branch** | `umarcor/dev` |
| **Collection** | `debian/bullseye` |
| **Architecture** | `amd64` |
| **Registry** | `ghcr.io/hdl` |

## Image: `pkg/pono`

### Build Invocation

```python
BuildImage('pkg/pono', collection='debian/bullseye', architecture='amd64', default=True, test=True)
```

**Result:** FAIL
**Exit status:** non-zero (CalledProcessError from `docker build`)

### Symptoms / Error Lines

```
#7 4.418 /tmp/pono/deps/smt-switch/contrib/common-setup.sh: line 59: wget: command not found
#7 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && build" did not complete successfully: exit code: 127
```

The build clones pono successfully, then runs `./contrib/setup-smt-switch.sh`. That script clones smt-switch and checks out a specific commit (`460b5fd`). During its setup, it sources `deps/smt-switch/contrib/common-setup.sh`, which calls `wget` on line 59 to download something (likely an archive). The `wget` binary is not installed in the build container.

### Environment Facts

- Dockerfile: `debian-bullseye/pono/Dockerfile`
- HDLC recipe: `debian-bullseye/pono/HDLC`
- Base image: `ghcr.io/hdl/amd64/debian/bullseye/build/build:latest` (sha256:2efef5e6...)
- Build step `2/3` (apt-get install) succeeds — all declared `makedepends` install cleanly
- Build step `3/3` (the `build()` function) fails immediately in the first sub-step (`setup-smt-switch.sh`)
- The `makedepends` array in the HDLC recipe does **not** include `wget` or `curl`

### Root-Cause Hypothesis

**Recipe issue — missing dependency.** The upstream `smt-switch` `common-setup.sh` helper (invoked transitively by pono's `setup-smt-switch.sh`) uses `wget` to fetch assets, but the pono recipe's `makedepends` does not list `wget`. No other recipe in the repository references `wget` either, so this was likely masked previously if smt-switch's script used a different download method or if the base image happened to include it.

The required fix is to add `wget` (and/or `curl` as a belt-and-suspenders option) to the `makedepends` array in `debian-bullseye/pono/HDLC`.

### Investigation Notes

- Grep across all `HDLC` files in the repo shows zero prior use of `wget` or `curl` as declared dependencies — this dependency was never accounted for.
- The smt-switch `common-setup.sh` is fetched at build time (cloned from upstream), so the recipe has no control over which tools it calls. Adding `wget` to `makedepends` is the standard mitigation pattern.

### Recommended Next Step

Add `wget` to the `makedepends` array in `debian-bullseye/pono/HDLC` (line ~27–40), e.g.:

```bash
makedepends=(
  autoconf
  binutils
  bison
  cmake
  flex
  libbison-dev
  libfl-dev
  libgmp-dev
  m4
  openjdk-11-jre-headless
  patch
  python3-toml
  wget
)
```

Then re-run the audit to confirm the build succeeds past `setup-smt-switch.sh`.
