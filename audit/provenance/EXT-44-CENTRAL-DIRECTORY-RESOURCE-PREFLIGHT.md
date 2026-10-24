# EXT-44 — Pre-parse ZIP central-directory resource cap

**Date:** 2026-10-24. **Status:** SYNTHETIC_REPRODUCED / PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Concrete defect in independent EXT-41 verifier

The 512-member cap was enforced **after** `zipfile.ZipFile(...).infolist()` had allocated Python `ZipInfo` objects for the entire central directory. A synthetic **60,000-empty-entry ZIP** occupies **5,400,022 bytes** (below the 16 MiB archive-size cap) and EXT-41 rejects it with `MEMBER_COUNT_LIMIT` **only after parsing 60,000 entries**. No Darts code is executed.

## Isolated EXT-44 candidate

Adds a bounded preflight of the already captured immutable ZIP bytes, before calling `zipfile.ZipFile`. It inspects the canonical End of Central Directory record and walks fixed central-directory headers without constructing `ZipInfo` objects. It rejects:
- over 512 entries (`MEMBER_COUNT_LIMIT_PREFLIGHT`);
- mismatched or corrupted directory headers/offsets;
- malformed or truncated EOCD and trailing bytes;
- multi-disk ZIP and ZIP64 markers.

A valid ZIP comment is supported. This is an intentionally **strict canonical, single-disk, non-ZIP64 profile**, not a general ZIP parser. Original seven archives fit this profile.

## Regressions

| Candidate | Passed / total | Interpretation |
| --- | ---: | --- |
| EXT-41 | **39/47** | Eight new expected-code/timing mismatches, **not** eight false acceptances |
| EXT-44 | **47/47** | 37 inherited plus 10 new synthetic controls |
| EXT-44 with `python -O` | **47/47** | Optimized verifier subprocesses included |
| Seven immutable historical ZIPs | **7/7 PASS_LIMITED** | **653/653** member SHA-256 matches |

Ten new controls: 512 entries, 513 entries, 60,000 entries, forged small EOCD count, truncated EOCD, multi-disk, ZIP64 marker, valid ZIP comment, corrupted central header and trailing bytes.

## Observed resource differential

Three independent process samples per candidate, same synthetic 60,000-entry ZIP:

| Sample median | EXT-41 | EXT-44 |
| --- | ---: | ---: |
| Elapsed verification | **0.1949 s** | **0.0064 s** |
| Max RSS (Linux KiB) | **135,560** | **123,664** |

Samples are not a worst-case resource guarantee or Policy B proof.

## Reproducibility

`EngineYT_Darts_EXT44_Central_Directory_Resource_Evidence_20261024.zip` SHA-256 **`f074ac48ca2ef00420336442b18ae236365ed96ec4c0916112dca0d790d9ce3b`**, **12 members**. ZIP CRC and package member SHA-256 PASS. Contains isolated EXT-44 verifier (SHA-256 `e03e0e442682723491e4c5e8f1089c9660152bd7a2f9403e266e59147d796796`), 47-case harness, resource differential generator/runner, original inventory, normal/optimized/prior/historical results, technical review and package manifest. The seven original ZIPs and the 60,000-entry synthetic ZIP are **not redistributed**.

## Gates

External hash-anchor authentication still missing (issue #12). No Windows parity or OS-suspension deadline proof. No Darts project code imported/executed, no project tests, workers, render, publication, production integration or main merge.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO. Candidate NOT_APPLIED.**