# EXT-42 — Synthetic provenance-anchor substitution: consistency is not authenticity

**Date:** 2026-10-24. **Status:** SYNTHETIC_REPRODUCED / PASS_LIMITED / INDEPENDENT_PROVENANCE_NOT_ESTABLISHED. **Darts runtime:** NOT_RUN.

## Reproduced trust-boundary distinction

A standalone standard-library harness operates exclusively on temporary copies of the seven immutable source-only historical ZIPs. It appends an inert comment to `VERIFY_V040.py` in the copied v040 ZIP, updates that copy's `MANIFEST_V040_SHA256.json`, and recomputes the copied archive SHA-256 and corresponding copied inventory target hashes. Original ZIPs and original inventory are **not modified**; the synthetic modified copies are deleted on completion and are not distributed.

| Inputs to independent EXT-41 verifier | Result |
| --- | --- |
| Original seven ZIPs and original OPT-30 inventory | **PASS_LIMITED**, seven ZIPs / 653 manifest members |
| One modified v040 ZIP, **original unchanged inventory** | **FAIL**, `ARCHIVE_HASH_MISMATCH` |
| Same modified ZIP, **coherently updated temporary inventory** | **PASS_LIMITED**, seven ZIPs / 653 manifest members |

Normal and `python -O` runs return identical result objects.

**Original v040 ZIP SHA-256:** `7cb1b8c3ee16a5f123aa291e953b49b033d39a6b180a66170110bef6a3d97922`.
**Synthetic altered v040 ZIP SHA-256:** `2a88e0f793e24f42c45a3193c7f70602ee69e2a475a6d57555fcdb96becef4b1`.
**Original target SHA-256:** `871db8d1d78162100299b72d0d61fbd9e929ddc13fd4f489f0e9634b6a5d0b48`.
**Synthetic altered target SHA-256:** `773a17154b16cd907812e4b0e3b62c8e233f0e77b6813989992c79a4a52f3b62`.

This **does not** demonstrate a SHA-256 collision or a defect in internal consistency checking. It proves that attacker-controlled source data and attacker-controlled reference hashes can agree while lacking independently attested historical authenticity.

## Reproducible evidence

`EngineYT_Darts_EXT42_Provenance_Trust_Boundary_Evidence_20261024.zip` SHA-256 `c37be45f9e37ecf65a2e691225d90b6111dd0adb832f47b0350cb87bd2b2a266`; six members, ZIP CRC and package SHA-256 manifest verified. Includes reproducible standalone synthetic probe, normal and optimized JSON outputs, unchanged OPT-30 inventory, review and package manifest. **Does not bundle altered historical ZIPs or altered inventory.**

## Specific open proof obligation

To elevate the seven-ZIP result above PASS_LIMITED, obtain an **independently authenticated original anchor** for each historical ZIP and establish its signer/issuer, custody, version identity, and integrity at the relevant historical time. A separate repository file or issue copying the same SHA-256 is not independent authentication. Acceptable paths require independently verifiable signatures, trustworthy archived release attestations, or an independently controlled custody record with demonstrable historical binding. No such independent evidence has been verified here.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** No Darts project code imported or executed, no project tests, workers, render, publication, production integration or main merge.
