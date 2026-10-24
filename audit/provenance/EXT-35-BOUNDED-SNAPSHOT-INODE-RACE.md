# EXT-35 — Bounded byte snapshot binds ZIP digest to parsed contents

**Date:** 2026-10-24. **Evidence:** SYNTHETIC_DIFFERENTIAL_REPRODUCED. **Status:** PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Reproduced EXT-34 residual defect

EXT-34 uses one open descriptor to hash and parse a ZIP, but seeks back to the beginning between operations. A concurrent writer can change bytes in the **same inode** between hashing and parsing. An isolated test built two **equal-length** synthetic ZIP_STORED archives, changed one non-target member and updated its embedded manifest, then overwrote the same file in place exactly as `ZipFile` was called.

- **EXT-34:** accepted the modified member/manifest while reporting the outer SHA-256 of the original archive.
- **EXT-35:** accepted the original captured bytes, and both its reported outer digest and verified manifest came from that same captured byte string.
- Synthetic ZIP length: **518,169 bytes** in each version; no path swap, only same-inode overwrite.
- Seven immutable historical archives: **7/7 PASS_LIMITED**, **653/653** non-manifest member SHA-256 comparisons match.
- No Darts module imported or executed, no worker launched.

## Candidate change

Read at most `MAX_ARCHIVE+1` bytes through the already-open file handle, reject oversized content, calculate SHA-256 of the immutable `bytes` snapshot, then parse **`zipfile.ZipFile(io.BytesIO(snapshot))`**. This eliminates the post-hash in-place mutation window between hash and ZIP parse, not all filesystem races.

## Package

`EngineYT_Darts_EXT35_Bounded_Snapshot_Evidence_20261024.zip` SHA-256 `3eb24024741916982a2c87195013f61b922350f2ddeb84da0298103a2495ad3c`. Five files: standalone candidate, synthetic builder, JSON results, technical review, package SHA-256 manifest. ZIP CRC and member hashes PASS.

## Explicit remaining limitations

- This **is not** an atomic filesystem snapshot. Concurrent writes **during capture** can yield mixed bytes; external anchor authenticity is unproven.
- Bounded ZIP input memory does not prove OS-level process termination under model M, nor bound total interpreter RSS.
- Candidate has not been integrated into production or main. No independent review of open-file symlink policy, file modes, or platform-specific behavior yet.
- A coherent attacker-controlled inventory + ZIP can still pass; independent signed/custodied anchors are required for provenance certification.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** No runtime project tests, merge, render or publication.
