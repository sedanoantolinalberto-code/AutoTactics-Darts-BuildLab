# P0-TEST-07 — Synthetic test evidence versus guarantees

**Status:** STATIC REVIEW ONLY / NOT_RUN.  
**Date:** 2026-10-24.  
**Input:** exact v0.55 Integrated SourceOnly ZIP, SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## What the source test actually checks

- `test_transport_v055.py:76–80`: a forged ACK is rejected in a fake-worker scenario, with `ACK_MISMATCH` and logical `FAILED_TERMINAL`. This does **not** show that every ACK is independently authenticated, or that the child OS process exited and was reaped.
- `test_transport_v055.py:82–93`: fake worker emits stderr flood; test checks `len(c._err)<=65536` and eventual `len(c._err)==65536`. This proves at most retained buffer length in that fixture; it does **not** check lifetime emitted stderr bytes against the 1MiB Policy B ceiling.
- `test_transport_v055.py:94–106`: synthetic harmless marker outside worker root is read by the fake worker; expected `{'type':'FILE_ACCESS_PROBE','readable':True}`. This is **evidence of the test's expected sandbox gap**, not exfiltration of personal data. Independent Windows reproduction remains NOT_RUN.
- `test_transport_v055.py:107–113`: slow HELLO raises `CHILD_TIMEOUT` under a .15s configured timeout and test checks one observed run completed in <4 seconds. This is a best-effort observation, not proof of a strict 120-second upper bound under arbitrary OS suspension.

## Additional test hygiene issue: TEST-ENV-01

`test_transport_v055.py:99` assigns `DARTS_V055_PROBE_PATH` in `os.environ`; `:106` removes it after the fixture context. An exception in `case('file_access_probe',file_probe)` can bypass the removal; an already-set original value is not preserved. The enclosing `finally` at lines 114–117 restores `client.ROOT` and `DARTS_V055_FAKE_MODE` but does not restore `DARTS_V055_PROBE_PATH`.

**Proposal, not applied:** save the original value and restore it in the enclosing `finally`, or scope the temporary environment with a context manager that restores exact prior state on all exits. No production impact or exploit is asserted.

## Negative test design — NOT_RUN

| Case | Target | Required observation | Status |
|---|---|---|---|
| TEST-TERM-01 | wait/kill failure path | separate requested/observed/reaped states and survivor detection | NOT_RUN |
| TEST-STDERR-01 | >1MiB stderr emitted | actual emitted vs accepted byte counts, no hidden overflow | NOT_RUN |
| TEST-STDOUT-01 | >1MiB stdout emitted | lifetime byte accounting independent of queue occupancy | NOT_RUN |
| TEST-STDIN-01 | blocked stdin write | total request duration including write and cleanup | NOT_RUN |
| TEST-HELLO-01 | mismatched HELLO PID | local identity consistency rejection | NOT_RUN |
| TEST-ENV-01 | probe exception and preexisting env var | exact environment restoration | NOT_RUN |

These designs do not authorize execution under model M. A synthetic PASS in one environment cannot resolve E5B4D.

**Gates:** E5B4D_NO-GO; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.
