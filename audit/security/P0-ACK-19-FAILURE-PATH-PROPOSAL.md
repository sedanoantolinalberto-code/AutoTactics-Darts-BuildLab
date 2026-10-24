# ACK-19 — Failure-path correction proposal (NOT APPLIED)

**Date:** 2026-10-24. **Status:** STATIC_AST_PASS / NOT_RUN / NOT_APPLIED.

Revises the standalone ACK-18 client proposal, not the original Darts code.

## Proposed changes

- Place `digest(body)` inside the `send()` and `finish()` validator try blocks.
- Preserve the existing `ProposedSchemaRejected` to `ProcessRejected` conversion.
- Add a narrowly scoped `except BaseException: self.abort(); raise` for unexpected validation or digest exceptions.
- Keep `COMMITTED` assignment after `wait()` and observed zero exit code, as already proposed in ACK-18.

## Verified artifacts

- `EngineYT_Darts_ACK19_public_process_client_v055_PROPOSED.py` — syntax parsed, not executed.
- `EngineYT_Darts_ACK19_Failure_Path_PROPOSED.diff` — precise delta from ACK-18.
- `EngineYT_Darts_ACK19_Failure_Path_Review_20261024.md` — scope, limitations, review criteria.
- `EngineYT_Darts_ACK19_Failure_Path_Proposal_20261024.zip` SHA-256 `c09b19a439aba3cab8966805cac55d2c16d7c63ea6f66ecd9b081b695bb503fe`; ZIP CRC and manifest member hashes verified.

## Unresolved

The original `abort()` sets `FAILED_TERMINAL` before confirming process exit and suppresses kill/wait errors. The new catch cannot guarantee physical process termination or strict Policy B. Code outside the new validator boundary also needs a separate comprehensive failure-path audit. ACK-02 independent effect attestation remains unproven.

**No Darts imports, tests, worker launches, renders, main changes or publication.** E5B4D_NO-GO; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.
