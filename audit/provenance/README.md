# Darts S34 — provenance register (documentary only)

**Status:** DOCUMENTARY_BASELINE / NOT A RELEASE APPROVAL  
**Created:** 2026-10-24  
**Scope:** isolated audit branch only. No changes to `main`, no executable code, no renderer, no publication.

## Current repository facts (live GitHub inspection)

- Repository: `sedanoantolinalberto-code/AutoTactics-Darts-BuildLab` (private).
- Default branch: `main`.
- Branches observed before creating this audit branch: `main`, `s34/windows-off-v023`, `s34/windows-off-v024-rgb-macro-fix`, `s34/windows-off-v025-link-only`.
- The v0.55 integrated source-only ZIP has **not** been shown to be committed to this repository. ZIP lineage and Git lineage must not be conflated.

## External package anchor (Windows PowerShell output supplied by project owner)

- Name: `EngineYT_Darts_S34_v055_BoundedStdout_Integrated_SourceOnly_PRIVATE.zip`
- Byte length: **171747**
- SHA-256: `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`
- ZIP entries: **87**
- Source: owner's Windows PowerShell read-only inventory and hash, 2026-10-24.
- This record anchors a particular byte sequence; it does not authenticate the original author, certify safety, or establish execution of tests.

## Distinct review-only package (do not confuse with integrated ZIP)

- Name: `EngineYT_Darts_S34_v055_BoundedStdout_ReviewOnly_20261022.zip`
- Byte length: **3351**
- SHA-256: `feb35c690e126428642f306c67feec5ed879438085369ccd3d0b1fc63816e795`
- Entries: `AUDITORIA_V055.md`, `EVIDENCE.json`, `public_process_client_v055_candidate.py`.
- This is a different artifact and not a substitute for the integrated source-only package.

## Previous documentary audit claims — require independent reproducibility

Earlier audit reports in the project conversation state: 25 S34 ZIP CRC checks passed; 98 manifest schemas recognized and checked; 4605 file references matched; and six byte-preserving inclusion relations from v0.49 to v0.55. **These are carried forward as reported findings, not re-run by the creation of this Git document.** The corresponding reports, scripts, full source packages and machine-readable outputs must be retained and independently checked before upgrading their status.

## Evidence classes and mandatory labeling

1. `OBSERVED_OWNER_TERMINAL`: verbatim user-supplied command output.
2. `OBSERVED_GITHUB`: live repository metadata, commit, tree or blob.
3. `STATIC_REPRODUCED`: rerunnable file/manifest comparison with inputs, tool version and output hashes.
4. `DOCUMENTARY_REPORTED`: claim in earlier report not independently reproduced in this Git change.
5. `FUNCTIONAL_REPRODUCED`: independently executed synthetic test with isolated inputs and raw logs.
6. `NOT_RUN`: no execution evidence.
7. `PROPOSED`: design/mitigation not yet implemented or accepted.

Never silently promote a lower evidence class to a higher one.

## Open gates

- `SEC-02`: synthetic out-of-root file read reported; Windows independent reproduction NOT_RUN.
- `ACK-02`: ACK alone does not attest independent processing; static concern, not exploit proof.
- `STDIN-01`: synchronous stdin write may block before read timeout; unproven functional risk.
- `HELLO-01`: PID binding hardening candidate; not an observed exploit.
- `TEST-ENV-01`: environment restoration on exceptional exit to review.
- `E5B4D`: STRICT_GUARANTEES_INCOMPATIBLE_UNDER_STATED_MODEL; execution NO-GO under failure model M.
- `Policy B`: all relevant processes terminated **and termination confirmed strictly before 120 seconds**, independent stdout and stderr each <= 1048576 bytes **emitted and accepted** over their entire lifetimes.
- `RENDER_NO-GO`, `PUBLISH_NO-GO`: unchanged.

A Windows ACL or AppContainer denial in one synthetic case may mitigate SEC-02, but does not resolve E5B4D or prove global confinement.

## Acceptance checklist for P1

- [x] Create an isolated documentary branch, without merging to main.
- [x] Register owner-observed v0.55 and ReviewOnly SHA-256 anchors.
- [ ] Record source of every historical ZIP and hash independently.
- [ ] Record tool versions, invocation and raw outputs for each reproduced check.
- [ ] Separate Git commit ancestry from ZIP containment relations.
- [ ] Review complete file inventory for sensitive content before any upload.
- [ ] Require human gate review before any merge or release.
