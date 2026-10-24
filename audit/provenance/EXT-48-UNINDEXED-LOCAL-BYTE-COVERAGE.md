# EXT-48 — Unindexed ZIP local-byte coverage / contiguous strict-profile layout

**2026-10-25 | ISOLATED_SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Falsifiable gap in supplied EXT-45

EXT-45 validates bounded central records and each referenced local filename, rejects ZIP64/malformed extras, then hashes **only the central-directory indexed members**. It does not verify that indexed local header/payload spans account for all bytes before the central directory.

A standalone synthetic ZIP with indexed `VERIFY_V040.py` and `MANIFEST_V040_SHA256.json` plus an **unindexed local header `UNINDEXED-V040.bin` and 72 bytes of orphan header/data** was accepted by EXT-45 `verify_one` as `PASS` with 1/1 manifest-linked hashes, while Python `ZipFile.namelist()` listed only the two indexed names. The synthetic ZIP and its synthetic outer SHA-256 anchor were updated together. No original ZIP was modified, and the demonstration is **not** a hash collision or independent provenance authentication.

Under general ZIP practices, prefixes/padding can be tolerated (including self-extracting ZIPs); the finding is specifically a **coverage omission relative to a deliberately strict canonical profile**, not a universal ZIP specification violation.

## Isolated EXT-48 experiment

Candidate derived byte-for-byte from the exact user-supplied EXT-45 verifier (SHA-256 `66e47b49e259410f256369f54819868b1392c47c9b18cbd34a26c8e54da72202`). During central preflight, it records each referenced physical local interval `[header_offset, local_header_end + declared_compressed_size)`, rejects spans entering the central directory, and requires sorted intervals to cover exactly `[0, central_directory_start)` without gaps or overlaps. It explicitly rejects descriptor bit 3 because this **candidate's** profile is no-descriptor. The candidate is **not** an integrated accumulation of EXT-46/47 fixes; their differing descriptor policy and decompression allowlist remain to reconcile.

| Synthetic class | EXT-45 | Isolated EXT-48 |
| --- | --- | --- |
| Canonical DEFLATE/STORED, ZIP comment, well-formed unknown extra TLV (4) | 4 PASS | 4 PASS |
| Unindexed orphan, trailing padding, middle gap, SFX-style prefix, two orphan records (5) | 5 PASS | 5 `ZIP_UNINDEXED_GAP_OR_OVERLAP` |
| Total expected behavior | **9/9** | **9/9** |
| Python `-O` | **9/9** | **9/9** |

**Source-only evidence:** `EngineYT_Darts_EXT48_Layout_Coverage_Evidence_20261025.zip`, SHA-256 `75fd87aab0666d55b382c05662df8be65f097a4ca8c84dbec0e242a6872f770a`, 8 members; ZIP CRC and per-member manifest hashes checked. Candidate SHA-256 `5e56cfce74426f5fb54f8bb225b24784bc7aa682ae26830662902195d29406f0`; synthetic regression SHA-256 `d59449e44ca22db13266e65879a1922afd89867b5f05374ffc1a7cef5bec0600`. Python 3.13.5/Linux.

## Mandatory limitations and open obligations

- **Seven original historical ZIPs NOT_RUN against EXT-48:** originals are not bundled with the supplied EXT-45 evidence. Do not transfer the previously reported 7/7 historical PASS_LIMITED to this candidate.
- Previous historical-dependent 51-case consolidated suite **NOT_RUN**; only nine independent synthetic cases were exercised.
- Strict gapless layout excludes otherwise readable self-extracting/padded ZIPs intentionally; no broad ZIP compatibility is asserted.
- Need reconcile competing EXT-46/EXT-47 candidate scopes and test the combined candidate against original seven immutable ZIPs before considering integration.
- Existing [issue #13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) covers ZIP preflight/layout/resource review; [#14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/14) decompression; [#12](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/12) independent historical anchor authenticity. None are closed.
- No Windows parity or formal resource proof; no Darts modules/workers, project tests, render, publication, main merge or production integration.

**Gates unchanged: E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
