# P1-OPT-28 — Optimized Python bypasses historical verification assertions

**Date:** 2026-10-24. **Evidence:** STATIC_AST_AND_COMPILE_REPRODUCED. **Darts runtime:** NOT_RUN.

## New findings

A source-only inspector parsed and compiled **19** selected historical root-level verification, test and runner scripts, using `compile(..., optimize=0)` and `compile(..., optimize=1)` without executing them. The optimized bytecode has **zero `LOAD_ASSERTION_ERROR` instructions** for all 19 scripts.

Six **integrity verifier** entrypoints have assert-based digest or provenance comparisons, lack an unconditional `if not __debug__: raise` guard, and contain success print statements:

| Version | Entrypoint | Assert statements | Success line |
|---|---|---:|---:|
| v0.40 | `VERIFY_V040.py` | 2 | 15 |
| v0.41 | `VERIFY_V041.py` | 3 | 16 |
| v0.42 | `VERIFY_V042.py` | 3 | 13 |
| v0.43 | `VERIFY_V043.py` | 3 | 13 |
| v0.52 | `VERIFY_V052.py` | 3 | 12 |
| v0.53 | `VERIFY_V053.py` | 4 | 15 |

**Impact:** with `python -O`, v040–v043 compute but do not compare file hashes, v052 computes but does not compare per-file hashes, and v053 omits the `read_bytes()`/hash expressions inside assertions entirely. Their PASS printouts can be reached without these integrity predicates; unrelated errors may still stop execution. This is **not** a live tampering experiment.

Historical test/runner entrypoints with assert-dependent checks and no effective fail-closed optimization guard: `run_v045.py` (5), `test_v046.py` (19), `test_v047.py` (17), `test_v048.py` (19), `test_v050.py` (33), `test_transport_v055.py` (13).

**OPT28-GUARD-01:** `test_v050.py:30` uses `assert __debug__` to reject optimization. That is ineffective: the optimized compiler removes the entire assertion. The normal compiled bytecode has 32 `LOAD_ASSERTION_ERROR` opcodes for 33 AST assert nodes; the optimized version has zero. This is independently established through in-memory bytecode inspection.

**Controls that differ:** `test_v049.py`, `test_v051.py`–`test_v055.py` (main tests), and `verify_v034.py` have an explicit fail-closed `if not __debug__: raise` pattern; `test_transport_v055.py` does not. `verify_v044.py` uses unconditional raises for its core comparisons.

## Reproduction

Original v0.55 ZIP SHA-256: `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`. The JSON inventory records exact historical ZIP and member hashes, assert locations, guard checks and bytecode counts for all 19 scripts.

Package: `EngineYT_Darts_P1_OPT28_Static_Evidence_20261024.zip` SHA-256 `56ea28725e44552f94f44faa268cb83f6c574a5348713a14468ac2341a96dfd9`. Four files: read-only inspector, inventory, review and SHA-256 manifest. ZIP CRC and member hashes PASS. The inspector does not import or execute Darts code or start workers.

## Remediation criteria (NOT_APPLIED)

1. Replace verifier integrity `assert` with unconditional `if ...: raise`, and record optimization mode in evidence.
2. Reject optimized mode unconditionally in legacy tests, or convert all security-relevant assertions to unconditional checks.
3. Replace `test_v050.py:30` `assert __debug__` with `if not __debug__: raise RuntimeError(...)`.
4. Do not retroactively promote prior PASS reports without exact invocation and optimization-mode provenance.
5. Preserve TEST-27 as a separate v0.55 transport-test finding.

**No change of gates:** E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO. No project tests run, no code patched, no merge to main.
