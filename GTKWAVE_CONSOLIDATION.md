# GTKWAVE CONSOLIDATION

> Handover for the `debian/gtkwave` recipe. Complements `CONSOLIDATION.md` and
> `AGENTS.md`. This file is a living document for the gtkwave work; keep it in sync
> when the recipe or the collection wiring changes.

## Current state

Upstream `github.com/gtkwave/gtkwave` maintains two divergent branches (`master` and
`lts`) with different build systems. The **lts lane is merged into `main`** of this
codebase (`8e35c80`, recipe `debian/gtkwave/HDLC` = `0c840e7`): `git clone -b lts`,
a `config.guess`/`config.sub` refresh from automake (riscv64), the `--with-tk` flag
dropped, and the `jobs.yml` anchor widened to `*SysDebianDefaultArchSet`. It was
verified on bullseye/bookworm/trixie amd64 (`dist/hdlc.gtkwave.version`
= `v3.3.116-g012758d`); riscv64 is fixed, and arm64v8/ppc64le/s390x remain flaky
under qemu emulation (environmental, not a gtkwave defect).

The **master lane (meson) is the pending work** documented below. It is not yet on
`main`.

## Upstream divergence: `master` vs `lts`

- **`master`**: moved to **meson** in 2023-08. The `gtkwave3-gtk3/` autotools tree was
  deleted; Tcl/Tk and GTK2 support were dropped. Project `gtkwave`, version
  `4.0.0-prealpha`, `meson_version: >= 1.0.0`. Source layout moved to the repo root
  (`src/`, `lib/`, `contrib/`, `libwcp/`, ...); `libfst` is fetched at `meson setup`
  time through the vendored wrap `subprojects/libfst.wrap` (network + git required in
  the build container).
- **`lts`**: the 3.3.x line, still **autotools**. Keeps `gtkwave3-gtk3/`,
  `autogen.sh` and `--enable-gtk3`; GTK2/GTK3 and the Tcl/Tk subsystem are preserved.
  Current HEAD is `012758d`, version `3.3.129` (`AC_INIT(gtkwave-gtk3, 3.3.129, ...)`
  in `gtkwave3-gtk3/configure.ac`).

## Root cause of the break

The unified recipe `debian/gtkwave/HDLC` does `cd /tmp/gtkwave/gtkwave3-gtk3` after
`git clone ... git.git`. On upstream `master` that directory no longer exists, so
`./autogen.sh` fails. The recipe followed the LTS-era build flow (autotools + gtk3),
which is only available on the `lts` branch; and beyond `gtkwave3-gtk3/`, there is
no `autogen.sh`/`configure` anymore on `master` and no Tcl configure knob. Each lane
therefore needs its own recipe.

## Target topology (pending split)

On `main`, the single `gtkwave` image is meant to become two images:

- **`gtkwave`** — the master lane (meson), replacing the lts recipe at
  `debian/gtkwave/`.
- **`gtkwave/lts`** — the lts lane (autotools, currently at `debian/gtkwave/`),
  moving to its own recipe dir (e.g. `debian/gtkwave-lts/`, with
  `images.yml: gtkwave/lts: { dockerfile: gtkwave-lts }`, mirroring how `ghdl/yosys`
  maps to `dockerfile: ghdl-yosys-plugin`), plus its own `jobs.yml` anchor.

## Build system / deps side-by-side

| aspect | master (meson `4.0.0-prealpha`) | lts (autotools `3.3.129`) |
|---|---|---|
| build system | `meson setup/compile/test/install` | `autogen.sh` + `configure` + `make` |
| GUI toolkit | GTK3 for `gtkwave`/`twinwave`; `contrib/rtlbrowse` requires GTK4 (>= 4.6) | GTK3, no GTK4 |
| script language | none | Tcl/Tk |
| key libs | glib-2.0 >= 2.72, gtk+-3.0 >= 3.24, gtk4 >= 4.6, json-glib >= 1.6.6 (libwcp), zlib >= 1.2.0, libfst (meson wrap), Judy (auto feature) | GTK3 + inline/older deps |
| source layout | repo root (`src/`, `contrib/`, `libwcp/`, `subprojects/`) | `gtkwave3-gtk3/` |
| helper binaries | `vcd2fst`, `fst2vcd`, `lxt2vcd`, `evcd2vcd`, `vzt2vcd`, `vztminer`, `fstminer`, `lxt2miner`, `xml2stems`, ... | similar set, older |
| install | `meson install` with `DESTDIR`; default prefix `/usr/local` | `make DESTDIR check install` |

## `master` lane: adaptation and verification

### Adaptation (recipe rewrite, `debian/gtkwave/HDLC`)

- `makedepends` supplies the meson toolchain and meson deps: `build-essential meson
  ninja-build gperf flex desktop-file-utils libgtk-3-dev libgtk-4-dev
  libjson-glib-dev zlib1g-dev libbz2-dev libjudy-dev liblzma-dev libgtk-3-bin
  pkg-config`. The autotools/Tcl set was dropped (`automake gawk libreadline-dev
  libffi-dev tcl-dev tk-dev`).
  - `gperf` and `flex` are required at `meson setup` time (`contrib/rtlbrowse`).
  - `desktop-file-utils` (`update-desktop-database`) and `libgtk-3-bin`
    (`gtk-update-icon-cache`) are required at `meson setup` time —
    `gnome.post_install` hardcodes both regardless of `-Dupdate_mime_database` and
    resolves the tool paths during setup (the actual post-install scripts are skipped
    under `DESTDIR` installs).
  - `libjudy-dev` exists on bookworm (`1.0.5-5+b2`); its runtime counterpart is
    `libjudydebian1` (`libJudy.so.1`).
- `build()`:
  ```sh
  git clone https://github.com/gtkwave/gtkwave.git /tmp/gtkwave
  cd /tmp/gtkwave
  versionString=$(sed -n "s/^[[:space:]]*version: *'\([^']*\)',/\1/p" meson.build | head -1)
  git describe --long --tags | sed 's/nightly/'"$versionString"'/;s/[^-]*-g/g/' > /tmp/hdlc.gtkwave.version
  meson setup build -Dintrospection=false -Dupdate_mime_database=false
  meson compile -C build
  meson test -C build
  DESTDIR=/opt/gtkwave meson install -C build
  ```
  - `-Dintrospection=false` avoids gobject-introspection/g-ir tools;
    `-Dupdate_mime_database=false` avoids shared-mime-info. Tests are kept at their
    default (`true`).
  - `meson setup build` fetches `libfst` via the wrap (network + git are available
    in the build image).
  - version extraction: meson.build contains both the project `version:
    '4.0.0-prealpha'` and `meson_version: '>= 1.0.0'`; the anchored regex
    `^[[:space:]]*version: *'` matches only the project line.
- Dockerfile unchanged: `COPY --from=build /opt/gtkwave /` maps
  `/opt/gtkwave/usr/local/...` onto the runtime root, so `/usr/local/bin` and
  `/usr/local/lib` are on the default prefix paths.

### Verification (bookworm, this pass)

- `meson setup build -Dintrospection=false -Dupdate_mime_database=false`: OK (libfst
  wrap fetched).
- `meson compile -C build`: OK.
- `meson test -C build`: OK — **45 tests passed, 0 failed, 0 skipped, 0 timeout**
  (wcp_smoke + libgtkwave tests).
- `DESTDIR=/opt/gtkwave meson install -C build`: OK.
- version file `dist/hdlc.gtkwave.version`:
  ```
  4.0.0-prealpha-g132a086
  ```
- smoke test: `docker run --rm -v .../test://wrk
  ghcr.io/hdl/amd64/debian/bookworm/gtkwave //wrk/gtkwave.sh` → `gtkwave help: exit
  code 0 | OK` + `_todo.sh` no-op → **exit 0**. `gtkwave --help`, `vcd2fst --help`,
  `fst2vcd --help`: exit 0.

### Final runtime `depends` (master)

```sh
depends=(
  graphviz
  libgtk-3-bin
  libgtk-4-1
  libjson-glib-1.0-0
  libjudydebian1
  xdot
)
```

Rationale: `libjudydebian1` (`libJudy.so.1`) and `libjson-glib-1.0-0`
(`libjson-glib-1.0.so.0`) are unconditional `DT_NEEDED` of `gtkwave` (Judy feature
auto-enabled at setup since `libjudy-dev` was installed; json-glib is a libwcp hard
dep); without them `gtkwave` aborts with exit 127. `libgtk-4-1` was added for
`contrib/rtlbrowse` (GTK4 >= 4.6). `graphviz`, `libgtk-3-bin`, `xdot` kept from the
old recipe (GUI/export helpers for the GTK3 app).

### Known limitation: `rtlbrowse` needs `ldconfig` after `COPY`

`gtkwave` is linked with a meson-baked RUNPATH pointing at
`/usr/local/lib/x86_64-linux-gnu`, so it finds the wrapped `libfst.so.1`.
`rtlbrowse` (contrib, GTK4) is built without a RUNPATH, so it relies on the loader
cache — which is generated during the `apt-get` RUN layer, i.e. *before*
`COPY --from=build /opt/gtkwave /` adds the libs. Result: `rtlbrowse --help` still
exits 127 (`libfst.so.1 => not found`). Fixing it would require an `ldconfig` after
the `COPY`, i.e. a Dockerfile change — out of scope by design. The primary image
(`gtkwave`) is unaffected.

## `jobs.yml` status

- `gtkwave: *SysDebianDefaultArchSet` — already widened (merged with the lts lane on
  `main`). `pyHDLC jobs gtkwave` yields trixie amd64/arm64v8/ppc64le/s390x/riscv64
  plus the bookworm/bullseye arch sets.
- `magic`/`yosys`/`z3` remain on `*SysDebianLegacy*` anchors until their trixie
  builds are verified (follow-up, not a gtkwave matter).
- Once the lts lane becomes its own image (`gtkwave/lts`), it needs its own anchor;
  the widened `gtkwave` anchor then applies to the master lane image only.

The master lane has not (yet) been exercised on the widened anchor; it is only
verified on bookworm/amd64 (see above).

## Follow-ups

- `master` on **trixie**: the recipe is collection-agnostic (unified `debian/`), so
  it should build once wired into a trixie job; needs a build + `--test` + `dist/`
  verification run.
- `master` on **bullseye**: too old — glib 2.66 < 2.72, json-glib 1.6.2 < 1.6.6,
  gtk4 4.2 < 4.6. Keep bullseye on the lts/autotools recipe.
- **Split the lanes into two images on `main`**: rename the lts lane to
  `gtkwave/lts` (its own recipe dir + `images.yml` mapping + `jobs.yml` anchor, as
  per "Target topology"), keep `gtkwave` = master. This is the pending step this
  document prepares; do not lose these notes when it happens.

## Tooling quirk: pyHDLC `--test` may abort cosmetically

`TestImage` (`utils/pyHDLC/__init__.py` ~L558) runs a `docker inspect` before the
actual `docker run`. On a Docker daemon using the containerd snapshotter, `inspect`
omits `.Variant` for amd64 and the Go text/template fails (`map has no entry for key
"Variant"`), so the CLI reports a non-zero exit even though the build succeeded. This
is a **tooling quirk, not a recipe issue** — do not patch pyHDLC for it. Verify the
smoke test by running the underlying command directly:

```sh
docker run --rm -v <repo>/test://wrk ghcr.io/hdl/amd64/debian/bookworm/gtkwave //wrk/gtkwave.sh
```