# P0-DEADLINE-26 / P1-TEST-27 — Read deadline and optimized assertion coverage

**Date:** 2026-10-24. **Evidence:** STATIC_REPRODUCED. **Project runtime:** NOT_RUN.  
**Exact source ZIP SHA-256:** `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## P0-DEADLINE-26 — no post-dequeue deadline validation

In original `public_process_client_v055.py`, `_read()` sets `deadline=time.monotonic()+self._timeout` at line 92. It calls `_out.get_nowait()` at line 96. The **only** `remaining<=0` comparison is line 100 inside the `queue.Empty` handler, before `_out.get(timeout=min(0.025,remaining))` at line 101. The response can then be decoded/returned at line 105 **without a second clock check**.

A response dequeued after the deadline, e.g. because the parent was descheduled between pre-get check and dequeue completion, can be accepted. This is a conditional **local deadline-invariant gap**, not a reproduced late ACK and not a novel proof of the already-frozen model-M impossibility. `_exchange()` also writes/flushes stdin at line 112 before calling `_read()` at 113; STDIN-01 remains independently open.

**Proposed, NOT_APPLIED:** finite timeout validation (TIMEOUT-25), one operation-level deadline including write/flush, and post-dequeue expiration checks. No local patch proves Policy B under arbitrary suspension.

## P1-TEST-27 — optimized Python can skip transport assertions

AST counts on the two exact top-level test scripts:

| File | AST `assert` statements | Explicit `if not __debug__` rejection |
|---|---:|---|
| `test_transport_v055.py` | **13** | **No** |
| `test_v055.py` | **26** | **Yes, line 60** |

In Python, `-O` omits `assert` statements. In `test_transport_v055.py`, this removes checks of queue size (line 37), post-abort state (40), exact rejection reason (46, 77, 110), overflow/oversize reader flags (53, 59), failure-terminal status (79), stderr response/retention (87–88, 91), synthetic file probe equality (103) and elapsed timeout (112). The script still constructs the fixed `BOUNDED_STDOUT_FAKE_WORKER_PASS_LIMITED` verdict at line 118 **if the remaining code completes**. Explicit `else: raise TestFailure` branches remain and can still fail; this is not a claim that optimized runs always PASS.

**Important distinction:** `test_v055.py:60` explicitly raises `RuntimeError('NO_OPTIMIZED_EXECUTION')` under `-O`; the missing-guard finding applies to the transport test only. No tests were run in either mode.

**Proposed, NOT_APPLIED:** fail closed on `not __debug__` in the transport test; preferably convert security-critical `assert` statements into unconditional checks; retain interpreter/version/optimization-mode provenance for any future test evidence.

## Reproduction anchors

Read-only inspector `EngineYT_Darts_P0_AUDIT26_ReadOnly_Inspector_20261024.py` SHA-256 `6929755b25a50fbb3439384ee1049d48173e3adf6ee39ad3f6cdf82412f6889e`.

Full JSON inventory `EngineYT_Darts_P0_DEADLINE26_P1_TEST27_Static_Inventory_20261024.json` SHA-256 `54d756b8cc45ad848a99fbcf4ff11255a1a94cdf56fba0b8854fb75612f1c354`.

Full report `EngineYT_Darts_P0_DEADLINE26_P1_TEST27_Review_20261024.md` SHA-256 `8527c15b481cefba844d99f1c45d1e69e79c8e5b2ffe1d3c735f8fa799913f86`.

Package `EngineYT_Darts_P0_DEADLINE26_P1_TEST27_Static_Evidence_20261024.zip` SHA-256 `60fbd9938666e820ea8f8e80a726808a5c45c6170b100b1b2d5e1edf8ea1eaa1`. Four members; ZIP CRC and member SHA-256 checks PASS.

The inspector only reads ZIP bytes, hashes and parses AST. It does **not** import/run Darts code, launch a child, run tests, render media or change project files.

**Gates:** E5B4D_NO-GO, ACK-02 OPEN, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO. No merge to main.
