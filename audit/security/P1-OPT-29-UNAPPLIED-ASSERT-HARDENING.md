# P1-OPT-29 — Unapplied fail-closed assertion hardening proposals

**Date:** 2026-10-24. **Status:** PROPOSED_NOT_APPLIED / STATIC_AST_AND_COMPILE_PASS / NOT_RUN.

Follow-up to [OPT-28](P1-OPT-28-HISTORICAL-ASSERT-INTEGRITY.md) and issues [#5](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/5), [#6](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/6).

## Deliverables

Seven standalone source-only proposals for exact historical ZIP members: `VERIFY_V040.py`, `VERIFY_V041.py`, `VERIFY_V042.py`, `VERIFY_V043.py`, `VERIFY_V052.py`, `VERIFY_V053.py` and `test_v050.py`. A standalone AST builder transforms **51** assert nodes into unconditional `if not condition: raise AssertionError(message)` checks.

The v050 `assert __debug__` is instead replaced with `if not __debug__: raise RuntimeError('OPTIMIZED_EXECUTION_NOT_ALLOWED')`.

All seven candidate sources contain zero AST `assert` nodes, parse successfully and compile in memory with `optimize=0` and `optimize=1`. No compiled project code was executed or imported.

## Package integrity

`EngineYT_Darts_P1_OPT29_Assert_Hardening_Proposal_20261024.zip` SHA-256 `ea49883594fab8fc2c86fa5b5126778b313c2e4e8c75c58bbc4f887fd81db209`. Contains 12 members: seven proposed Python sources, independent source-only builder, unified diff, JSON inventory, review and SHA-256 manifest. ZIP CRC and member SHA-256 verification PASS.

The JSON inventory records each historical input ZIP SHA-256, original member SHA-256, proposed member SHA-256 and transformed assertion count.

## Required review before integration

1. The AST unparser normalizes formatting and drops comments; the 507-line diff includes **nonfunctional churn**. A reviewer should apply only intended semantic changes or create a smaller source-preserving patch.
2. Preserve conditional evaluation of assertion messages and exception types; test actual behavior **only after separately authorized governance**.
3. Validate interpreter compatibility for historical versions. The proposal deliberately changes optimized behavior from skipping checks to enforcing them (and explicitly rejecting `-O` for v050).
4. Replacing asserts cannot independently authenticate an unsigned manifest; source provenance and trust remain separate.

**Gates unchanged:** E5B4D_NO-GO, ACK-02 OPEN, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO. No runtime tests, code integration, main merge, media render or publication.
