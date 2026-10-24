# EXT-56 — Canonical ZIP DOS timestamp validity

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Falsifiable strict-profile acceptance gap

EXT-55 checks ZIP local/central DOS modification timestamp words for exact agreement, but can return **PASS** on matching impossible calendar/clock values. Nine independently generated synthetic v040 ZIPs, preserving byte-for-byte local/central agreement and with recalculated **synthetic** outer SHA-256 anchors, were accepted under EXT-55 with impossible timestamps:

- Hour **31**, minute **63**, second **62** (DOS has 2-second units).
- Month **0** and **13**, day **0**, February **30**, February **29** in **2100** (non-leap), and April **31**.

This is a deliberately strict-profile metadata-consistency false acceptance, not a SHA-256 collision, historic ZIP modification or project-code exploit. Python `zipfile` itself may permit these timestamp fields.

## Isolated correction

After checking equality of local/central timestamp words, EXT-56 validates DOS bit fields (hour <=23, minute <=59, second <=59) and calendar date with `datetime.date`; invalid values reject `ZIP_DOS_TIMESTAMP_INVALID` before invoking any ZIP stream scanner. DOS date range 1980-01-01 to 2107-12-31 is preserved.

| Synthetic differential | EXT-55 | EXT-56 | Stream stage reached EXT-55 / EXT-56 |
| --- | --- | --- | --- |
| Nine impossible DOS date/clock values | 9 PASS | 9 `ZIP_DOS_TIMESTAMP_INVALID` | 1 / 0 for each |
| Three valid positive boundaries (2000 leap day, 1980 minimum, 2107 maximum) | 3 PASS | 3 PASS | 1 / 1 for each |

The independent uninstrumented `verify_one` was compared to an isolated fail-fast stream-entry instrumentation. This is not a full parser proof or a claimed hard OS resource bound.

**Synthetic 85/85 normal and 85/85 Python `-O`** (73 prior EXT-55 cases + 12 new), Python 3.13.5 / Linux. Replay after clean extraction matched captured structured JSON in both modes.

## Reproducible evidence

`EngineYT_Darts_EXT56_Canonical_DOS_Timestamps_Evidence_20261025.zip`: **SHA-256 `ebe0a3ababcb09e1ee48c43d907198e5443bea0b170086dfbc0bbd8c387063d3`**, 18 source-only members, ZIP CRC and per-member SHA-256 manifest checked. Candidate SHA-256 `26066be729632ba0ef8d042130417218a441b66e54499616589dd6db891f574e`, regression harness SHA-256 `109f4142335f9ff831beb0ff309deaf7a45ace35ee70664e61bdb9282e383830`. The package includes the prior standalone candidates needed to reproduce the synthetic tests, both result JSON files and review documentation. No historic originals or synthetic mutated archive binaries are redistributed.

## Mandatory limitations / gates

The 7 immutable historical ZIPs v040/v041/v042/v043/v050/v052/v053 are **NOT_RUN** against EXT-56; earlier 7/7 and 653/653 results from older candidates are not transferable. The historic-dependent suite is **NOT_RUN**; independent authenticity (#12), full ZIP preflight/resource review (#13), decompression OS-resource limits (#14), Windows parity and model-M Policy B deadlines are unproven. Accepting wider ZIP timestamp conventions is **outside this restrictive candidate's profile**, and historical compatibility must be reviewed before integration.

**Candidate NOT_APPLIED**. No Darts project code, workers, project tests, integration, merge to `main`, renders or publishing.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**