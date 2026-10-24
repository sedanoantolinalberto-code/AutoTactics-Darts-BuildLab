# P0-TEST-11 — Independent static audit of nine v0.55 synthetic tests

**Date:** 2026-10-24  
**Status:** STATIC_REPRODUCED; no Darts modules, fake workers, subprocesses or renderer executed.  
**Input:** `EngineYT_Darts_S34_v055_BoundedStdout_Integrated_SourceOnly_PRIVATE.zip`, SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## Exact reproduction artifacts

- Read-only AST/ZIP inspector: `EngineYT_Darts_P0_P1_Test_Coverage_Static_2026-10-24.py`, SHA-256 `8da362a5313121835b35343318a035a251abafc38eb5c943131e0cac2b4e10b6`.
- JSON result: `EngineYT_Darts_P0_P1_Test_Coverage_Static_2026-10-24.json`, SHA-256 `fb244ea6f1459ca58a9b5674012df04ca573e5467a76f92f3ef9845d0a2476d7`.
- Full report: `EngineYT_Darts_P0_P1_Test_Coverage_Report_2026-10-24.md`, SHA-256 `082d343e6edb159ffaf864ab59681c2e55b681bd247f3d03a85ccf895f118b4f`.
- Four-file reproducibility bundle: `EngineYT_Darts_P0_P1_Test_Coverage_Package_2026-10-24.zip`, SHA-256 `afc0aeda211d545e3a6a4f8cad1d8606f58ee5d333c692710da152aae6e123ad`; ZIP CRC check PASS.

The inspector parses four Python members from the immutable ZIP, extracts the eight `case(...)` invocations and the ninth direct `slow_hello` case, and compares each against the fake worker's static mode branches. It does **not** run any case.

## Coverage ledger

| Case | test_transport_v055.py | Narrow observation | Not demonstrated |
|---|---:|---|---|
| stdout_flood | 55 | Queue overflow detection | Total stdout bytes emitted and accepted |
| oversized | 61 | Oversized line rejection | Lifetime output ceiling |
| invalid_json | 65 | Invalid response rejection | General protocol security |
| truncated | 69 | Truncated response rejection | Confirmed process termination |
| eof | 73 | EOF rejection | Reaping guarantee |
| forged_ack | 80 | Malformed ACK rejection | Independent response attestation |
| stderr_flood | 92 | Retained buffer <=65536 | Lifetime stderr emitted/accepted <=1048576 |
| file_access_probe | 104 | Synthetic out-of-root marker readable | Windows reproduction or OS confinement |
| slow_hello | 107–112 | Best-effort delayed greeting timeout | Strict Policy B under arbitrary OS suspension |

The fake worker's `eof` mode is the default, not an explicit conditional branch. The delayed greeting test does not call `case(...)`; the count remains nine tests.

## Newly quantified gaps

- `stdout_flood` emits **512 x 15 = 7,680 bytes** of ACK-like lines after HELLO, below the 1,048,576-byte per-stream Policy B lifetime ceiling. Queue saturation is not emission-budget validation.
- `stderr_flood` writes **250,000 bytes** to stderr, and the test asserts at most **65,536 bytes retained**. These are different quantities; neither assertion enforces a lifetime emission/acceptance budget.
- `forged_ack` simultaneously supplies `head='fake'` and `pid=123`. A rejection does not independently exercise each mismatch check; no independent ACK attestation exists.
- The synthetic file probe uses the literal `SYNTHETIC_NONPRIVATE_MARKER`; no evidence of personal-data exfiltration or independent Windows SEC-02 execution is asserted.

## Seven untested obligations

`HELLO-01` (mismatched HELLO PID), `TERM-01` (failed kill/wait and confirmed reaping), `STDIN-01` (blocked write/flush), `TEST-ENV-01` (exception-safe environment restoration), `STDOUT-EMIT` (lifetime output), `STDERR-EMIT` (lifetime output), and `POLICY-B` (strict all-process exit and confirmation under model M).

These are **test-design gaps**, not seven newly proven exploitable defects. The previously proposed HELLO and test-environment source patches remain unapplied. All new negative tests are **NOT_RUN**.

**Frozen:** E5B4D_NO-GO, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO. No change to main.
