# EXT-32 — Exhaustive bounded external verifier (seven immutable historical ZIPs)

**Date:** 2026-10-24. **Result:** PASS_LIMITED. **Darts runtime:** NOT_RUN. **Integration:** NOT_APPLIED.

The independently authored Python verifier reads seven original source-only ZIPs v040/v041/v042/v043/v050/v052/v053 without importing or executing Darts code. It checks each complete ZIP SHA-256 against the exact OPT-30 inventory anchor, enforces unambiguous manifest schema, requires **exactly complete manifest coverage**, streams and hashes every non-manifest member, and verifies the targeted historical script-to-manifest binding.

**Observed:** seven of seven archives PASS, **653 non-manifest members SHA-256 matched**. CRC checked during member reads. Original ZIPs and their manifests unchanged.

## Resource and archive constraints

- 16 MiB maximum ZIP input; 512 entries; 2 MiB per member; 32 MiB total uncompressed; 100:1 maximum declared compression ratio; 512 KiB manifest/inventory.
- Reject duplicate names, traversal or absolute member names, encrypted entries, ambiguous mapping dictionaries, non-64-hex digest strings, incomplete or surplus manifest coverage, oversized or corrupt decompressed members.
- Resource caps are **not** physical process-termination guarantees under failure model M.

## Negative cases

Eight synthetic, temporary ZIP-only cases **8/8 PASS**: repacked baseline, mutated member with updated outer ZIP anchor, missing member, extra member, duplicate ZIP name, traversal name, oversized member, and wrong outer SHA-256. The negative harness constructs synthetic ZIPs and runs only the independent verifier, not the project or its tests. **SEC-02 remains NOT_RUN.**

## Evidence

`EngineYT_Darts_EXT32_Exhaustive_Archive_Evidence_20261024.zip`, SHA-256 `9fcb0e077dccd52f26c66e25fd1617b10c49fb48df0c781e8b085b5cf62f8f6a`. Seven files: verifier, original OPT-30 inventory, results JSON, synthetic negative-test harness, negative results JSON, technical review and SHA-256 package manifest. ZIP CRC and manifest checks PASS.

## Limitations and next gate

The supplied inventory anchors are not independently authenticated: coherent attacker-controlled ZIP and inventory may pass. No external signing key, attested custody, or trusted publication channel is available. No claims of historical runtime success, commercial rights, or Policy B compliance. Further independent code review and pathological ZIP input tests remain open.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** No production code modification, main merge, Darts worker execution, render or publication.
