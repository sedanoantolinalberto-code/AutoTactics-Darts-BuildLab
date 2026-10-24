# P0-TERM-06 — Process lifecycle proof obligations (v0.55)

**Status:** STATIC SOURCE REVIEW; **execution:** NOT_RUN; **date:** 2026-10-24.  
**Exact input:** `EngineYT_Darts_S34_v055_BoundedStdout_Integrated_SourceOnly_PRIVATE.zip`, SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.  
**Method:** read-only ZIP member inspection with source line numbers; no import, child process or media rendering.

## Findings and proof gaps

| ID | Source location | Observed source behavior | Unproven property |
|---|---|---|---|
| TERM-01 | `public_process_client_v055.py:151–161` | `abort()` sets `FAILED_TERMINAL` before kill/wait; catches and suppresses exceptions; future `abort()` returns immediately | Process actually exited, was reaped, and exit was confirmed |
| TERM-02 | `public_process_client_v055.py:163–168` | `close()` on COMMITTED closes stdout/stderr without rechecking child state | Complete reader drain / physical lifecycle proof beyond prior `finish()` |
| TERM-03 | `public_process_client_v055.py:42–47,48–62` | stdout reader calls `kill()` after overflow; does not itself wait/reap; sets reader completion event on exit | Bounded, confirmed child termination after reader failure |
| TERM-04 | `public_process_client_v055.py:63–70` | stderr thread drains 4096-byte chunks to EOF, retains first 65536 bytes | Lifetime stderr bytes **emitted and accepted** <=1048576 |
| TERM-05 | `public_process_client_v055.py:108–117` | synchronous stdin write/flush precedes `_read()` timeout | Strict time bound for entire request, including pipe write |
| TERM-06 | `public_process_client_v055.py:35–59` | `Queue(maxsize=2)` bounds retained stdout lines; `readline(MAX_WIRE+1)` bounds one read | Lifetime stdout bytes emitted and accepted <=1048576 |
| TERM-07 | `public_process_client_v055.py:144–149` | `finish()` calls `wait(timeout=self._timeout)` and checks returncode | Policy B under arbitrary OS suspension; timeout is best-effort |
| HELLO-01 | `public_process_client_v055.py:74–79` | HELLO checks integer PID differs from parent, but not `hello['pid']==self.p.pid` | HELLO identity bound to actual child PID; later ACK/COMMITTED do compare `self.p.pid` |
| ACK-02 | `baseline_v054/isolated_public_worker_v054.py:54–66` | worker emits ACK after `session.consume`, COMMITTED after `session.finish` | Independent attestation of effects outside worker trust boundary |

## Important distinctions

- A reported `FAILED_TERMINAL` is **an internal state label**, not evidence of OS process termination.
- A successful `kill()` call, even if observed, is not a strict guarantee that all relevant processes were terminated and termination confirmed within 120 seconds under model M.
- `maxsize=2` limits queue occupancy, **not total stdout output**. `_err` capped at 65536 limits memory retention, **not total stderr output**.
- A worker PID echoed in ACK/COMMITTED is a checked protocol field, not cryptographic remote attestation.
- None of these static concerns proves a successfully exploited vulnerability. Distinguish source-level gaps from experimentally reproduced failures.

## Documentary acceptance matrix (NO tests executed)

1. **TERM-01:** design a lifecycle state machine with separate `ABORT_REQUESTED`, `EXIT_OBSERVED`, `REAP_CONFIRMED` states; record failure reasons instead of swallowing them. This is a **proposal**, not a patch.
2. **TERM-03:** establish a single owner of process termination and reaping; document races between reader thread and parent.
3. **TERM-04/06:** define separate accounting of bytes **emitted** and **accepted**, not only read/captured, and an OS-level enforcement mechanism if any such guarantee is claimed.
4. **TERM-05:** include pipe write in the request-level deadline model; a read deadline starting after write is insufficient.
5. **HELLO-01:** require claimed HELLO PID to match `self.p.pid` as a local consistency check, while explicitly not claiming it establishes secure identity.
6. **ACK-02:** define a trust boundary and what independent evidence of state application would actually look like.
7. **E5B4D:** do not execute or promote tests until strict Policy B's compatibility with model M is formally resolved.

**Frozen:** E5B4D_NO-GO, RENDER_NO-GO, PUBLISH_NO-GO. No changes to `main`.
