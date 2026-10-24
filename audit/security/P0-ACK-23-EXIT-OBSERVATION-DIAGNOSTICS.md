# ACK-23 — Exit observations and cleanup diagnostics

Date: 2026-10-24. Status: STATIC_AST_PASS / PROPOSED_NOT_APPLIED / NOT_RUN.

## New static findings in the ACK-22 proposal

- ACK23-OBS-01: The proposed finish method observes p.wait and checks returncode, but does not update exit_confirmed. A successful COMMITTED path may retain a false observation flag. ACK-22 lines 170-176.
- ACK23-OBS-02: The COMMITTED close path closes streams without updating pipes_closed. ACK-22 lines 221-226.
- ACK23-DIAG-03: The best-effort abort helper and exception-aware context manager suppress secondary cleanup exceptions without retaining a stable diagnostic code. ACK-22 lines 183-188 and 229-237.
- ACK23-OBS-04: The abort close loop does not inspect the stream.closed property after close returns. ACK-22 lines 210-218.

These are findings in an unapplied proposal, not runtime defects reproduced in shipped Darts.

## Proposed, unapplied changes

1. Mark exit_confirmed true immediately after a successful wait in finish, before returncode inspection.
2. Introduce a shared close-pipe observer used by abort and normal committed close, recording failed or unconfirmed close observations.
3. Retain bounded fixed-format secondary diagnostic codes without exception text, preserving the original exception.
4. Keep a distinction between local observation, independent OS attestation, and strict Policy B.

## Evidence and integrity

- Source ZIP SHA-256: 3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105
- ACK-22 baseline SHA-256: 1e908f46e21b8ddca97d4d3fee105b65f05ec03470924ee064eed45e86b391a4
- ACK-23 proposed client SHA-256: 4a730ce0d2fb9e1bdd383f22aa5544265521bed2bedffb82ecf7f03f30e65a7e
- Package EngineYT_Darts_ACK23_Exit_Diagnostics_Proposal_20261024.zip SHA-256: 0045dc7648ea800196b692e39957eabbec289d2b011d7720b82d2febee61dc6e
- The package contains seven files: baseline, offline builder, proposed client, unified diff, static inventory, review, and SHA-256 manifest.
- ZIP CRC and manifest hashes PASS. Both baseline and proposal parse with Python AST. No Darts modules executed or imported.
- Twelve negative cases designed, all NOT_RUN.

## Additional open review points

The parent and stdout/stderr reader threads share process streams. There is no explicit concurrency ownership contract for close while read is in progress. Cleanup counters and status are not synchronized for simultaneous abort calls. The 65536-byte stderr retention limit is not a lifetime emitted/accepted-byte guarantee. A successful wait or stream.closed observation is not independent proof of strict physical termination.

ACK-02 OPEN. E5B4D_NO-GO. SEC-02 Windows NOT_RUN. RENDER_NO-GO. PUBLISH_NO-GO. No runtime changes or main merge.
