# EXT-47 — Local/central ZIP header congruence

**2026-10-24 | SYNTHETIC_REPRODUCED | PASS_LIMITED | ISOLATED_CANDIDATE_NOT_APPLIED | DARTS_NOT_RUN**

## Six EXT-46 false acceptances

Python's ZIP reader uses central-directory metadata. EXT-46 inspected local header signatures, filenames and ZIP64/extra-field safety but did not compare other local metadata with the central directory. Controlled **temporary v040 ZIP byte copies**, each with a recalculated **synthetic** outer SHA-256 anchor, were all accepted by EXT-46 despite one of six local/central contradictions:

1. Required extraction version changed locally to 45.
2. Local-only encryption flag set.
3. Local-only compression method changed to LZMA.
4. Local-only CRC32 changed to zero.
5. Local-only compressed size changed to zero.
6. Local-only uncompressed size changed to zero.

All six returned **PASS** under EXT-46, even though local-header metadata disagreed with central records. This is a ZIP reader-interpretation ambiguity, not SHA-256 collision, Darts code execution or modification of original archives.

## EXT-47 isolated correction

Before invoking Python ZipFile on the already captured immutable snapshot, compare local and central version-needed, flags and compression method. Where the data-descriptor flag (bit 3) is clear, require exact local/central CRC32, compressed size and uncompressed size agreement. If bit 3 is set, allow local CRC/sizes to be placeholders as permitted by ZIP format, while still enforcing version/flags/method.

| Run | Passed | Total |
| --- | ---: | ---: |
| EXT-46 with six additional cases | **54** | 60 |
| EXT-47 | **60** | 60 |
| EXT-47 under `python -O` including subprocesses | **60** | 60 |
| Original seven immutable ZIPs | **7/7 PASS_LIMITED** | **653/653 member hashes** |

All **660** original ZIP entries use DEFLATE and general-purpose flags zero. Seven original archive SHA-256 values still match their locally supplied inventory anchors; these remain independently unauthenticated.

## Evidence, limits and gates

`EngineYT_Darts_EXT47_Local_Central_Congruence_Evidence_20261024.zip` SHA-256 **`3dd8ee63fbc435932e5783729615d6d08bab4661729045dbac163593bd15323a`**, 10 members, ZIP CRC and per-member SHA-256 PASS. Includes isolated candidate (SHA-256 `cbb3a0d6b2f0e18f3dcf459aeb1cf68bdfe4650c372eea85f424a6ff80586c96`), 60-case harness (SHA-256 `f8ad8bae005f6b83c0efe8c898b3fe0a469ae7c8278b0598fcbdf2e38c6b98d6`), inventory, before/normal/optimized/historical/differential results, review and manifest. Original ZIPs are not redistributed.

Open proof obligations: independent ZIP preflight/resource review issue #13, decompressor-resource issue #14, independent provenance anchors issue #12, Windows SEC-02 and Policy B model-M. Candidate NOT_APPLIED; no Darts modules, workers, project tests, main merge, render, publication or production integration.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**