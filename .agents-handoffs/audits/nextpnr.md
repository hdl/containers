# Audit Report: nextpnr (debian/bullseye, amd64)

**Task:** nextpnr
**Images:** `pkg/nextpnr/generic`, `nextpnr/generic`, `nextpnr`
**Date:** 2026-09-15
**Branch:** umarcor/dev
**Collection:** debian/bullseye
**Architecture:** amd64
**Registry:** ghcr.io/hdl
**Log:** audits/logs/nextpnr.log
**Status:** FAIL

---

## Image: pkg/nextpnr/generic

**BuildImage Call:**
```python
BuildImage("pkg/nextpnr/generic", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

**Exit Status:** 1 (CalledProcessError)

**Result:** FAIL

**Symptoms / Error Lines:**
```
#5 [build-generic 2/2] RUN cd /tmp/nextpnr/build  && cmake ..    -DARCH=generic    -DBUILD_GUI=OFF    -DBUILD_PYTHON=ON    -DUSE_OPENMP=ON  && make -j $(nproc)  && make DESTDIR=/opt/nextpnr install
#5 0.208 CMake Error at CMakeLists.txt:5 (cmake_minimum_required):
#5 0.208   CMake 3.25 or higher is required.  You are running version 3.18.4
#5 0.208 
#5 0.208 
#5 0.209 -- Configuring incomplete, errors occurred!
```

**Environment Facts:**
- Base image: `ghcr.io/hdl/amd64/debian/bullseye/build/nextpnr/build:latest` (sha256:03e2f82c3a05ec22601466bd7d66a84814ff496c75c16a56981994ec8e6eab97)
- Debian bullseye provides CMake 3.18.4 (from `debian:bullseye-slim` base)
- Upstream nextpnr (YosysHQ/nextpnr) now requires CMake ≥ 3.25 (CMakeLists.txt:5)
- The `build-generic` stage is at dockerfile line 149-158

**Root-Cause Hypothesis (recipe vs test vs deps vs env):**
- **RECIPE**: The `debian-bullseye/nextpnr.dockerfile` does not upgrade CMake. The `build` stage (line 40-49) inherits from `$REGISTRY/build/dev` which is based on `debian:bullseye-slim` and only installs `libeigen3-dev` and `libomp-dev`. No CMake backport or manual installation is performed.
- The `build-generic` stage reuses the same `/tmp/nextpnr` source cloned in the `build` stage, so it picks up the updated CMakeLists.txt requirement.
- Architecture-specific builds (ice40, ecp5, nexus) may have succeeded earlier when nextpnr's CMake requirement was lower, and their layers are cached in the registry. The `generic` target is now failing because it triggers a fresh build with the new CMake requirement.

**Investigation Notes:**
- The `nextpnr-prjs` task (which builds `pkg/nextpnr/ice40`, `nextpnr/ice40`, etc.) is separate and its images are published in the registry (log shows they are pulled successfully at lines 159-190).
- The `nextpnr-build` task builds `build/nextpnr/base` and `build/nextpnr/build` — these succeed because they don't run cmake.
- Only the `generic` architecture build (and thus `pkg/nextpnr/generic`, `nextpnr/generic`, `nextpnr`) fails because it's the only one that re-runs cmake on the current upstream source.
- Possible fixes: (1) Install CMake ≥ 3.25 from backports or Kitware APT repo in the `build` stage; (2) Pin nextpnr to an older commit that works with CMake 3.18.4 (but repo policy is to track upstream main); (3) Drop bullseye support for nextpnr (since bookworm/trixie have newer CMake).

**Recommended Next Step:**
Add CMake ≥ 3.25 installation to the `build` stage in `debian-bullseye/nextpnr.dockerfile` (e.g., via Kitware APT repository or by building from source), or restrict nextpnr to bookworm/trixie collections in `jobs.yml`.

---

## Image: nextpnr/generic

**BuildImage Call:**
```python
BuildImage("nextpnr/generic", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

**Exit Status:** 1 (CalledProcessError)

**Result:** FAIL

**Symptoms / Error Lines:**
```
#7 [build-generic 2/2] RUN cd /tmp/nextpnr/build  && cmake ..    -DARCH=generic    -DBUILD_GUI=OFF    -DBUILD_PYTHON=ON    -DUSE_OPENMP=ON  && make -j $(nproc)  && make DESTDIR=/opt/nextpnr install
#7 0.170 CMake Error at CMakeLists.txt:5 (cmake_minimum_required):
#7 0.170   CMake 3.25 or higher is required.  You are running version 3.18.4
```

**Environment Facts:**
- Same as `pkg/nextpnr/generic` — the `build-generic` stage is shared.
- Depends on `build/nextpnr/build` and `build/nextpnr/base` (both cached).

**Root-Cause Hypothesis:** Identical to `pkg/nextpnr/generic`.

**Investigation Notes:** Same failure in the `build-generic` stage. The runtime image `nextpnr/generic` includes the `generic` target which depends on `build-generic`.

**Recommended Next Step:** Same as above.

---

## Image: nextpnr

**BuildImage Call:**
```python
BuildImage("nextpnr", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

**Exit Status:** 1 (CalledProcessError)

**Result:** FAIL

**Symptoms / Error Lines:**
```
#13 [build-generic 2/2] RUN cd /tmp/nextpnr/build  && cmake ..    -DARCH=generic    -DBUILD_GUI=OFF    -DBUILD_PYTHON=ON    -DUSE_OPENMP=ON  && make -j $(nproc)  && make DESTDIR=/opt/nextpnr install
#13 0.163 CMake Error at CMakeLists.txt:5 (cmake_minimum_required):
#13 0.163   CMake 3.25 or higher is required.  You are running version 3.18.4
```

**Environment Facts:**
- The `nextpnr` image (final combined image) includes the `build-generic` stage (line 177-181 in dockerfile) to copy the generic architecture build.
- Also pulls `pkg/nextpnr/ice40`, `pkg/nextpnr/ecp5`, `pkg/nextpnr/nexus` from registry (successfully, per log lines 159-190).
- Fails at the same `build-generic` cmake step.

**Root-Cause Hypothesis:** Identical — the final image build triggers the `build-generic` stage which requires CMake 3.25+.

**Investigation Notes:** The combined `nextpnr` image is the only one that aggregates all architectures. It fails because it must build the `generic` variant locally (not available as a pre-built pkg image in the registry for bullseye).

**Recommended Next Step:** Same as above. Fixing the `build` stage CMake version will unblock all three images.