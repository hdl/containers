# Bullseye audit

Audit of all tools on `debian/bullseye` (`amd64`), built + tested via pyHDLC
(`BuildImage ... test=True`), one task per report in this directory.

Branch: `umarcor/dev`
Registry: `ghcr.io/hdl`
Collection: `debian/bullseye`
Architecture: `amd64`

## Status table

| task | status | report |
|---|---|---|
| base | PASS | — |
| apicula | PASS | — |
| arachne-pnr | PASS | — |
| boolector | PASS | — |
| conda | PASS | — |
| conda/f4pga/xc7/toolchain | FAIL | f4pga-xc7-toolchain.md |
| cosim | PASS | — |
| cvc | FAIL | cvc.md |
| f4pga-eos-s3 | FAIL | f4pga-eos-s3.md |
| f4pga-xc7-devices | PASS | — |
| formal | FAIL | formal.md |
| ghdl | PASS | — |
| ghdl-yosys-plugin | FAIL | ghdl-yosys-plugin.md |
| gnuplot | PASS | — |
| gtkwave | FAIL | gtkwave.md |
| icestorm | PASS | — |
| impl | PASS | — |
| impl-build | FAIL | impl-build.md |
| impl-prjs | PASS | — |
| irsim | PASS | — |
| iverilog | PASS | — |
| klayout | PASS | — |
| magic | PASS | — |
| magic-irsim | PASS | — |
| netgen | PASS | — |
| nextpnr | FAIL | nextpnr.md |
| nextpnr-build | PASS | — |
| nextpnr-prjs | FAIL | nextpnr-prjs.md |
| nvc | PASS | — |
| openfpgaloader | PASS | — |
| openroad | FAIL | openroad.md |
| osvb | FAIL | osvb.md |
| pono | FAIL | pono.md |
| prog | PASS | — |
| prjoxide | PASS | — |
| prjtrellis | PASS | — |
| sim | PASS | — |
| sby | PASS | — |
| superprove | PASS | — |
| verible | FAIL | verible.md |
| verilator | FAIL | verilator.md |
| vtr | FAIL | vtr.md |
| xschem | PASS | — |
| xyce | FAIL | xyce.md |
| yices2 | PASS | — |
| yosys | FAIL | yosys.md |
| z3 | FAIL | z3.md |

## Final tally (47 tasks, debian/bullseye/amd64, branch umarcor/dev):
- 29 PASS — base, all simulators (ghdl, iverilog, nvc, sim, osvb-runtime, cosim, gnuplot), icestorm/prjoxide/prjtrellis chain, impl, impl-prjs, prog, conda, and others
- 18 FAIL — each with a full report in audits/<task>.md plus logs in audits/logs/

## Failure patterns worth knowing:

1. EOL bullseye apt 404s (impl-build, formal) — recipes without the snapshot/archive pinning; impl-build's root cause is actually the stale published ghdl/yosys base predating the snapshot fix
2. Upstream build-system drift (yosys→CMake-only, xyce→CMake, nextpnr/nextpnr-prjs need CMake ≥3.25 vs bullseye's 3.18, vtr missing --recursive submodules, cvc5 configure.sh now requires a build-type arg)
3. Stale URLs/hosts (verible's bazel GPG key 404, openroad's decommissioned boost mirror)
4. Toolchain gaps (z3 needs C++20/clang>11, verilator master breaks under clang 11 C++17, ghdl-yosys-plugin vs GHDL API skew, osvb's VUnit needs Python ≥3.10)
5. Recipe bugs (pono missing wget, gtkwave meson recipe pulling GTK4 which doesn't exist on bullseye)
6. External ToS change (conda 26.x blocks f4pga env creation without ToS acceptance)

## Follow-up: ghdl on all collections (Sep 2026)

- 12 images built + tested PASS via pyHDLC on `amd64`: bullseye/bookworm/trixie ×
  (`ghdl` mcode, `ghdl/llvm`, `pkg/ghdl`, `pkg/ghdl/llvm`).
  - bullseye: GNAT 9.3.0 / `llvm 11.0.1 code generator`; bookworm: GNAT 12.2.0 /
    `llvm 14.0.6 code generator`; trixie: GNAT 14.2.0 / `llvm 19.1.7 code generator`.
  - All images report `GHDL 7.0.0-dev (6.0.0.r512.g858569681) [Dunoon edition]`.
- The `hello.vhdl` smoke (analyze → elaborate → run → `hello from ghdl`) passed on all
  six runtime images.
- Build+test logs for the Sep-2026 cross-collection builds are no longer available
  locally (the local `work/logs/` was deleted); recipe notes (gnat/llvm/libbacktrace,
  `--default-pic`): see `CONSOLIDATION.md`.
