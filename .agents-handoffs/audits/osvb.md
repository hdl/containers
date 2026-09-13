# Audit Report: `osvb`

| Field | Value |
|---|---|
| Task | `osvb` |
| Date | 2026-09-15 |
| Branch | `umarcor/dev` |
| Collection | `debian/bullseye` |
| Architecture | `amd64` |
| Registry | `ghcr.io/hdl` |

## Image Results

| Image | BuildImage Call | Exit Status | Result |
|---|---|---|---|
| `pkg/osvb` | `BuildImage('pkg/osvb', collection='debian/bullseye', architecture='amd64', default=True, test=True)` | 1 (CalledProcessError) | **FAIL** |
| `sim/osvb` | `BuildImage('sim/osvb', collection='debian/bullseye', architecture='amd64', default=True, test=True)` | 0 | **PASS** |

---

## pkg/osvb — FAIL

### Symptoms / Error Lines

The build fails in the `build` stage (step 3/3 of the `pkg` target) when running `python3 setup.py bdist_wheel` on the VUnit clone:

```
Traceback (most recent call last):
  File "/tmp/vunit/setup.py", line 22, in <module>
    from vunit.about import version
  File "/tmp/vunit/vunit/__init__.py", line 13, in <module>
    from vunit.ui import VUnit
  File "/tmp/vunit/vunit/ui/__init__.py", line 28, in <module>
    from ..vunit_cli import VUnitCLI
  File "/tmp/vunit/vunit/vunit_cli.py", line 41, in <module>
    from vunit.sim_if.factory import SIMULATOR_FACTORY
  File "/tmp/vunit/vunit/sim_if/factory.py", line 15, in <module>
    from .modelsim import ModelSimInterface
  File "/tmp/vunit/vunit/sim_if/modelsim.py", line 26, in <module>
    class ModelSimInterface(VsimSimulatorMixin, SimulatorInterface):
  File "/tmp/vunit/vunit/sim_if/modelsim.py", line 91, in ModelSimInterface
    def _find_any_ini_file(root: Path) -> Path | None:
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

### Environment Facts

- Debian bullseye ships **Python 3.9.2** (confirmed installed in the build).
- VUnit `master` branch was cloned (`git clone -b master ...`).
- Cocotb `master` cloned and built successfully (wrote `UNKNOWN-0.0.0-py3-none-any.whl`).
- OsvvmLibraries `2022.06` clone was never reached (the chain `&&` aborted at VUnit).

### Root-Cause Hypothesis

**Recipe issue** — upstream breakage. VUnit's `master` branch now uses **PEP 604 union type syntax** (`Path | None`) in `vunit/sim_if/modelsim.py:91`. This syntax is only valid at runtime starting with **Python 3.10**. Debian bullseye ships Python 3.9, which does not support `X | Y` type annotations at runtime (it raises `TypeError`).

The Dockerfile at `debian-bullseye/osvb.dockerfile:44` unconditionally clones VUnit `master`:
```
git clone -b master --recurse-submodules https://github.com/VUnit/vunit /tmp/vunit
```

VUnit's `master` branch dropped Python 3.9 compatibility, making this clone incompatible with bullseye's Python runtime.

### Investigation Notes

- The `sim/osvb` image **PASS**ed because it pulls a pre-existing `pkg/osvb` image from the registry (line 58: `FROM $REGISTRY/pkg/osvb AS pkg-osvb`). That cached image was built before VUnit's upstream breaking change.
- This confirms the breakage is in the **recipe's unpinned upstream clone**, not in the runtime/test layer.
- The same Dockerfile would fail on any fresh `pkg` build on bullseye; it only passes `sim` today because the registry still holds the old `pkg/osvb` artifact.

### Recommended Next Step

Pin the VUnit clone to the last tag/commit that supports Python 3.9. For example, change:
```
git clone -b master --recurse-submodules https://github.com/VUnit/vunit /tmp/vunit
```
to:
```
git clone -b <last-py3.9-compatible-tag> --recurse-submodules https://github.com/VUnit/vunit /tmp/vunit
```
Alternatively, if the intent is to continuously track `master`, the bullseye recipe may need to be retired (EOL 2026-08-31) in favor of bookworm/trixie which ship Python 3.11+/3.12+.
