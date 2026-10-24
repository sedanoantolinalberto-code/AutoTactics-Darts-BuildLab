# EXT-38 — Consolidated 27-case external verifier regression

**Date:** 2026-10-24. **Status:** PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## New reproducible input-schema defect

EXT-37 checks that the top-level inventory `files` is a list of length seven but not that its entries are objects. Replacing `files[0]` with JSON `null` causes an unhandled `AttributeError` at `verify_one` before its error handler, yielding an unstructured traceback instead of a structured `FAIL`. This is an input-validation/error-reporting gap, **not** a demonstrated SHA-256 bypass or code execution.

EXT-38 candidate adds a seven-entry object-type guard before iterating. The CLI then rejects malformed inventory as `INPUT_INVALID`. No original historical ZIP or manifest changed.

## Single consolidated regression

| Run | PASS | Total | Finding |
| --- | ---: | ---: | --- |
| Original EXT-37 | 26 | 27 | `inventory_entry_nonobject` fails (unstructured error) |
| EXT-38 candidate | **27** | **27** | All checks pass |
| EXT-38 with `python -O` | **27** | **27** | All checks pass |

The 27 cases comprise historical 7-ZIP/653-member baseline (1), ZIP corruption/coverage controls (8), strict JSON and POSIX ZIP metadata (5), path and inventory safety (11), and controlled post-capture ZIP races (2). Historical verification remains **7/7 ZIPs and 653/653 member hashes PASS_LIMITED**. No Darts code imported/executed.

## Reproducibility and package

`EngineYT_Darts_EXT38_Consolidated_Regression_Evidence_20261024.zip` SHA-256 `779508a722ddcacfaeb8257178513384696624509be62de2a1c3feb0add14a3f`, 8 members; ZIP CRC and member SHA-256 package manifest PASS. Includes:
- EXT-38 standalone verifier candidate (SHA-256 `ab18721bb7641ae27efc858d4b1c2e3b924dbf82030fb4c3591acb6447fb59e8`).
- One consolidated 27-case test harness with `--root`, `--inventory`, `--verifier` arguments.
- OPT-30 inventory, pre-fix, post-fix and optimized JSON results, technical review and package manifest.

The original seven historical ZIPs are **not** bundled; they must be supplied externally to reproduce the historical baseline. This avoids altering/repackaging immutable originals.

## Remaining proof obligations

External inventory anchors remain unauthenticated; no formal ZIP-parser proof, atomic filesystem snapshot during capture, Windows validation or Policy B physical OS deadline guarantees. Candidate NOT_APPLIED; independent review before integration. **E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** No main merge, project tests, Darts worker, render or publication.
