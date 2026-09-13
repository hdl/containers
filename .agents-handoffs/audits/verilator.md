# Audit: `verilator` on `debian/bullseye` (amd64)

- **Task**: `verilator`
- **Images**: `pkg/verilator`, `verilator`
- **Date**: 2026-09-15
- **Branch**: `umarcor/dev`
- **Collection**: `debian/bullseye`
- **Architecture**: `amd64`
- **Registry**: `ghcr.io/hdl`
- **Method**: `BuildImage(img, collection='debian/bullseye', architecture='amd64', default=True, test=True)` via the pyHDLC Python API (`venv/bin/python`, heredoc audit script)
- **Log**: `audits/logs/verilator.log`
- **Audit runner exit**: 1 (`RESULT: FAIL`)

## Overall result: FAIL

Both images fail during the Docker build step (the `make` compile phase inside `verilator.dockerfile` `RUN git clone ...`). Tests never run.

Matrix as returned by `job_images('verilator')` → `['pkg/verilator', 'verilator']`.

---

## `pkg/verilator` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 5):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/pkg/verilator \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  --target pkg -f debian/verilator.dockerfile debian
```

Exit status: 1 (`CalledProcessError` from `docker build`); the in-image step itself failed with exit code 2. Logged as `=== FAIL pkg/verilator ... ===`.

Symptoms / error lines (Dockerfile:39, `[build 3/3]`):

```
#6 425.9 ../V3ClassGraph.h:43:5: warning: explicitly defaulted default constructor is implicitly deleted [-Wdefaulted-function-deleted]
#6 425.9     V3ClassGraph() = default;
#6 425.9 ../V3ClassGraph.h:41:9: note: default constructor of 'V3ClassGraph' is implicitly deleted because field 'm_emptySet' of const-qualified type 'const std::unordered_set<AstCFunc *>' would not be initialized
#6 425.9         m_emptySet;  // Always empty set - used to return a reference to an empty set
#6 426.4 ../V3ClassGraph.cpp:196:24: error: call to implicitly-deleted default constructor of 'V3ClassGraph'
#6 426.4         : m_graphp{new V3ClassGraph} {
#6 443.5 1 warning and 1 error generated.
#6 443.6 make[2]: *** [../Makefile_obj:446: V3ClassGraph.o] Error 1
#6 446.2 make: *** [Makefile:151: verilator_exe] Error 2
#6 ERROR: process "/bin/bash -c git clone https://github.com/verilator/verilator ..." did not complete successfully: exit code: 2
```

Preceding stages were healthy:
- `apt-get install` of `autoconf`, `bison`, `flex`, `help2man`, `libfl-dev` — all fetched successfully from `snapshot.debian.org` (`20260824T000000Z` bullseye pin, `[check-valid-until=no]`), no apt 404s.
- `git clone https://github.com/verilator/verilator` — completed successfully (version `v5.052-86-g253f51f1d`).
- `autoconf` + `./configure` — completed successfully (clang++ 11.0.1-2 detected, C++17 mode, no z3/cvc5).
- `make` — failed compiling `V3ClassGraph.cpp` (both `obj_dbg` and `obj_opt` targets).

---

## `verilator` — FAIL

Exact `docker build` as resolved by `BuildImage` (log line 543):

```
docker build --progress=plain --build-arg BUILDKIT_INLINE_CACHE=1 --platform linux/amd64 \
  -t ghcr.io/hdl/amd64/debian/bullseye/verilator \
  --build-arg REGISTRY=ghcr.io/hdl/amd64/debian/bullseye \
  -f debian/verilator.dockerfile debian
```

Exit status: 1 (`CalledProcessError`); in-image step exit code 2. Logged as `=== FAIL verilator ... ===`.

Same root cause and identical error lines as `pkg/verilator`. The runtime deps install stage (`clang`, `make`, `perl`) was never reached because the shared `build` stage failed.

---

## Root-cause hypothesis

**Recipe/upstream drift** (unpinned `git clone` of verilator `master`), not test, not deps, not env.

The verilator Dockerfile (`debian/verilator.dockerfile:39-47`) clones `https://github.com/verilator/verilator` without a tag/commit pin. The repo's design intentionally tracks upstream `master` to catch breakage early (AGENTS.md: "Unpinned git clone in HDLC recipes is intentional ... This catches breakage early").

A recent upstream commit added `V3ClassGraph.h` containing:

```cpp
// line 41
const std::unordered_set<AstCFunc *> m_emptySet;  // Always empty set - used to return a reference to an empty set
// line 43
V3ClassGraph() = default;
```

In C++17 (which verilator uses, per `--std=gnu++17`), a defaulted default constructor is **defined as deleted** when the class has a non-static data member of const-qualified type without a default member initializer ([class.ctor.default]/5). **Clang 11 on bullseye correctly implements this rule** and rejects the code. GCC historically was more lenient about this, so the code may compile on GCC but not on clang 11.

The configure output confirms: `compiler CXX inbound is set to... clang++`, `gcc = clang`. The Dockerfile sets `CC=clang` for the build base, and the vcddiff sub-build also uses `CC=$CC = clang`.

Verilator `v5.052` (latest release tag) or slightly older commits likely compiled fine; the breakage is from the post-5.052 development branch (`v5.052-86-g253f51f1d`).

### Env facts

- Base image `ghcr.io/hdl/amd64/debian/bullseye/build/build:latest@sha256:2efef5e6...` resolved fine.
- Network, apt (`snapshot.debian.org`), and `git clone` all healthy — no EOL-mirror or network issues.
- Compiler: **Debian clang 11.0.1-2** (bullseye's system clang). The upstream verilator CI likely tests with newer clang (14+) where this either compiles (if the C++20 relaxed rules are in play) or where the const-member issue was fixed upstream.

---

## Investigation notes

- `V3ClassGraph.cpp:196` tries `new V3ClassGraph` which requires calling the default constructor. The defaulted default constructor is deleted because `m_emptySet` is `const`-qualified without a default member initializer. This is a hard error, not a warning (the warning was emitted first, then the error at the call site).
- This is a **known class of C++17 conformance issue** — clang 11 is strict, GCC may accept it as an extension.
- The fix is **upstream's responsibility**: either remove `const` from `m_emptySet`, provide a default member initializer (`= {}`), or switch to a `static` member. The verilator project may have already fixed this on their `master` branch or it may need a vendored patch.
- Tests never ran for either image; `test/verilator.sh` was never reached.

## Recommended next step

1. **Short-term**: Pin the `git clone` to a known-good verilator commit/tag (e.g., `v5.052` release) in `debian/verilator.dockerfile`, OR apply a small patch in the Dockerfile to fix `V3ClassGraph.h` (e.g., change `const std::unordered_set<AstCFunc *> m_emptySet;` to `static const std::unordered_set<AstCFunc *> m_emptySet;` or add `= {}` initializer).
2. **Long-term**: Monitor upstream for a fix to the `const` member issue and revert to unpinned `master` once the verilator project addresses the clang 11 incompatibility.
3. Re-run the same audit command after the fix. Both images must reach their `=== PASS ... ===` markers, which would also exercise `test/verilator.sh` for the first time in this audit run.
