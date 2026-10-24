# EXT-43 — Original historical ZIP custody-source discovery

**2026-10-24 | LOCAL_ANCHOR_AGREEMENT_7_OF_7 | INDEPENDENT_ATTESTATION_NOT_OBTAINED | PASS_LIMITED**

## Reproducible cross-report check

Seven original ZIP SHA-256 values for v040, v041, v042, v043, v050, v052, v053 agree **7/7** with the OPT-30 inventory and all three earlier local static audit reports (25ZIP independent bytes, P1 static inventory, architecture/branch audit). A standard-library read-only comparator confirms the exact local ZIP bytes; normal and `python -O` results are byte-identical. **All four reports derive from the same locally supplied ZIPs**; their agreement is reproducibility, not an independent historical attestation.

## Connected evidence discovery and its limits

- **Two connected Gmail accounts:** exact v040 ZIP name and attachment-filename queries yielded no matching messages. A broader project-name query found one GitHub Actions failure notification in one account; no original ZIP hash attestation.
- **Connected Google Drive:** searches for `EngineYT_Darts`, `AutoTactics`, `S34`, `v040` returned no accessible matches.
- **GitHub private Darts BuildLab default-branch code search:** exact v040 SHA-256, manifest name and archive-name token returned no matches. Main commit search returned no `v040` or `manifest` message matches. Branch-name search found no v040/source-named branch.
- **Project/Library file search:** earlier local audit records reproduce v040 hash; these are not independently controlled attestations.

**Negative results apply only to these exact queries and indexed surfaces.** GitHub releases, Actions artifacts, all branch content, offline stores, external archival services, unindexed data and other accounts were not exhaustively examined. No claim of global absence.

## Evidence package

`EngineYT_Darts_EXT43_Custody_Source_Discovery_20261024.zip` SHA-256 **`8d9aa2337b060e484b79561f0da92bd75ef9d9c5576f6e9b389f90b363b0c70f`**, nine members, ZIP CRC and member SHA-256 manifest PASS. Includes executable read-only cross-report comparator, normal and optimized results, detailed search-scope report, four local input reports, and package manifest. Original seven ZIPs are **not** redistributed.

## Gate

Issue #12 remains **OPEN**: require independently controlled and verifiable original seven-archive SHA-256 anchors or signatures with issuer, historical time and custody validation. A new signature over today's local hashes does not retroactively prove 2026-10-21 origin.

No Darts modules, workers, tests, renders, publication, or main merge. **E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**
