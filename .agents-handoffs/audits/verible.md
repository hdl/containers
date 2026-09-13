# Audit report: verible

- **Task:** `verible`
- **Images:** `pkg/verible`, `verible`
- **Date:** 2026-09-15
- **Branch:** `umarcor/dev` (HEAD 8761c15)
- **Collection:** `debian/bullseye`
- **Architecture:** `amd64`
- **Registry:** `ghcr.io/hdl/amd64/debian/bullseye`
- **Result:** FAIL (2/2 images)
- **Log:** `audits/logs/verible.log`

## pkg/verible

- Call: `BuildImage('pkg/verible', collection='debian/bullseye', architecture='amd64', default=True, test=True)`
- Exit status: `CalledProcessError` (docker build exit 1), wrapped as SystemExit path -> FAIL
- Result: **FAIL**
- RAW docker command: `docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/pkg/verible --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target pkg -f debian/verible.dockerfile debian`

### Symptoms / error lines

- `curl: (22) The requested URL returned error: 404`
- `gpg: no valid OpenPGP data found.`
- `<ERROR [build 2/3] ... did not complete successfully: exit code: 2`
- The failing RUN is `debian/verible.dockerfile:29-35` (the Bazel apt-repo bootstrap RUN).

## verible

- Call: `BuildImage('verible', collection='debian/bullseye', architecture='amd64', default=True, test=True)`
- Exit status: `CalledProcessError` (docker build exit 1), wrapped as SystemExit path -> FAIL
- Result: **FAIL**
- RAW docker command: `docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 -t ghcr.io/hdl/amd64/debian/bullseye/verible --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye -f debian/verible.dockerfile debian`

### Symptoms / error lines

- Identical to `pkg/verible`; same `[build 2/3]` RUN, same `curl: (22) ... 404`, `gpg: no valid OpenPGP data found.`.

## Root-cause hypothesis: recipe-vs-env

**Recipe staleness (upstream drift), not test, not deps, not env.**

The failure is at `debian/verible.dockerfile:31`:

```
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > /usr/share/keyrings/bazel-archive-keyring.gpg
```

`https://bazel.build/bazel-release.pub.gpg` now returns HTTP 404 (reproduced both from this host and inside the build; also tracked upstream as bazelbuild/bazel#23492). Bazel moved the apt signing key to `https://releases.bazel.build/bazel-release.pub.gpg`, which returns 200 (verified from this host). The current official docs (`site/en/install/ubuntu.md`) use the `releases.bazel.build` URL.

### Env facts

- Build base `ghcr.io/hdl/amd64/debian/bullseye/build/build:latest@sha256:2efef5e6...` resolves and is CACHED.
- apt pulls from `snapshot.debian.org` (`20260824T000000Z`) succeed — no Debian mirror drift.
- Host curl of the recipe's URL: `404`; host curl of `https://releases.bazel.build/bazel-release.pub.gpg`: `200`. Network is fine; the URL itself is dead.

### Why "recipe" and not deps/env/test

- Fails in the very first recipe step of the build stage before any verible source interaction — cannot be a test issue (tests never ran) nor a build-time dependency of verible itself.
- `apt-get`/`gpg`/`curl` install and run fine inside the EOL-bullseye snapshot environment; the only failing external is the hard-coded Bazel key URL, which is a recipe constant, not an environment artifact.

### Investigation notes

- `git log -- debian/verible.dockerfile` shows the recipe came in via `1fbcf50 debian: use same recipes`; the stale `bazel.build/...pub.gpg` URL was already upstream-fixed in Bazel docs previously.
- Both `target pkg` and the runtime target share the identical `build` stage, so both images fail at the exact same instruction — single root cause.

### Recommended next step

Change `debian/verible.dockerfile:31` from

```
https://bazel.build/bazel-release.pub.gpg
```

to

```
https://releases.bazel.build/bazel-release.pub.gpg
```

then re-run the audit. Expect both `pkg/verible` and `verible` to build; the `bazel run -c opt //:install` step and the runtime tests (`verible.sh`) are then the next potential failure points (unrelated to this fix).