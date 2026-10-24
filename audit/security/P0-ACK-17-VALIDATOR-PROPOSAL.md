# P0-ACK-17 — Proposed parent-side strict validator

**Date:** 2026-10-24. **Status:** PROPOSED_NOT_APPLIED / NOT_RUN.  
**Input:** `EngineYT_Darts_S34_v055_BoundedStdout_Integrated_SourceOnly_PRIVATE.zip`, SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

A **standalone**, **unapplied** standard-library Python validator draft was prepared, covering HELLO, ACK and COMMITTED. The original ZIP and all repository runtime code are unchanged. Only `ast.parse` of the proposal was performed; no Darts imports, worker launches or tests were run.

## Exact deliverables

- `EngineYT_Darts_ACK17_Proposed_Validator_20261024.py`: SHA-256 `3904b1dd5107f44ae2d3c92fb792bf4a5e9c2c8f5269020768047fe9c29d344f`.
- `EngineYT_Darts_ACK17_Validator_Design_20261024.md`: SHA-256 `39bc91a224599fa0facabcdf2da56eb879c7938f58b9b9385cef47138422e346`.
- `EngineYT_Darts_ACK17_Proposed_Validator_Package_20261024.zip`: SHA-256 `f0e84153588db3f83323d5e4d86f82eb4ebd88d67e253b85e415674c1fee8e17`. CRC and manifest member hashes PASS.

## Controls proposed, not verified

1. Exact response key sets, exact integer types, nonce canonical Base64 and actual child PID consistency.
2. ACK field shape, source-derived camera/overlay/cue enumerations, frame range and expected digest.
3. **COMMITTED exact episode length**: D-15 requires 480, D-16 requires 432; a parent-side check is absent from the current `finish()` which only compares `frames` with `self._seq`. The shipped worker does require the full length at `baseline_v054/isolated_public_worker_v054.py:61–66`. This is a defense-in-depth check under an untrusted-child assumption, not a demonstrated exploit.
4. `intent_count` exact integer bounded by frames; semantic equality with an independent intent reference is still unproven.

## Scope and limitations

- The draft is **not a patch to the project**. Integration must preserve fail-terminal semantics and must undergo code review.
- Exact schemas could reject future extensions; version negotiation needs a separate decision.
- Remaining score and subtitle correctness are not established by type checks.
- Schema validation **cannot** prove that `consume` or `finish` occurred; ACK-02 remains open.
- The draft's exception handling and integration are not functionally validated.
- No guarantee under model M follows from this change.

**Gates unchanged:** E5B4D_NO-GO, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO; no merge to main.
