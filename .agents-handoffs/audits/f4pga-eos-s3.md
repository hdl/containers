# Audit report: `conda/f4pga/eos-s3`

## Task & context

- Task: `conda/f4pga/eos-s3` (job key `f4pga-eos-s3` in `utils/pyHDLC/jobs.yml` → single image `conda/f4pga/eos-s3`)
- Images: `ghcr.io/hdl/amd64/debian/bullseye/conda/f4pga/eos-s3`
- Date: 2026-09-15
- Branch: `umarcor/dev`
- Collection: `debian/bullseye`
- Architecture: `amd64`
- Registry (default): `ghcr.io/hdl` (`Defaults.registry`; `Defaults.collection` is `debian/trixie` but this audit forces `debian/bullseye` explicitly)
- Dependency: `conda/f4pga/eos-s3` builds `FROM ghcr.io/hdl/amd64/debian/bullseye/conda:latest` (built above)
- Method: `BuildImage("conda/f4pga/eos-s3", collection="debian/bullseye", architecture="amd64", default=True, test=True)` via venv `/home/umarcor/containers/venv/bin/python`

## Result overview

| Image | BuildImage call | Exit | Status |
|---|---|---|---|
| `conda/f4pga/eos-s3` | `BuildImage("conda/f4pga/eos-s3", "debian/bullseye", "amd64", default=True, test=True)` | non-zero (subprocess `docker build` rc=1) | **FAIL** |

Also relevant: the audit harness itself aborts before any build when invoked with the image name as the task, because `GenerateJobList` and the `job_images()` helper key on **job keys** (`jobs.yml`), not image names. See Investigation.

## Logs

- Harness failure: `audits/logs/f4pga-eos-s3.log`
- Corrected-run failure (job key `f4pga-eos-s3`, full build+test attempt): `audits/logs/f4pga-eos-s3-fixed.log`

---

## `conda/f4pga/eos-s3` — FAIL

### BuildImage call

```
BuildImage("conda/f4pga/eos-s3", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

Effective command (from pyHDLC `_exec`, `debian-bullseye/f4pga` Dockerfile, target `eos-s3`):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/conda/f4pga/eos-s3 \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target eos-s3 debian-bullseye/f4pga
```

### Exit status

`CalledProcessError` from `docker build` (rc=1). Raised at `utils/pyHDLC/__init__.py:456` → `_exec` → `subprocess.check_call` (run.py:46). The test stage was **never reached** (build failed first).

### Pass/Fail

FAIL.

### Symptoms / error lines

Build fails in stage `eos-s3` at `debian-bullseye/f4pga/Dockerfile:77`:

```dockerfile
FROM $REGISTRY/conda AS eos-s3
RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && env-and-toolchain eos-s3
```

Docker RUN output (`eos-s3 2/2`):

```
CondaToSNonInteractiveError: Terms of Service have not been accepted for the following channels. Please accept or remove them before proceeding:
    - https://repo.anaconda.com/pkgs/main
    - https://repo.anaconda.com/pkgs/r

To accept these channels' Terms of Service, run the following commands:
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

```
ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && env-and-toolchain eos-s3" did not complete successfully: exit code: 1
ERROR: failed to build: failed to solve: ... exit code: 1
```

### Env facts

- Base image `ghcr.io/hdl/amd64/debian/bullseye/conda:latest@sha256:59b6dbd411e3...` (layer `#5` CACHED) ships **conda 26.7.1** with:
  - `channels: [defaults]` (→ `repo.anaconda.com/pkgs/main` + `repo.anaconda.com/pkgs/r`)
  - no ToS acceptance recorded
- `debian-bullseye/conda.dockerfile:37` installs unpinned `Miniconda3-latest` from `repo.continuum.io`; `conda clean -afy` but no channel/ToS configuration.
- The failing `RUN` runs non-interactively inside BuildKit with no TTY (`--progress=plain`, no `-t`), so conda refuses to prompt and raises `CondaToSNonInteractiveError`.
- `env-and-toolchain eos-s3` (`debian-bullseye/f4pga/HDLC:42`) executes `conda env create -f /usr/local/eos-s3_env/eos-s3_environment.yml`. The env file (fetched live via `get-arch-defs-package install-ql`, upstream `SymbiFlow/f4pga-arch-defs` release `latest`) declares `channels: [litex-hub]` only, but conda env create always merges the configured default channels (`defaults`) into the solver, which triggers the ToS gate before any package resolution.
- Base conda image/CI lane exists: job `conda` (`runonly`, `*SysDebianLegacyDefaultArchSet`) is scheduled ahead; the `FROM .../conda:latest` digest resolved and was pulled/cached successfully (this is an *environment/upstream* regression in the prebuilt base, not a scheduling gap).

### Root-cause hypothesis

**Deps/upstream (recipe-level), not test**: `conda` 26.x enforces Anaconda "Terms of Service" acceptance for the `defaults` channels and fails hard in non-interactive contexts when no ToS was accepted or channels not removed. The F4PGA eos-s3 recipe relies on the plain Miniconda base (default channels active) and was written/hardened long before this enforcement. The build therefore breaks deterministically regardless of the (functionally correct) f4pga recipe logic. Debug shows the environment.yaml content is fine (`litex-hub` channel only) and always resolves to `defaults` + `litex-hub` in conda 26.

Secondary observation (not hit in this run, would surface after the ToS issue is fixed): the recipe's tool/artifact downloads depend on upstream `f4pga-arch-defs` `latest` release assets that are now namespaced differently (`symbiflow-ql-eos-s3_wlcsp-latest`, all frozen at `20230411-180123` / commit `5e974a8`), so this image is effectively frozen at 2023-era content.

### Investigation notes

- `job_images("conda/f4pga/eos-s3")` raises `pyHDLC.Exception: Unknown job conda/f4pga/eos-s3` from `_generateJobList` (`__init__.py:239`) because `GenerateJobList` resolves **job keys** (`jobs.yml`), not image names (`images.yml`). `conda/f4pga/eos-s3` is a *runonly/custom* job key, but this image is wired under the custom job key `f4pga-eos-s3` (`jobs.yml:233`). So the audit must use task key `f4pga-eos-s3`. (Note `conda/f4pga/xc7` and `conda/f4pga/xc7/toolchain` *do* exist as runonly keys, so only the eos-s3 one is affected.)
- Verified `job_images("f4pga-eos-s3")` → `['conda/f4pga/eos-s3']`; then re-ran the exact same `BuildImage(...)` scaffolding with that key — image build genuinely fails (see log `f4pga-eos-s3-fixed.log`).
- Confirmed conda version in the pulled base image by `docker run` inspection: `conda 26.7.1`, `channels: [defaults]`.
- Downloaded and inspected `symbiflow-install-ql-latest` (env file source): `eos-s3_env/eos-s3_environment.yml` uses `litex-hub` channel; no `defaults` listed explicitly, so the gate comes from the base conda config.

### Recommended next step

Fix the base conda image (likely `debian-bullseye/conda.dockerfile`) for conda ≥26 policy, in one of two ways:

1. **Pin an older Miniconda/conda** (pre-ToS-enforcement, e.g. conda 24.x) — minimal change, keeps `defaults` behavior.
2. **Disable `defaults` and add ToS acceptance / conda-forge**: e.g.
   `conda config --remove channels defaults` + `conda config --add channels conda-forge`, or
   `conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main` (and `/r`) on first run (echo the prompted `Do you accept?` non-interactively, or use `conda config --set tos_acceptance true` if supported).

Then rebuild `conda` (image above) and re-run this audit. If still failing, evaluate pinning `miniconda` version and/or switching the f4pga env to `--override-channels --channel litex-hub`.