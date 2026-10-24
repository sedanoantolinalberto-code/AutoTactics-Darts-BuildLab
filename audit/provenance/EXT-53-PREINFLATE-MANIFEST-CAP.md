# EXT-53 — Early manifest-size constraint before ZIP stream scanning

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Reproducible EXT-52 late-gate defect

The independent EXT-52 verifier correctly preflights each archive member's declared 2 MiB size and the 32 MiB/100:1 archive limits before decompression. The **narrower 512 KiB manifest cap** was still checked only after every indexed compressed stream was independently processed. Two validly structured, temporary synthetic ZIPs with a matching, inventoried manifest name and synthetic SHA-256 anchors demonstrate unnecessary scanning:

| Synthetic manifest | EXT-52 | EXT-53 | Stream scanner entry, EXT-52 / EXT-53 |
| --- | --- | --- | --- |
| Exactly **524,288 bytes** | `PASS` | `PASS` | 1 / 1 |
| **524,289 bytes** | `MANIFEST_SIZE_LIMIT` | `MANIFEST_SIZE_LIMIT_PREFLIGHT` | **1 / 0** |
| **921,600 bytes** | `MANIFEST_SIZE_LIMIT` | `MANIFEST_SIZE_LIMIT_PREFLIGHT` | **1 / 0** |

Each synthetic manifest uses deterministic, bounded, low-compressibility JSON padding; none relies on violating the earlier general ratio or member cap. Both the actual uninstrumented outcome and an isolated sentinel instrumenting entry to the stream checker were verified. All original ZIPs remained untouched.

## Minimal isolated candidate

Pass the inventoried manifest filename to `preflight_zip_directory`. Compare it against the decoded, bounded central-directory filename using the same UTF-8 (GPBF bit 11) / CP437 selection as the Python ZIP reader. A matching declared uncompressed size **greater than 524,288 bytes** now returns `MANIFEST_SIZE_LIMIT_PREFLIGHT` before independent DEFLATE scanning or allocation of `ZipInfo` records.

| Synthetic consolidated battery | Normal | `python -O` |
| --- | ---: | ---: |
| EXT-53 (includes EXT-52's 53 cases) | **56/56** | **56/56** |

**Evidence:** `EngineYT_Darts_EXT53_PreInflate_Manifest_Cap_Evidence_20261025.zip` SHA-256 **`0732df0b4e822d338b67dd8d66e919768c37369526c0bd3b58ab567e0f671fd3`**, 11 members; ZIP CRC and per-member SHA-256 verified. EXT-53 candidate SHA-256 **`bfee30778785efa690c5da11200b3746e49d1988d110b1d121cb70985bbb9324`**. Regression SHA-256 **`089d95adc870f3f6c79a4c03dcfdca89cf3f8af2a3176bdb6d7ed8f2e5892c1b`**. Python 3.13.5 / Linux.

## Bounds and higher gates

The manifest name and anchors are taken from an **untrusted** inventory. This check does not authenticate the historical archive, nor establish full ZIP compatibility, Windows parity or worst-case OS-level CPU/memory/termination guarantees. **All seven immutable historical originals (v040/v041/v042/v043/v050/v052/v053) and 653 member hashes NOT_RUN against EXT-53; earlier PASS claims cannot transfer.** The historical-dependent suite NOT_RUN; candidate NOT_APPLIED.

Issues [#12](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/12), [#13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) and [#14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/14) remain OPEN. No Darts code, workers, project tests, production integration, `main` merge, renders or publication.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
