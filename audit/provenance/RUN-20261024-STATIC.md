# RUN-20261024-STATIC — independent local ZIP verification

**Class:** STATIC_REPRODUCED (container, Python stdlib, read-only inputs)  
**Date:** 2026-10-24  
**Execution:** no Darts modules imported or executed; no subprocess workers; no renderer; no changes to main.

## Inputs

- 25 S34 ZIP files available in the local audit workspace; each file name, byte size, SHA-256, entry count and manifest count recorded in `s34-25-zip-anchors.v1.json`.
- Earlier audit report `EngineYT_Darts_P1_Manifiestos_98_Verificados_2026-10-24.json` used solely as a cross-check, not as the source of the newly computed hashes.
- Script `EngineYT_Darts_P1_Independent_ZIP_Anchors_2026-10-24.py`, SHA-256 `d77e28a0e482c57e40b3e880e493a36e7000e5b3a1ac92076c77c5490400c04f`.
- Full generated report `EngineYT_Darts_P1_25ZIP_Independent_Anchors_2026-10-24.json`, SHA-256 `9868f551065c0911e8564c3d0cab0a0eac2a1b1dcd4e315487f5ca6e7ae120e1`.

## Procedure

Read each ZIP as bytes and calculate SHA-256. Open ZIP with Python's standard-library `zipfile`; run CRC integrity test; inspect member names, path traversal, duplicates, Unix symlink bits, and case-fold collisions; count manifest filenames. Compare all member bytes of v0.49 through v0.54 against the corresponding `baseline_vXXX/` entries in v0.50 through v0.55. Compare recomputed hash, count, CRC and manifest count against the earlier report.

## Observed results

| Measure | Result |
|---|---:|
| ZIPs processed | 25 |
| CRC checks passing | 25/25 |
| Total ZIP bytes | 2,542,251 |
| Total ZIP entries (including repeated historical baselines) | 1,368 |
| Manifest files found | 98 |
| Duplicate names | 0 |
| Unsafe paths | 0 |
| Symlink entries | 0 |
| Case-insensitive name collisions | 0 |
| Previous report package-level cross-checks | 25/25 |
| Byte-identical containment edges | 6/6 |

Containment edges: v049→v050 22/22, v050→v051 33/33, v051→v052 43/43, v052→v053 55/55, v053→v054 66/66, v054→v055 76/76.

**Separate earlier manifest check:** 98/98 manifests and 4,605 listed file references PASS under the previously retained static validator, with report SHA-256 `6d2d613734d453db1a5d7650710fd9d9f4ffd8559a14e44bfedeac7c714aedd4` and script SHA-256 `7a359443c854c729fcf539d2aeef6a64f0cfcc189e2fbb34d51be07f11d5508f`. That check is not rerun by this independent inventory script.

## Boundaries

The 1,368 member count includes nested baselines, not unique independent source files. The 98 manifest count is occurrence count across packages, not distinct manifest definitions. SHA-256 and CRC support byte consistency, not external provenance, rights clearance, sandboxing, correct functional output or security. ZIP containment does not establish Git ancestry.

The full source ZIPs, raw generated JSON and audit script remain outside this Git branch; this commit stores a concise normalized ledger and cryptographic anchors, not the underlying binary inputs. A reviewer must acquire the exact inputs and reproduce the computation before asserting third-party independent verification.

**Gates unchanged:** E5B4D_NO-GO; SEC-02 Windows functional reproduction NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.
