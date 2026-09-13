# Audit: conda/f4pga/xc7/toolchain

| Field | Value |
|---|---|
| **Task** | `conda/f4pga/xc7/toolchain` |
| **Images** | `conda/f4pga/xc7/toolchain` |
| **Date** | 2026-09-15 |
| **Branch** | `umarcor/dev` |
| **Collection** | `debian/bullseye` |
| **Architecture** | `amd64` |
| **Registry** | `ghcr.io/hdl` |
| **Result** | **FAIL** |

---

## Image: `conda/f4pga/xc7/toolchain`

**BuildImage call:**
```python
BuildImage("conda/f4pga/xc7/toolchain", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

**Dockerfile:** `debian-bullseye/f4pga/Dockerfile`, target `xc7-toolchain` (line 27-28)

**Build command issued:**
```
docker build ... --target xc7-toolchain debian-bullseye/f4pga
```

**Exit status:** Non-zero (CalledProcessError from `docker build`)

**Result:** FAIL

### Symptoms / Error lines

```
#6 [xc7-toolchain 2/2] RUN --mount=type=bind,target=/tmp/ctx . /tmp/ctx/HDLC && env-and-toolchain xc7
#6 7.286 CondaToSNonInteractiveError: Terms of Service have not been accepted for the following channels. Please accept or remove them before proceeding:
#6 7.286     - https://repo.anaconda.com/pkgs/main
#6 7.286     - https://repo.anaconda.com/pkgs/r
#6 7.286
#6 7.286 To accept these channels' Terms of Service, run the following commands:
#6 7.286     conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
#6 7.286     conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
#6 ERROR: process "/bin/bash -c . /tmp/ctx/HDLC && env-and-toolchain xc7" did not complete successfully: exit code: 1
```

### Env facts

- Base image `conda:latest` was freshly built from `debian-bullseye/conda.dockerfile` using `Miniconda3-latest-Linux-x86_64.sh` (passed, conda PASS audit).
- Installed conda version: **26.7.1** (live-inspected from the built image).
- `.condarc` ships with `channels: [defaults]` (confirmed via `conda config --show channels`).
- The `xc7_environment.yml` (delivered inside the `symbiflow-install-xc7-latest` package from f4pga-arch-defs) lists `defaults` as a channel — this maps to `pkgs/main` and `pkgs/r`.
- `conda-anaconda-tos` plugin (bundled with conda ≥25.5.0, activated by default from conda ≥26.x) enforces ToS acceptance for `defaults` channels before `conda env create` proceeds.
- The `HDLC` script (`debian-bullseye/f4pga/HDLC:32-48`) calls `conda env create -f ...` at line 42 without prior ToS acceptance.
- No `CI=true` or `CONDA_PLUGINS_AUTO_ACCEPT_TOS` is set in the Docker build environment, so the plugin does not auto-accept.

### Root-cause hypothesis

**Recipe + environment (upstream conda ToS change):**

Anaconda's `conda-anaconda-tos` plugin (effective July 2025, mandatory in conda 26.x) requires explicit or CI-auto-accepted ToS for the `defaults` channels (`pkgs/main`, `pkgs/r`). The Miniconda3-latest installer now ships with conda 26.7.1, which includes this plugin. The `conda` base image (`debian-bullseye/conda.dockerfile`) installs Miniconda3-latest but does not:
1. Accept the ToS before the image is frozen, nor
2. Set `CONDA_PLUGINS_AUTO_ACCEPT_TOS=yes` as an `ENV`.

When `conda env create` runs inside `env-and-toolchain xc7` (in `debian-bullseye/f4pga/HDLC:42`), the plugin checks ToS status, finds it unaccepted, and throws `CondaToSNonInteractiveError` — a fatal error.

This is not a test issue (testing was never reached). It is not a dependency-fetch issue (the `get-arch-defs-package xc7` curl steps completed before the failure). The failure is purely the conda ToS gate blocking `conda env create`.

### Investigation notes

- Confirmed the `conda:latest` image (digest `sha256:59b6dbd...`) was built and passed its own audit on 2026-09-15 with conda 26.7.1.
- The f4pga recipe has no prior workaround for conda ToS; this issue was invisible before conda shipped with the plugin (pre-July 2025).
- The upstream f4pga-arch-defs `xc7_environment.yml` uses the `defaults` channel and is not under this repo's control.

### Recommended next step

**Fix in the recipe (short-term, correct):** In `debian-bullseye/f4pga/HDLC`, accept the ToS before `conda env create`. Insert the following before line 42:

```sh
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

**Alternative fix (simpler, recommended):** Add the `ENV` directive to the base conda image (`debian-bullseye/conda.dockerfile`) so all downstream conda-based images benefit:

```dockerfile
ENV CONDA_PLUGINS_AUTO_ACCEPT_TOS=yes
```

This is the approach recommended by Anaconda for Docker/CI environments and avoids per-recipe workarounds. Since CI=true is not reliably set during `docker build`, the explicit env var is the cleanest path.

A secondary (longer-term) option is to ensure the upstream f4pga-arch-defs environment YAML uses `conda-forge` only and drops the `defaults` channel, eliminating the ToS requirement entirely.
