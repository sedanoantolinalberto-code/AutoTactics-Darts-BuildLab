# ACK-22 — Preserving primary exceptions during cleanup

**Date:** 2026-10-24. **Status:** STATIC_AST_PASS / PROPOSED_NOT_APPLIED / NOT_RUN.

ACK-22 is an isolated text patch to the **ACK-21 proposal**, not a modification of Darts production code. It addresses four static failure paths in ACK-21:

1. `__init__`, `_exchange`, `send` and `finish` invoke `abort()` in error handlers. An exception in `abort()` may replace the triggering exception.
2. `send` invokes `abort()` before raising `PACKET_INVALID`, so a cleanup exception may prevent the intended rejection.
3. `__exit__` calls `close()` during exception unwinding; a close error may mask the exception raised by the `with` body.
4. `send` increments `_seq` outside its guarded validation `try`.

## Unapplied proposal

- Add `_abort_best_effort()` to attempt `abort()` without replacing a primary error if cleanup raises.
- Use that helper at exception-handling sites and the invalid-packet rejection.
- Make `__exit__` preserve an active `with`-body exception, while leaving errors visible when no such exception exists.
- Move `_seq` / `_prev` updates inside the guarded `send` block.

## Independent static checks

- Both input ACK-21 and output ACK-22 parse with `ast.parse`.
- AST inspection finds direct `self.abort()` calls only in the helper and `close()`, not in exception handlers.
- `__exit__` returns `False` and has a `BaseException` handler for secondary close failures.
- `send` state update occurs inside the guarded `try`.
- Ten negative cases specified, **all NOT_RUN**.
- ZIP CRC and member SHA-256 manifest checks PASS.

## Reproducible artifact anchors

- Input ACK-21 SHA-256: `06ccd774de6aa39b48e85e9c4e3077de1224f00674f0cb587e041c760a6870b5`.
- ACK-22 proposal SHA-256: `1e908f46e21b8ddca97d4d3fee105b65f05ec03470924ee064eed45e86b391a4`.
- Package `EngineYT_Darts_ACK22_Primary_Exception_Proposal_20261024.zip` SHA-256: `352dfd32d91fb11895a1e7739a4695a5c5024a267e5024f96b91b0b0f95b8c5a`.
- Source-only builder: `build_ack22_static.py`; package also contains source, unified diff, review, JSON inventory and manifest.

## Residuals

This is **exception precedence**, not termination assurance. A cleanup operation may block; secondary errors may be lost; `FAILED_TERMINAL` is not verified physical exit. No child runtime test, Windows SEC-02 test, ACK-02 independent effect proof, or lifetime emitted/accepted stream accounting. Under model M, E5B4D remains NO-GO. No main changes, renders or publication.
