# Audit: `impl-build` on `debian/bullseye` (amd64)

- **Task**: `impl-build`
- **Images**: `build/impl`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev` (`8761c15` "AGENTS.md: document _anchors as loader-only config scaffolding")
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=False)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script; `job_images('impl-build')` → `['build/impl']`)
- **Log**: `audits/logs/impl-build.log`

## Overall result: FAIL

The single image `build/impl` fails during the `apt-get install` step (stage `base` 4/4 in `debian-bullseye/impl.dockerfile:37`). The base image (`ghdl/yosys`) carries `/etc/apt/sources.list` pointing at the live `deb.debian.org` mirrors — not the `snapshot.debian.org` fix applied by `debian-bullseye/base.dockerfile:30`. With bullseye EOL (2026-08-31) now ~2 weeks past, the security-pool .deb files have been drained from `deb.debian.org` while the Packages index still advertises them, yielding deterministic 404 errors on upgrade packages.

---

## `build/impl` — FAIL

### BuildImage call

```
BuildImage('build/impl', collection='debian/bullseye', architecture='amd64', default=True, test=False)
```

Effective command (from pyHDLC `_exec`, `debian-bullseye/impl.dockerfile`, target `base`):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/build/impl \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye --target base \
  -f debian-bullseye/impl.dockerfile debian-bullseye
```

### Exit status

`CalledProcessError` from `docker build` (rc=1). Raised at `utils/pyHDLC/__init__.py:456` → `_exec` → `subprocess.check_call` (run.py:46).

### Pass/Fail

FAIL.

### Symptoms / error lines

Build fails at stage `base` 4/4, step `impl.dockerfile:37`:

```dockerfile
RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    libboost-all-dev \
    libomp5-11 \
    make \
 && apt-get autoclean && apt-get clean && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists
```

`apt-get update` succeeds (Packages index is still served), but `apt-get install` fails with 404 errors when fetching pool .deb files from `deb.debian.org` for security-track upgrades (log lines 197–386):

```
Err:2 http://deb.debian.org/debian-security bullseye-security/main amd64 libpython3.9-stdlib amd64 3.9.2-1+deb11u7
  404  Not Found [IP: 151.101.194.132 80]
Err:4 http://deb.debian.org/debian-security bullseye-security/main amd64 libpython3.9-minimal amd64 3.9.2-1+deb11u7
  404  Not Found [IP: 151.101.194.132 80]
Err:5 http://deb.debian.org/debian-security bullseye-security/main amd64 libexpat1 amd64 2.2.10-2+deb11u7
  404  Not Found [IP: 151.101.194.132 80]
Err:26 http://deb.debian.org/debian-security bullseye-security/main amd64 libicu67 amd64 67.1-7+deb11u1
  404  Not Found [IP: 151.101.194.132 80]
Err:27 http://deb.debian.org/debian-security bullseye-security/main amd64 icu-devtools amd64 67.1-7+deb11u1
  404  Not Found [IP: 151.101.194.132 80]
Err:81 http://deb.debian.org/debian-security bullseye-security/main amd64 libxnvctrl0 amd64 535.309.01-0+deb11u1
  404  Not Found [IP: 151.101.194.132 80]
Err:133 http://deb.debian.org/debian-security bullseye-security/main amd64 libpython3.9 amd64 3.9.2-1+deb11u7
  404  Not Found [IP: 151.101.194.132 80]
Err:134 http://deb.debian.org/debian-security bullseye-security/main amd64 libexpat1-dev amd64 2.2.10-2+deb11u7
  404  Not Found [IP: 151.101.194.132 80]
Err:135 http://deb.debian.org/debian-security bullseye-security/main amd64 libpython3.9-dev amd64 3.9.2-1+deb11u7
  404  Not Found [IP: 151.101.194.132 80]

E: Unable to fetch some archives, maybe run apt-get update or try with --fix-missing?
```

Nine 404 errors; exit code 100.

### Env facts

- **Date**: 2026-09-15; bullseye EOL: 2026-08-31 (~2 weeks post-EOL).
- **Base image**: `ghcr.io/hdl/amd64/debian/bullseye/ghdl/yosys:latest@sha256:a1e59fb42f352341957816cb6b4f3694e3985d71f59562bda01c590434d0f414`. Pulled/extracted fine (step `base` 1/4). The failure is inside the `RUN` step inside this image, not in resolving or fetching the base layer.
- **Other dependencies resolved OK**: `ghcr.io/hdl/amd64/debian/bullseye/pkg/yosys:latest@sha256:b1df229...` and `ghcr.io/hdl/amd64/debian/bullseye/pkg/ghdl-yosys-plugin:latest@sha256:9a26c6e...` both resolve and extract fine.
- **APT sources in base image**: `deb.debian.org` (live mirror) — confirmed by the `Get:1 http://deb.debian.org/debian-security` URLs in the log output. The `debian-bullseye/base.dockerfile:30` sed fix (`deb [check-valid-until=no]` → snapshot.debian.org) is applied only at `build/base` level; the published `ghdl/yosys:latest` image was built before this fix was present, so its inherited `/etc/apt/sources.list` still points at the draining live mirrors.
- **Failing packages**: 6 upgraded + 9 new installs are security-track `.deb` files (`+deb11u7`, `+deb11u1`) whose pool entries have been drained from `deb.debian.org`. The Packages index still advertises them (apt update succeeded), but the .deb files themselves are gone → deterministic 404s.
- **Wiring**: `jobs.yml:159-162` — `impl-build: { images: [build/impl], sys: *SysDebianLegacyAmd64 }`; `images.yml:67` — `build/impl: { <<: *ImplDockerfile, target: base }`.
- **Target `base`**: The `--target base` flag means only the first stage (`base`) of `debian-bullseye/impl.dockerfile` is built. The downstream targets (`ice40`, `ecp5`, `nexus`, `generic`, `pnr`) are never reached.

### Root-cause hypothesis

**Environment (EOL apt sources in base image) — not recipe logic, not test, not build-deps**

The root cause is the well-documented EOL Debian "pool drain" issue (AGENTS.md): `debian-bullseye/base.dockerfile:30` fixes this by switching `/etc/apt/sources.list` to `snapshot.debian.org` with `[check-valid-until=no]`, but the **published `ghdl/yosys:latest` image** (the `base` stage of `impl.dockerfile`) was built before this fix existed. Its apt sources still point at `deb.debian.org`, which post-EOL drains pool .debs while keeping the Packages index live. The `impl.dockerfile:37` `RUN apt-get install` then fails deterministically with 404s.

This is identical to every other EOL-bullseye `apt-get install` failure seen in this audit batch (verilator, vtr, openroad, etc.) — they all inherit the pre-fix `ghdl/yosys` or similar bullseye base images.

### Investigation notes

- `job_images('impl-build')` → `['build/impl']`; single image, single attempt, fails.
- The build command resolves correctly (Dockerfile: `debian-bullseye/impl.dockerfile`, target: `base`, context: `debian-bullseye`).
- Steps `base` 1/3 (`COPY --from=pkg-ghdl-yosys-plugin`), `base` 2/3 (`COPY --from=pkg-yosys`) both succeed. Only the final `apt-get install` step (4/4) fails.
- The `apt-get update -qq` itself succeeds (exit 0, no errors) — the Packages index is still served by the live mirror. The failure is in *fetching* the .deb files referenced by that index.
- Version stage never executes (build fails before it); no `dist/hdlc.<image>.version` produced.
- This is a build-only task (`test=False`); no test script exists for `build/impl` (confirmed per AGENTS.md).
- Similar pre-existing pattern: `debian-bullseye/base.dockerfile:30` already contains the `sed` fix and has been used for other bullseye images successfully. The issue is specifically that the `ghdl/yosys` image in the registry predates the fix.
- The `sys: *SysDebianLegacyAmd64` wiring is correct; `impl-build` builds only for `debian/bullseye` on `amd64` (no bookworm/trixie/other-arch variants).

### Recommended next step

Rebuild the dependency chain `ghdl/yosys` for bullseye-amd64 using the current `debian-bullseye/base.dockerfile` (which contains the EOL snapshot fix), then re-publish `ghcr.io/hdl/amd64/debian/bullseye/ghdl/yosys:latest`. After that, re-run `impl-build` — the inherited `/etc/apt/sources.list` will contain the `snapshot.debian.org` entries and the `apt-get install` step will succeed.

Steps:

1. Verify `ghdl/yosys` is scheduled/rebuildable for bullseye-amd64. Confirm `ghdl` task is in the dispatch window (`needs.dot`); if not, trigger it manually.
2. After `ghdl/yosys` is rebuilt and pushed, re-run this audit:
   ```bash
   ./venv/bin/python -u - < your-heredoc  # with task='impl-build'
   ```
3. Confirm `=== PASS build/impl ===` and `RESULT: PASS` in the log.

No changes to `debian-bullseye/impl.dockerfile` are needed — the recipe is correct. The failure is entirely in the pre-built base image.
