# EXT-55 — Unsafe ZIP metadata gates before decompression

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Verified ordering defect in EXT-54

The independent verifier EXT-54 checks raw ZIP local/central metadata but calls `verify_complete_compressed_streams` before checking **decoded unsafe member names, duplicate logical names, Unix special-file type metadata and manifest existence**. Eleven controlled, internally consistent, synthetic ZIP variants were rejected by EXT-54 **only after** entering the raw DEFLATE stream-checking stage. This is a **late-rejection/resource-ordering defect**, not a demonstrated false PASS or ZIP extraction escape.

## Isolated EXT-55 correction

The source-only candidate moves these checks into the already bounded central-directory preflight, before `ZipInfo` construction and any DEFLATE stream scan, while preserving the existing later defense-in-depth checks. It uses CP437 or UTF-8 according to general-purpose bit 11, rejects empty/absolute/backslash/colon/parent-or-dot-segment/directory-suffix logical filenames, duplicate decoded names, and nonregular POSIX creator-system 3 entry types. It also demands the nominated manifest name appear in the preflight records.

| Synthetic cases | EXT-54 scanner entered | EXT-55 scanner entered | EXT-55 result |
| --- | ---: | ---: | --- |
| 7 unsafe filename/path variants | 1 each | 0 each | Same `UNSAFE_MEMBER_NAME` rejection |
| Duplicate logical filename | 1 | 0 | `DUPLICATE_NAMES` |
| Unix symlink and Unix directory type (2) | 1 each | 0 each | `UNSAFE_UNIX_FILE_TYPE` |
| Missing nominated manifest | 1 | 0 | `MANIFEST_MISSING` |
| 2 safe UTF-8 / nested-path positive controls | 1 each | 1 each | `PASS` |

Normal, unmodified `verify_one` verdicts were checked separately from a synthetic sentinel probe instrumenting entry into the isolated stream checker. No Darts modules or historical originals were opened in these tests.

- User-supplied **original EXT-54 60-case suite replay**: **60/60 Python normal and 60/60 Python `-O`**.
- EXT-55 consolidated **73-case** synthetic suite (60 previous + 13 new): **73/73 normal and 73/73 `python -O`**.
- Independent extraction/replay from the packaged evidence: **73/73** both modes; the structured JSON results match the captured run.
- Environment: **Python 3.13.5 / Linux**.

## Evidence

Evidence archive `EngineYT_Darts_EXT55_Early_Metadata_Gates_Evidence_20261025.zip`: **SHA-256 `77711fa8736d0f0f8c51c17ef06f2484802369748b2d28ce0eb3ee41ae21f4fc`**, **17 members**, ZIP CRC and per-member SHA-256 manifest validated.

Isolated candidate SHA-256: `75be7134a17360d3788ebe414637e779f4eb3c9b5de5d578f215892f2313b2d2`.

Reproducible full harness SHA-256: `edd89895ec3db1341b7c2250dded573b182c2666a6d3c3867122e0a93d47b9e3`.

The archive contains all standalone external-verifier versions referenced by the harness, the original and extended regression scripts, captured normal/optimized results, review, and a per-member manifest. Synthetic ZIP fixtures are generated temporarily during tests. No original historical ZIP is redistributed.

## Non-transferable gates

Seven original immutable ZIPs **v040/v041/v042/v043/v050/v052/v053 NOT_RUN** against EXT-55; the historic-dependent full verifier suite and **653 historical member digests NOT_RUN** against this candidate. Prior 7/7 historical PASS_LIMITED cannot be transferred. This change improves rejection ordering, not all ZIP compatibility, parser-completeness proof, historical SHA-256 authenticity, worst-case OS CPU/RAM/termination guarantees, or Windows parity. Existing issues **#12/#13/#14 remain OPEN**.

**Candidate NOT_APPLIED**; audit branch documentation only, no Darts functional code, workers, tests, production integration, `main` merge, render or publication.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**