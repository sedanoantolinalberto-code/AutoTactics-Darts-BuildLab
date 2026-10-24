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

## Audit navigation (2026-10-24)

Use this index to locate the relevant evidence without treating documentary commits as gate approvals.

| Question | Source | Evidence status |
|---|---|---|
| Which original ZIPs were hashed? | [25-ZIP anchors](s34-25-zip-anchors.v1.json), [static audit record](RUN-20261024-STATIC.md) | STATIC_REPRODUCED; raw inputs externally retained |
| Why do v0.37–v0.43 root READMEs mention v0.36? | [Archive lines](DOC-README-01-ARCHIVE-LINES.md) | STATIC_REPRODUCED |
| What are the external S31/v0.34 anchors? | [External anchors](P1-DEPENDENCY-03-EXTERNAL-ANCHORS.md) | STATIC_REPRODUCED |
| Are v0.35–v0.43 and v0.44–v0.55 identical implementations? | [Static AST graph](P1-GRAPH-04-STATIC-AST.md) | STATIC_REPRODUCED, limited |
| Which modules can the v0.55 worker import? | [Worker reachability](P1-IMPORT-08-WORKER-REACHABILITY.md) | STATIC_REPRODUCED, not dynamic |
| What external Python dependencies are specified? | [Dependency inventory](P1-DEP-10-THIRD-PARTY-REPRODUCIBILITY.md) | STATIC_REPRODUCED |
| Does ACK prove application? | [ACK trust-boundary analysis](../security/P0-ACK-12-TRUST-BOUNDARY.md) | STATIC_REASONING_ONLY |
| What process and byte limits remain unproven? | [Lifecycle obligations](../security/P0-TERM-06-LIFECYCLE-PROOF-OBLIGATIONS.md) | STATIC SOURCE REVIEW |
| What do the nine fake-worker tests establish? | [Independent test coverage](../security/P0-TEST-11-INDEPENDENT-COVERAGE.md) | STATIC_REPRODUCED; tests NOT_RUN here |
| What patches are proposed? | [Unapplied hardening diffs](../security/P0-HARDENING-09-PROPOSED-DIFFS.md) | PROPOSED_NOT_APPLIED |
| Which ACK presentation values are actually permitted by existing public ports? | [Source-derived response contract](../security/P0-ACK-16-SOURCE-DERIVED-RESPONSE-CONTRACT.md) | STATIC_REPRODUCED extraction; PROPOSED_NOT_APPLIED schema |
| How are successful child exit and secondary cleanup errors observed in the latest draft? | [ACK-23 observations](../security/P0-ACK-23-EXIT-OBSERVATION-DIAGNOSTICS.md) | STATIC_AST_PASS; proposal NOT_APPLIED / NOT_RUN |
| Are stdout/stderr reader threads confirmed terminated? | [ACK-24 thread lifecycle](../security/P0-ACK-24-READER-THREAD-LIFECYCLE.md) | STATIC_AST_PASS; no joins found; runtime NOT_RUN |
| Can an invalid timeout bypass the parent deadline? | [NaN timeout source audit](../security/P0-TIMEOUT-25-NAN-DEADLINE-BYPASS.md), [P0 issue #2](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/2) | STATIC_REPRODUCED + stdlib semantics; runtime NOT_RUN |
| Does the parent recheck a deadline after dequeuing, and are transport assertions optimization-safe? | [DEADLINE-26 / TEST-27 source audit](../security/P0-DEADLINE-26-P1-TEST-27-STATIC-FINDINGS.md), [deadline issue #3](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/3), [test issue #4](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/4) | STATIC_REPRODUCED; tests NOT_RUN |
| Do historical integrity PASS messages survive unsafe Python optimization? | [OPT-28 historical assert audit](../security/P1-OPT-28-HISTORICAL-ASSERT-INTEGRITY.md), [verifier issue #5](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/5), [test issue #6](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/6) | STATIC AST and bytecode compilation; no project execution |
| Are there isolated source-level candidates to harden optimized historical verifiers? | [OPT-29 seven unapplied candidates](../security/P1-OPT-29-UNAPPLIED-ASSERT-HARDENING.md) | PROPOSED_NOT_APPLIED; 51 asserts transformed, static compile only |
| Can assertion hardening be reviewed without reformatting historical scripts or invalidating manifests? | [OPT-30 minimal diff and manifest binding](../security/P1-OPT-30-MINIMAL-DIFF-MANIFEST-COUPLING.md), [immutable provenance issue #7](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/7) | 51 AST-equivalent proposals; seven manifest links STATIC_REPRODUCED; NOT_APPLIED / NOT_RUN |
| Can all members of immutable historical ZIPs be checked externally with bounded resources? | [EXT-32 full-manifest verifier](EXT-32-ALL-MEMBER-EXTERNAL-VERIFIER.md) | 7/7 archives, 653/653 member hashes, 8/8 synthetic negative cases PASS_LIMITED; no Darts runtime |
| Does the external verifier reject duplicate JSON keys and ZIP special-file metadata? | [EXT-33 differential verifier audit](EXT-33-STRICT-JSON-ZIP-METADATA.md), [issue #8](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/8) | 7/7 originals + 653 hashes; 7/7 new and 8/8 prior synthetic tests PASS_LIMITED; candidate NOT_APPLIED |
| Does the ZIP digest bind to the same archive bytes parsed after the hash check? | [EXT-34 single-descriptor TOCTOU audit](EXT-34-SINGLE-DESCRIPTOR-TOCTOU.md), [issue #9](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/9) | Synthetic path-swap reproduced; candidate PASS_LIMITED 7/7 ZIPs and 653 hashes; NOT_APPLIED |
| Can in-place mutation of an already-open ZIP break the outer-hash/member binding? | [EXT-35 bounded byte snapshot](EXT-35-BOUNDED-SNAPSHOT-INODE-RACE.md), [issue #10](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/10) | Synthetic same-inode overwrite reproduced; candidate 7/7 archives and 653 hashes PASS_LIMITED; NOT_APPLIED |
| Does the external ZIP verifier follow symlinks outside the designated root or block on FIFO files? | [EXT-36 nofollow/FIFO audit](EXT-36-NOFOLLOW-FIFO-OPEN.md), [issue #11](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/11) | Synthetic differential PASS; 7/7 original archives + 653 hashes PASS_LIMITED; candidate NOT_APPLIED |
| Do intermediate directory symlinks or unbounded inventory reads bypass external-verifier constraints? | [EXT-37 root and inventory safety](EXT-37-ROOT-PATH-INVENTORY-BOUNDS.md), [expanded issue #11](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/11) | Differential synthetic tests reproduce EXT-36 gaps; EXT-37 7/7 ZIPs and 653 hashes PASS_LIMITED; candidate NOT_APPLIED |
| Do prior external-verifier regressions pass together, including malformed inventory-entry types? | [EXT-38 unified 27-case regression](EXT-38-CONSOLIDATED-REGRESSION.md), [expanded issue #11](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/11) | EXT-37 26/27; isolated EXT-38 27/27 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; NOT_APPLIED |
| Can an inventory falsely count the same ZIP seven times or relabel its version? | [EXT-39 scope binding](EXT-39-INVENTORY-SCOPE-BINDING.md) | EXT-38 28/30; EXT-39 30/30 normal and optimized; 7 distinct ZIPs / 653 hashes PASS_LIMITED; NOT_APPLIED |
| Does deeply nested JSON disrupt the external verifier, and what happens during capture-time ZIP writes? | [EXT-40 JSON-depth and capture regression](EXT-40-JSON-DEPTH-CAPTURE-REGRESSION.md) | EXT-39 32/35; EXT-40 35/35 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; candidate NOT_APPLIED |
| Does strict JSON parsing reject nonfinite NaN/Infinity constants in inventory and ZIP manifests? | [EXT-41 strict nonfinite JSON](EXT-41-STRICT-NONFINITE-JSON.md) | EXT-40 35/37; EXT-41 37/37 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; candidate NOT_APPLIED |
| Can an internally consistent ZIP and inventory prove historical authenticity without an external trust anchor? | [EXT-42 coherent anchor-substitution demonstration](EXT-42-ANCHOR-AUTHENTICITY-BOUNDARY.md), [issue #12](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/12) | Original anchors reject tampered ZIP; coherently substituted inventory + ZIP returns PASS_LIMITED 7/7, 653 hashes; external provenance NOT_ATTESTED |
| Are historical ZIP hashes corroborated by independent custody evidence beyond the local audit reports? | [EXT-43 source-discovery and 7/7 local crosscheck](EXT-43-CUSTODY-SOURCE-DISCOVERY.md), [issue #12](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/12) | Four local records agree 7/7, but no independent external attestation identified in scoped Gmail/Drive/GitHub/Library searches; GATE OPEN |
| Does the 512-ZIP-member cap apply before central-directory parser allocation? | [EXT-44 ZIP preflight resource regression](EXT-44-CENTRAL-DIRECTORY-RESOURCE-PREFLIGHT.md), [issue #13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) | EXT-41 parses 60,000 entries before rejection; isolated EXT-44 preflight rejects before allocation, 47/47 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; NOT_APPLIED |
| Does strict non-ZIP64 preflight inspect local headers and extra-field TLVs, not just EOCD and central counts? | [EXT-45 local ZIP64 and extra-field regression](EXT-45-LOCAL-ZIP64-EXTRA-FIELD-PREFLIGHT.md), [issue #13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) | EXT-44 false accepts 3 synthetic noncanonical ZIPs; isolated EXT-45 51/51 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; NOT_APPLIED |
| Can BZIP2/LZMA allocate more decompressed bytes internally than declared ZIP limits or 64 KiB read requests? | [EXT-46 bounded decompression methods](EXT-46-BOUNDED-DECOMPRESSION-METHODS.md), [issue #14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/14) | EXT-45 accepts two synthetic underdeclared ZIPs; isolated EXT-46 STORED/DEFLATE allowlist 54/54 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; NOT_APPLIED |
| Can a ZIP's local header disagree with its central-directory version, flags, compression, CRC or sizes while passing audit? | [EXT-47 local/central header congruence](EXT-47-LOCAL-CENTRAL-HEADER-CONGRUENCE.md), [issue #13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) | EXT-46 accepts six synthetic contradictions; isolated EXT-47 60/60 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; NOT_APPLIED |
| Does ZIP preflight reject inconsistent local-versus-central metadata before ZipInfo parsing? | [EXT-46 local/central header coherence](EXT-46-LOCAL-CENTRAL-COHERENCE-PREFLIGHT.md), [issue #13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) | EXT-45 false accepts nine synthetic header/profile variants; isolated EXT-46 60/60 normal and optimized; 7 ZIPs / 653 hashes PASS_LIMITED; NOT_APPLIED |
| Does every byte before the central directory belong to an indexed local ZIP entry? | [EXT-48 unindexed local-byte coverage](EXT-48-UNINDEXED-LOCAL-BYTE-COVERAGE.md), [issue #13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) | EXT-45 false accepts 5 synthetic orphan/gap/prefix cases; isolated EXT-48 9/9 normal and -O; seven historic ZIPs NOT_RUN; NOT_APPLIED |
| Can distinct EXT-46/47 ZIP profile safeguards be combined without losing EXT-48 byte-layout coverage? | [EXT-49 consolidated profile](EXT-49-CONSOLIDATED-STRICT-ZIP-PROFILE.md), [issues #13/#14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) | Synthetic 35/35 normal and -O; 14 EXT-48 acceptances newly rejected; originals NOT_RUN; NOT_APPLIED |
| Does matching the local/central GPBF suffice to enforce a narrow historical ZIP profile? | [EXT-50 flag policy regression](EXT-50-GENERAL-PURPOSE-FLAGS.md), [issue #13](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/13) | Four synthetic unsupported bit patterns accepted by EXT-49; EXT-50 44/44 normal and -O; originals NOT_RUN; NOT_APPLIED |
| Does a declared DEFLATE output length prove that every byte of the physical compressed stream has been checked? | [EXT-51 stream completeness](EXT-51-COMPLETE-DEFLATE-STREAM.md), [decompression issue #14](https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/issues/14) | Four synthetic EXT-50 false acceptances; EXT-51 48/48 normal and -O; originals NOT_RUN; NOT_APPLIED |
| What exact evidence would allow gate decisions? | [Acceptance contract](../decisions/GATE-13-EVIDENCE-ACCEPTANCE-CONTRACT.md) | PROPOSED_ACCEPTANCE_CRITERIA |
| Why is functional execution still blocked? | [Model M ADR](../decisions/ADR-P0-001-MODEL-M.md) | FROZEN_NO_GO |
