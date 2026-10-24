# P0-ACK-20 — Static exception-path closure proposal

**Date:** 2026-10-24. **Status:** STATIC_AST_PASS / PROPOSED_NOT_APPLIED / NOT_RUN.  
**Original ZIP SHA-256:** `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## Newly documented gaps

| ID | Source anchors | Static finding |
|---|---|---|
| ACK20-INIT-01 | original `public_process_client_v055.py:31–34,37–41,71–81`; ACK-19 `:33–36,39–43,73–83` | After `Popen`, queue/event setup and both `Thread.start()` calls are outside the constructor's first cleanup `try`. A failure there bypasses `abort()`. |
| ACK20-EXCHANGE-02 | original `:108–117`; ACK-19 `:110–119` | `_exchange` catches `Exception`, not all `BaseException` subclasses, around pipe write/flush and response read. |
| ACK20-SEND-03 | original `:123–130`; ACK-19 `:125–136` | FRAME body creation and `_exchange` occur before ACK-19's validator catch. |
| ACK20-FINISH-04 | original `:136–148`; ACK-19 `:142–159` | FINISH body creation and exchange occur before the validator catch; close/wait catches `Exception` only. |
| ACK20-ABORT-05 | original `:151–161`; ACK-19 `:162–172` | `abort` labels `FAILED_TERMINAL` before verified exit, suppresses kill/wait exceptions, and short-circuits subsequent aborts. **OPEN; not resolved by ACK-20.** |

These are **lexical control-flow observations**, not runtime reproductions or proof of orphaned children.

## Standalone ACK-20 proposal

An **unapplied** client draft and unified diff from ACK-19 propose:
1. A post-spawn `try/except BaseException` covering queue/event allocation, thread startup and HELLO; on error attempt `abort()` and re-raise.
2. `_exchange` catches `BaseException`, attempts `abort()` and re-raises.
3. `send` and `finish` bring request-body construction and exchange inside their existing validation/failure handlers.
4. FINISH close/wait catches `BaseException`; `COMMITTED` remains after observed zero exit code.

No project code executed. Python `ast.parse` PASS for original, ACK-19 and ACK-20. The read-only inspector enumerates method calls and lexically enclosing `try` handlers; this is **not** a functional test or proof of cleanup.

## Deliverable integrity

`EngineYT_Darts_ACK20_Exception_Closure_Proposal_20261024.zip` SHA-256 `e19ba42e293da9659129cf25a8437011aad667139d9aeaf55cfd241f3cf4b9a4`, seven files, ZIP CRC and member SHA-256 checks PASS.

`EngineYT_Darts_ACK20_Exception_Topology_Review_20261024.md` SHA-256 `75e133b8b100c28751c6fb7f4db0b14857c546bfa1155445d86534fc1d6c07d7`.

## Open gates

- `abort()` can still fail to terminate or reap the child, and cleanup exceptions may mask the triggering error.
- `Popen` may fail before a usable child handle is assigned.
- Strict Policy B remains impossible under failure model M. Neither try/catch nor kill/wait solves arbitrary OS suspension or lifetime emitted/accepted byte bounds.
- ACK-02 independent effect attestation and SEC-02 Windows are not satisfied.

**E5B4D_NO-GO / SEC-02 Windows NOT_RUN / RENDER_NO-GO / PUBLISH_NO-GO. No merge to main.**
