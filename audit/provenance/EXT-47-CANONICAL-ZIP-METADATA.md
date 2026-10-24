# EXT-47 — Canonical ZIP DOS timestamps and member disk-start

**Date:** 2026-10-24. **Status:** SYNTHETIC_REPRODUCED / PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Three reproducible false acceptances in EXT-46 strict profile

EXT-46 enforces six local/central ZIP header metadata fields but does not compare local/central DOS modification timestamps. It also rejects only ZIP64 sentinel disk-start `0xffff`, not a nonzero per-member disk-start index in an otherwise single-disk EOCD. Synthetic v040 copies with a recomputed *synthetic* outer SHA-256 anchor returned `PASS` for each of:

1. Local DOS modification time different from central time.
2. Local DOS modification date different from central date.
3. First central-directory entry disk-start = 1 while EOCD indicates a single disk.

The first two are canonical metadata inconsistencies; the third contradicts the declared single-disk profile. These tests do not change original historical ZIPs, their member contents or original inventory.

## Isolated EXT-47 correction and results

Before `zipfile.ZipFile` parses the bounded immutable snapshot, compare local/central DOS date and time (reject `ZIP_LOCAL_HEADER_MISMATCH`) and reject nonzero per-member disk-start (`ZIP_MULTIDISK_UNSUPPORTED`). Retain prior EXT-46 ZIP64, extra-TLV, descriptor-profile, six header field, inventory, JSON, path, resource and all-member SHA-256 checks.

| Run | Passed | Total |
| --- | ---: | ---: |
| EXT-46 on expanded regression | **58** | 61 |
| EXT-47 normal | **61** | 61 |
| EXT-47 with `python -O` (verifier subprocesses included) | **61** | 61 |
| Seven immutable original ZIPs | **7/7 PASS_LIMITED** | **653/653 member SHA-256 matches** |

All 653 observed historical members have matching local/central DOS timestamps and disk-start 0. The strict single-disk non-ZIP64 no-descriptor profile is not a general ZIP parser. 61 tests are not a formal proof or worst-case resource bound.

## Evidence

`EngineYT_Darts_EXT47_Canonical_ZIP_Metadata_Evidence_20261024.zip` SHA-256 **`f9f25abc892e7dfe6cc6c2e03daa7ac35552a0d38c5a820da4d6648ec3842a1f`**, 10 members, ZIP CRC and per-member manifest SHA-256 PASS. Includes candidate SHA-256 `79f676bfb0af8c12370c824174fed343ff87304518559fe23b0395f9442c49c6`, 61-case harness SHA-256 `5afcb38ee8f7388745751b982103b6556827871c280b76b715a2848bdeb93d2e`, original inventory, pre-fix/normal/optimized/historical outputs, differential, review and package manifest. Historical ZIPs and temporary mutated copies are **not redistributed**.

**Open gates:** independent original ZIP provenance issue #12; parser/resource independent review issue #13; Windows SEC-02 NOT_RUN; Policy B under model M E5B4D_NO-GO. No Darts project code, workers, tests, integration, main merge, render or publication. **ACK-02 OPEN; RENDER_NO-GO; PUBLISH_NO-GO.**