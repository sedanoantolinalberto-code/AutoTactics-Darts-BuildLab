# EXT-40 — JSON depth cap and in-flight capture regression

**Date:** 2026-10-24. **Status:** PASS_LIMITED / ISOLATED_CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Reproduced defect in EXT-39

The standalone verifier limits untrusted inventory size but not JSON nesting. A 20,001-byte inventory containing 10,000 nested arrays triggers an **unhandled RecursionError**, yielding an unstructured CLI traceback. A valid inventory with 180 nested levels in an unused field passes as PASS_LIMITED. A 10,000-deep embedded ZIP manifest already fails generically as ARCHIVE_OR_INPUT_ERROR.

## Isolated EXT-40 candidate

Adds a linear byte-level JSON nesting scan, capped at **128 levels**, to both inventory and embedded manifests. Brackets inside quoted JSON strings, including escaped quotes, do not count toward depth. Strict JSON decoding remains in place. CLI also catches RuntimeError for fail-closed handling. Harness replaces its own assert-based synthetic preconditions with explicit checks.

**Observed:** EXT-39 **32/35**, EXT-40 **35/35**, EXT-40 under `python -O` (also propagated to subprocesses) **35/35**. All seven immutable historical ZIPs remain **7/7 PASS_LIMITED**, **653/653 member SHA-256 matches**.

A deterministic synthetic same-inode write **during** bounded snapshot capture produced mixed bytes and returned ARCHIVE_HASH_MISMATCH against the supplied A anchor. This is a limited negative case, **not** proof of atomic capture or universal detection.

## Observed resource sample (not a guarantee)

Single POSIX `/usr/bin/time` run of the seven-ZIP historical baseline: **0.72 seconds elapsed, 96,800 KiB maximum RSS**. This is not a worst-case bound or Policy B proof. Existing resource caps remain: ZIP 16 MiB, inventory/manifest 512 KiB, 512 entries, 2 MiB per member, declared 32 MiB total, compression ratio 100:1.

## Evidence

`EngineYT_Darts_EXT40_JSON_Depth_And_Capture_Evidence_20261024.zip` SHA-256 **`ee92fe3610feed6f5d284401d5c7b57b2b8665893cac7987fbb665eb1d8b0a34`**. Nine members: candidate, 35-case harness, inventory, pre-fix/normal/optimized results, historical results, review and SHA-256 package manifest. ZIP CRC and manifest member SHA-256 PASS. Historical ZIPs are not bundled.

**Limitations:** Inventory/ZIP outer anchors not independently authenticated. POSIX-only no-follow behavior; Windows SEC-02 NOT_RUN. Concurrent writes during capture remain possible. No Darts modules imported/executed, no project tests, no main merge, no render, no publication. **E5B4D_NO-GO, ACK-02 OPEN, RENDER_NO-GO, PUBLISH_NO-GO**. Candidate NOT_APPLIED.