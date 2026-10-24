# EXT-50 — Narrow-profile ZIP general-purpose flag allowlist

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | ISOLATED_CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Concrete EXT-49 false-acceptance

EXT-49 checks exact local/central ZIP general-purpose flag equality but did not restrict flags that have no supported meaning in this intentionally narrow no-descriptor, non-encrypted historical ZIP profile. Temporary synthetic ZIPs with *matching flags in both headers* and synthetic external hash anchors were accepted as `PASS` for **0x1000**, **0x2000**, **0x8000**, and **0x0100**. Python's ZIP parser may ignore these bits while extracting centrally indexed contents. This is a strict-profile conformance gap, not an exploit, historical original modification, or SHA-256 collision.

## Source-only isolated EXT-50 candidate

After the eight-field local/central equality check, permit only GPBF bit 11 (`0x0800`, UTF-8 names), plus bits 1/2 (`0x0006`) **on DEFLATE entries only**. Explicitly reject descriptors (bit 3) and reject other unsupported flags as `ZIP_GENERAL_PURPOSE_FLAGS_UNSUPPORTED`. The full EXT-49 preflight controls remain; this is a policy-limited ZIP profile, not a universal ZIP parser.

| Synthetic suite | Normal | Python `-O` |
| --- | ---: | ---: |
| Consolidated EXT-50 | **44/44** | **44/44** |

Includes all 35 EXT-49 tests, four demonstrated EXT-49 false-acceptances now rejected, four valid positive-flag combinations retained, plus one STORED member with DEFLATE-only option bits rejected. Execution covers temporary synthetic ZIPs and independent verifier functions only, never Darts code/workers.

**Evidence package:** `EngineYT_Darts_EXT50_General_Purpose_Flags_Evidence_20261025.zip`; SHA-256 `e0b44ab630cb2691efe6bf63e5bec945ef43e20810cdab89699299c594779dcd`; 9 members, ZIP CRC and per-member SHA-256 checked. Isolated candidate SHA-256 `208c96b0af77dfdb04480c5fc805a4fa4fd892ea152b82a28e9181faf826a449`; regression SHA-256 `5409c654f04f487a07a74c37401b65f348f0dd42719d34cfe524d0dbc0564a05`.

## Non-transferable limits and gates

The **seven immutable originals were NOT_RUN** with EXT-50 because they were not supplied in the source-evidence packages nor found by scoped file/Drive discovery. Earlier 7/7 historical findings do **not** transfer. Historical-dependent 51-case suite **NOT_RUN**. No guaranteed worst-case resource bound, OS suspension deadline guarantee, Windows parity, independent original hash authenticity, or production integration.

Retain OPEN issues [#12](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/12), [#13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13), [#14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/14). No Darts workers or project tests, no main merge, render, publication, functional execution or production integration.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
