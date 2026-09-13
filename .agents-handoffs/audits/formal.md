# Audit Report: `formal`

| Field | Value |
|---|---|
| **Task** | `formal` |
| **Date** | 2026-09-15 |
| **Branch** | `umarcor/dev` |
| **Collection** | `debian/bullseye` |
| **Architecture** | `amd64` |
| **Registry** | `ghcr.io/hdl` |
| **Dockerfile** | `debian-bullseye/formal.dockerfile` |

## Images

| Image | Status |
|---|---|
| `formal/min` | **FAIL** |
| `formal` | **FAIL** |
| `formal/all` | **FAIL** |

---

## `formal/min`

**BuildImage call:**
```python
BuildImage("formal/min", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

**Exit status:** non-zero (CalledProcessError from `docker build`)

**Result:** **FAIL**

### Error lines

```
Err:4 http://deb.debian.org/debian-security bullseye-security/main amd64 python3-pkg-resources all 52.0.0-4+deb11u2
  404  Not Found [IP: 151.101.130.132 80]
Err:5 http://deb.debian.org/debian-security bullseye-security/main amd64 python3-setuptools all 52.0.0-4+deb11u2
  404  Not Found [IP: 151.101.130.132 80]
Err:7 http://deb.debian.org/debian-security bullseye-security/main amd64 python3-pip all 20.3.4-4+deb11u2
  404  Not Found [IP: 151.101.130.132 80]
E: Failed to fetch .../python3-pkg-resources_52.0.0-4+deb11u2_all.deb  404  Not Found
E: Failed to fetch .../python3-setuptools_52.0.0-4+deb11u2_all.deb  404  Not Found
E: Failed to fetch .../python3-pip_20.3.4-4+deb11u2_all.deb  404  Not Found
```

**Failing Dockerfile line:** `formal.dockerfile:36` (the `min` stage `RUN apt-get ... install python3 python3-pip`)

### Investigation

- **Root cause:** **EOL apt pool drainage** — Debian bullseye went EOL 2026-08-31. The `debian-security` mirrors (`deb.debian.org/debian-security`) have drained old pool `.debs` while the Packages index still references them, causing deterministic 404s.
- This is the exact scenario documented in `AGENTS.md` under "EOL Debian releases don't self-heal".
- The base image `ghdl/yosys` is bullseye-based; the `min` stage runs `apt-get update -qq && apt-get install python3 python3-pip` using the stock `debian:*-slim` sources that point at `deb.debian.org`, not `archive.debian.org`.
- **No snapshot pinning** exists in this Dockerfile's `RUN` layer — unlike `debian-bullseye/base.dockerfile` which flips `/etc/apt/sources.list` to `snapshot.debian.org` and adds `[check-valid-until=no]`.

### Recommended next step

Patch `debian-bullseye/formal.dockerfile` (line 36) to prepend apt source manipulation before `apt-get install`:
```dockerfile
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list \
 && sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list \
 && sed -i '/stretch-updates/d' /etc/apt/sources.list \
 && sed -i 's/Check-Valid-Until "yes"/Check-Valid-Until "no"/g' /etc/apt/sources.list \
 && apt-get update -qq \
 && ...
```
Or switch to `snapshot.debian.org` per source. Either pattern unblocks the build.

---

## `formal`

**BuildImage call:**
```python
BuildImage("formal", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

**Exit status:** non-zero (CalledProcessError from `docker build`)

**Result:** **FAIL**

### Error lines

Identical to `formal/min` — same 404s on `python3-pkg-resources`, `python3-setuptools`, `python3-pip` from `debian-security`. Fails at `formal.dockerfile:36` (the `min` stage, which `latest` inherits from).

### Investigation

- The `latest` target depends on the `min` stage. Since `min` fails to build, `latest` cannot proceed.
- The `RUN` at line 59 (`libgmpxx4ldbl`) would also likely fail for the same EOL reason once the earlier step is fixed.

### Recommended next step

Same fix as `formal/min` — patch the apt sources in the `min` stage. Then also verify that `libgmpxx4ldbl` (line 59) is resolvable post-fix.

---

## `formal/all`

**BuildImage call:**
```python
BuildImage("formal/all", collection="debian/bullseye", architecture="amd64", default=True, test=True)
```

**Exit status:** non-zero (CalledProcessError from `docker build`)

**Result:** **FAIL**

### Error lines

Identical to `formal/min` — same 404s at `formal.dockerfile:36` (the `min` stage).

### Investigation

- `formal/all` is the full (default) target — it inherits from `latest`, which inherits from `min`. The `min` stage failure cascades.
- Once the `min` stage is fixed, the `python` / `libpython2.7` install at line 74 (for superprove) may also face EOL pool issues and should be tested.

### Recommended next step

Same fix as above. After fixing `min`, also add snapshot/archive pinning to the `latest` and default (`formal/all`) `RUN` layers at lines 59 and 74.
