# EXT-46 — Local/central ZIP metadata coherence preflight

**2026-10-24 | SYNTHETIC_REPRODUCED | PASS_LIMITED | ISOLATED_CANDIDATE_NOT_APPLIED | DARTS_NOT_RUN**

## Falsifiable EXT-45 defect

EXT-45 compares local/central raw filenames and rejects ZIP64/invalid extra fields, but omits comparison of **eight shared local/central header fields**. Python `zipfile` trusts the central directory when extracting; eight temporary synthetic ZIPs with a changed local field and an updated *synthetic* outer SHA-256 inventory anchor were accepted as `PASS` by EXT-45:

1. Extractor version required.
2. General-purpose flags.
3. Compression method.
4. Modification time.
5. Modification date.
6. CRC32.
7. Compressed size.
8. Uncompressed size.

A ninth synthetic case set the central directory's data-descriptor flag (bit 3), which is outside the deliberately strict historical ZIP profile; EXT-45 also returned `PASS`.

**These are canonical ZIP-profile consistency defects, not demonstrated SHA-256 collisions or changes to historical originals.**

## Isolated EXT-46 candidate

Before constructing Python `ZipInfo` records, compare all eight shared local/central fields in the already captured immutable archive snapshot. Return `ZIP_LOCAL_CENTRAL_MISMATCH` on any discrepancy. Reject central bit 3 explicitly with `ZIP_DATA_DESCRIPTOR_UNSUPPORTED`; streaming data descriptors are valid ZIP functionality in other contexts but intentionally unsupported in this narrow profile. Original seven archives have zero data-descriptor entries and consistent shared fields.

| Candidate | Passed / total | Interpretation |
| --- | ---: | --- |
| EXT-45 with expanded regression | **51/60** | Nine false acceptances |
| EXT-46 | **60/60** | All nine rejected |
| EXT-46 with `python -O` | **60/60** | Optimized verifier subprocesses included |
| Original seven immutable ZIPs | **7/7 PASS_LIMITED** | **653/653** member SHA-256 matches |

## Reproducible evidence

`EngineYT_Darts_EXT46_Local_Central_Coherence_Evidence_20261024.zip` SHA-256 **`18f2181bfc94b32b29aa9be81a711a7b776b3f2e1abbc16066a023b7ffbcb034`**, **10 members**; ZIP CRC and per-member SHA-256 manifest PASS. Contains isolated EXT-46 candidate (SHA-256 `7e4e7bc78ab68228d4c60ca0168f85cce654fe7747b38c8e7968e52c0901baa4`), 60-case consolidated harness (SHA-256 `60f0da7ae7b6cdf89cd2b6b09aab159a036c5ff39d575d83412688dc6ff7d342`), unchanged inventory, before/after/optimized/historical results, nine-case differential, review and package manifest. Original seven ZIPs are **not redistributed**.

## Remaining gates

- **Issue #13 OPEN:** independent ZIP parser/profile/resource review, including adversarial overlapping header and directory layouts.
- **Issue #12 OPEN:** independent historical archive hash anchors/signatures and custody validation.
- No worst-case OS resource guarantee, no independent source authenticity, no Windows parity.

No Darts project code imported/executed, no project tests, workers, renders, publishing, production integration or main merge.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO. Candidate NOT_APPLIED.**