# EXT-51 — Complete compressed-stream validation in isolated external ZIP verifier

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | ISOLATED_CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Reproducible EXT-50 false acceptances

EXT-50 checks ZIP-declared file sizes and allowed compression methods, but Python `zipfile` can stop extracting when the **declared output size** is reached; this does not establish that the full physical DEFLATE stream matches the declaration.

In controlled synthetic ZIPs, with consistent local/central header declarations, manifest prefix hashes/CRC and **synthetic** outer SHA-256 anchors:
1. Raw DEFLATE output **262,144** bytes, declared output **131,072** bytes: EXT-50 `PASS`.
2. Raw DEFLATE output **3,145,728** bytes, declared output **131,072** bytes: EXT-50 `PASS`.
3. Bytes appended **after raw DEFLATE end-of-stream**, still inside the declared compressed span: EXT-50 `PASS`.
4. STORED compressed span longer than declared uncompressed size, while physically contiguous: EXT-50 `PASS`.

These are strict canonical archive-profile and verification-coverage failures, not SHA-256 collisions, historic-file modifications or Darts execution.

## Source-only isolated EXT-51 candidate

After bounded ZIP local/central preflight and before `ZipFile` reads members:
- Record immutable physical member payload offsets and declared sizes.
- For STORED require exact compressed/uncompressed sizes.
- For DEFLATE independently decompress **all physically indexed bytes** with `zlib.decompressobj(-15)` (raw DEFLATE); demand EOF, no trailing compressed bytes and exact declared output length.
- Limit each decompressor-returned chunk to **65,536 bytes** and reject upon **one byte beyond declared output**. This does not establish worst-case OS memory, CPU or deadline guarantees.
- Retain EXT-50 compression allowlist, GPBF policy, header congruence, disk-start=0, ZIP64/extra fields, layout coverage, inventory and manifest checks.

| Suite | Normal | `python -O` |
| --- | ---: | ---: |
| Consolidated synthetic EXT-51 | **48/48** | **48/48** |

All 44 prior EXT-50 tests retained. The four new adversarial cases reject in EXT-51 while returning PASS in EXT-50. Valid STORED and DEFLATE controls remain accepted.

Evidence ZIP `EngineYT_Darts_EXT51_Deflate_Stream_Evidence_20261025.zip` SHA-256 `0f5254aa38d5ed25ac5b724437233d2be9d61278c603c61c3148c000982646c7`, **11 members**, CRC and per-member SHA-256 manifest checked. Candidate SHA-256 `a61568ef65c792482348c5c3766d801076b74938a6ae8d127e6775d21e776639`; harness SHA-256 `8b8da059bc8e563984634b87d49bb41a7d3b05961fdc422185180155209dfebc`.

## NON-TRANSFERABLE limitations

Historical seven originals v040/v041/v042/v043/v050/v052/v053 **NOT_RUN** against EXT-51 (not included in evidence ZIP or located through accessible file/Drive search); full historic-dependent suite **NOT_RUN**. Earlier original-archive PASS statuses cannot be transferred. Neither a formal parser proof nor a worst-case OS memory, CPU or termination guarantee is established. Original historical SHA-256 anchors remain independently unauthenticated (issue #12); ZIP preflight (#13) and decompression (#14) require review.

No Darts code, workers, project tests, production integration, main merge, render or publishing. No gate promotion.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
