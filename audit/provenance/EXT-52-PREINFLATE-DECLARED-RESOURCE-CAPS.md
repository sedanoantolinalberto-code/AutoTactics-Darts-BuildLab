# EXT-52 — Early declared-resource caps before ZIP decompression

**Date: 2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | ISOLATED_CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Concrete EXT-51 defect

`verify_one` in isolated EXT-51 called `preflight_zip_directory`, then **`verify_complete_compressed_streams`**, and only afterward checked the declared `MAX_MEMBER=2 MiB`, `MAX_TOTAL=32 MiB`, and `MAX_RATIO=100:1` using `ZipInfo`. Three temporary, internally coherent synthetic v040 ZIPs demonstrated that disqualified declared archive metadata unnecessarily reached the DEFLATE scanner:

| Synthetic sample | EXT-51 uninstrumented | EXT-52 uninstrumented | Scanner invoked before rejection, EXT-51 / EXT-52 |
| --- | --- | --- | --- |
| 1 MiB member expanding >100:1 | `COMPRESSION_RATIO_LIMIT` | `COMPRESSION_RATIO_LIMIT_PREFLIGHT` | **1 / 0** |
| Single 3 MiB member | `MEMBER_SIZE_LIMIT` | `MEMBER_SIZE_LIMIT_PREFLIGHT` | **1 / 0** |
| Twenty 1,700 KiB members, 34,816,000 B total | `TOTAL_SIZE_LIMIT` | `TOTAL_SIZE_LIMIT_PREFLIGHT` | **1 / 0** |
| Valid ~1.5 MiB positive | `PASS` | `PASS` | **1 / 1** |
| Valid ~3.2 MiB three-member positive | `PASS` | `PASS` | **1 / 1** |

Each sample has a synthetic manifest and synthetic recomputed outer SHA-256 only. Instrumentation substitutes a sentinel for the isolated stream scanner and restores it after each case; separate uninstrumented invocations validate the genuine verifier verdict. No Darts module or original historical archive is executed or modified.

## Isolated change

Within the bounded central-directory/local-header preflight, check **per-member declared uncompressed size**, **declared expansion ratio** (integer arithmetic), and **cumulative declared uncompressed size**, **before** invoking any decompressor or Python `ZipInfo` allocation. The source change preserves EXT-51 stream completeness and all prior profile checks.

| Regression scope | Python normal | `python -O` |
| --- | ---: | ---: |
| Original EXT-51 standalone synthetic baseline | **48/48** | **48/48** |
| EXT-52 expanded synthetic suite | **53/53** | **53/53** |

**Environment:** Python 3.13.5 / Linux; synchronous isolated synthetic verification.

**Evidence:** `EngineYT_Darts_EXT52_PreInflate_Resource_Caps_Evidence_20261025.zip`, SHA-256 **`8956dbb811f57c2f80f22c740447e1c55c9ddb790659c608dddf2a60817a8569`**, **10 members**, ZIP CRC and per-member manifest SHA-256 verified. Contains EXT-51 baseline, EXT-52 source-only candidate SHA-256 **`47ea15dc122a74f2df5b8bee23282b1d4f6988428d149364affdf8f433ea70b3`**, 53-case harness SHA-256 **`f886a380464d88eae8febb43f472259599c74b6b76afad705985e01e83a2db79`**, normal/optimized and baseline results, review, manifest.

## Mandatory limitations and gates

**Seven immutable historic originals (v040/v041/v042/v043/v050/v052/v053) NOT_RUN against EXT-52.** The older 7/7 and 653/653 results do not transfer. The historic-dependent suite NOT_RUN. The 512 KiB manifest-specific size cap is still enforced **after** stream preflight (general per-member 2 MiB limit applies earlier). Neither this improvement nor 53 tests establishes hard OS memory/CPU/termination bounds, Python-version parity, Windows parity or historical authenticity.

Issues [#12](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/12) (independent provenance), [#13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) (ZIP preflight) and [#14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/14) (decompression) remain OPEN. **Candidate NOT_APPLIED**; no project tests, Darts workers, functional engine execution, `main` merge, render or publication.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
