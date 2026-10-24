# EXT-54 — ZIP physical filename NUL truncation and aliasing

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | ISOLATED_CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Genuine EXT-53 false PASS

Python's `zipfile.ZipInfo` truncates a filename at its first NUL byte. The EXT-53 preflight required local and central **raw filename bytes** to match but did not disallow `0x00`. Consequently, three temporary synthetic v040 ZIPs with self-consistent synthetic member-hash manifests and newly computed **synthetic outer SHA-256 anchors** passed EXT-53 even though the physical name and logical name differed:

1. Raw local and central `VERIFY_V040.py\x00X` becomes logical `VERIFY_V040.py` in ZipInfo, EXT-53 **PASS**.
2. Raw manifest name `MANIFEST_V040_SHA256.json\x00X` becomes its intended nominated manifest in ZipInfo, EXT-53 **PASS**.
3. Raw member name `VERIFY_V040.py\x00HIDDEN` also aliases the logical target, EXT-53 **PASS**.

These are strict ZIP-profile acceptance/interpretation defects, not SHA-256 collisions, historic ZIP modifications, or project-code execution.

## Source-only isolated EXT-54 correction

During bounded central-record preflight, after the local/central raw-byte agreement check, **reject any NUL in raw ZIP member names** with `ZIP_FILENAME_NUL_UNSUPPORTED`. This precedes `ZipInfo`, manifest extraction and independent DEFLATE stream scanning, retaining all EXT-53 safeguards. A non-ASCII, legitimate UTF-8 filename (`ñ`) remains a positive control.

| New synthetic control | EXT-53 | EXT-54 | Stream stage entries EXT-53 / EXT-54 |
| --- | --- | --- | --- |
| Target name NUL suffix `X` | PASS | NUL rejected | 1 / 0 |
| Manifest name NUL suffix `X` | PASS | NUL rejected | 1 / 0 |
| Target name NUL suffix `HIDDEN` | PASS | NUL rejected | 1 / 0 |
| Valid non-ASCII UTF-8 member name | PASS | PASS | 1 / 1 |

Uninstrumented verifier results and separate isolated sentinel stream-entry probes corroborate the above. Existing 56 synthetic EXT-53 cases preserved.

**EXT-54 consolidated synthetic regression: 60/60 normal and 60/60 under `python -O`** on Python 3.13.5/Linux.

**Evidence:** `EngineYT_Darts_EXT54_NUL_Filename_Evidence_20261025.zip` SHA-256 **`e74f8679d36b1dba5b851b7560f24c89335ddf680493b12bab837d6d77a29786`**, 10 members, ZIP CRC and per-member manifest SHA-256 verified. EXT-54 candidate SHA-256 **`b6cd65b92c0e101795386a1b3e4dc97ef17194df49a252fbe8464bde89afa962`**; harness SHA-256 **`ca3f7367a9167a3e90c838a37654b4f2d407adb1c3c1779e3c6f7563a32d29f6`**.

## Non-transferable gates

Seven historic immutable ZIPs **NOT_RUN against EXT-54** (not present in supplied packages); the historic-dependent suite and 653 member hashes **NOT_RUN** for this candidate. Earlier 7/7 PASS_LIMITED from other candidates does not transfer. Independent original SHA256 anchor authenticity remains unestablished (issue #12); parser/profile review issue #13 and decompression resource issue #14 remain OPEN. No formal worst-case OS CPU/memory/termination guarantee, Windows parity, production integration or project execution. Candidate **NOT_APPLIED**. No Darts project tests/workers, `main` merge, render or publication.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
