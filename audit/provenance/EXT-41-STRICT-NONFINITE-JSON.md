# EXT-41 — Strict JSON NaN/Infinity parser regression

**Date:** 2026-10-24. **Status:** PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Falsifiable finding

EXT-40 uses Python `json.loads` without `parse_constant`, which accepts nonstandard JSON constants `NaN`, `Infinity`, and `-Infinity`. Controlled synthetic cases show:

- Inventory with an additional `NaN` field: EXT-40 reports **PASS_LIMITED**, rather than rejecting the non-RFC-8259 JSON.
- ZIP manifest with an additional `Infinity` field: EXT-40 reports **PASS**, when the synthetic ZIP is repacked and its synthetic outer SHA-256 inventory anchor is updated.

These are **JSON conformance and cross-tool interpretation defects**, not demonstrated cryptographic hash bypasses.

## EXT-41 isolated candidate

Supply `parse_constant=reject_nonfinite_json` for **both** inventory and embedded-manifest JSON decoding. Nonfinite inventory values produce structured CLI `FAIL / INPUT_INVALID`; nonfinite embedded-manifest values produce `FAIL / MANIFEST_NONFINITE_JSON_NUMBER`.

| Run | Passed | Total |
| --- | ---: | ---: |
| EXT-40 | **35** | 37 |
| EXT-41 | **37** | 37 |
| EXT-41 with `python -O` (propagated to subprocesses) | **37** | 37 |

Historical ZIPs **7/7 PASS_LIMITED**, **653/653** manifest member SHA-256 checks unchanged. Optimized consolidated test sample: 12.44 seconds, 103584 KiB maximum RSS, **not** a resource bound.

## Evidence

`EngineYT_Darts_EXT41_Strict_JSON_Regression_Evidence_20261024.zip` SHA-256 `00d54c21a8faa44e374f2f73922f052eeff33188c7b437d9747279a5ba2b2bbf`, eight files, ZIP CRC and package member SHA-256 manifest PASS. Includes candidate, consolidated 37-case harness, historical inventory, pre-fix/normal/optimized results, review and manifest. Seven original historical ZIPs are **not** repackaged.

## Remaining gates

Input inventory hash anchors remain unauthenticated; no external chain of custody, Windows parity, formal resource guarantee, or OS-level Policy B proof. Candidate **NOT_APPLIED**, no Darts code imported or executed, no main merge, render or publication.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
