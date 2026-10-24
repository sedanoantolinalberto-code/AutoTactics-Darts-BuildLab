# EXT-49 — Isolated strict ZIP-profile consolidation

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Purpose

User-supplied EXT-48 baseline is consolidated **in an isolated derivative** with separately documented EXT-46/47 controls (not applied to repository runtime code):

- Eight-field local/central equality: extraction version, flags, compression, DOS modification time/date, CRC32, compressed and uncompressed sizes.
- Zero per-member central-directory disk-start.
- STORED/DEFLATE compression allowlist, before any member/manifest extraction; excludes reproducible BZIP2/LZMA per-call resource overshoot.
- EXT-48 gapless physical coverage by central-indexed local header/payload intervals; reject orphan records, gaps, overlaps and SFX-style prefixes.
- Explicit no-data-descriptor bit-3 policy, as chosen for this narrow profile despite differences among earlier isolated research documents.
- Retain earlier ZIP64, TLV, central-record count and immutable-snapshot safeguards.

## Synthetic measurements

**Python 3.13.5 Linux:** **35/35 normal; 35/35 under `python -O`.** Isolated ZIP fixture creation and standalone verifier `verify_one` only. **14** cases accepted by EXT-48 are rejected by consolidated EXT-49; remaining positive controls (STORED, DEFLATE, harmless comment and extra TLV) are preserved. The test set also rechecks EXT-48 unindexed-member and EXT-45 ZIP64 negative controls.

**Source-only evidence:** `EngineYT_Darts_EXT49_Consolidated_ZIP_Profile_Evidence_20261025.zip` SHA-256 `ac4741fe38324d908c9fbace29aa4057bc49430544596a00a5f8cdd40876e6d1`, 9 members, ZIP CRC and per-member SHA-256 manifest checked. Candidate SHA-256 `c919c58ee2b7f31912b8d065e0630698ff0ef69858a7c197c97a95e9ec4b00ff`, harness SHA-256 `74880f4b392ecc8458d74d8dfaeb8d1e8742c0629ec323ce1a0a6128ba6cf5e6`. Original seven historical ZIPs not redistributed.

**Residual concrete flag-policy observation:** additional synthetic probe shows that matching local+central general-purpose flags `0x1000`, `0x2000`, and `0x8000` can still be accepted, requiring follow-up in EXT-50; do not overstate flag-policy completeness.

## Non-transferable limits

- Seven historical v040/v041/v042/v043/v050/v052/v053 ZIPs **NOT_RUN** against EXT-49; those bytes were unavailable here. Earlier historical PASS results **do not transfer**.
- Earlier full 51-case historical-dependent harness **NOT_RUN** against EXT-49.
- No worst-case RAM/CPU proof, Windows parity, external historical provenance authentication or OS-suspension deadline guarantee.
- Strict-profile choices intentionally exclude valid wider ZIP formats. Candidate NOT_APPLIED.
- Issues [#12](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/12), [#13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13), [#14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/14) remain OPEN. No Darts modules/workers/project tests, renders, publishing, integration, or main merge.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
