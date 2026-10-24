# DOC-README-01 / P1-LINEAGE-02 — S34 v0.35–v0.55 source-archive analysis

**Date:** 2026-10-24  
**Evidence class:** STATIC_REPRODUCED (read-only ZIP metadata and decompressed-file SHA-256; no project code executed)  
**Status:** DOCUMENTARY FINDING / NO RELEASE GATE CHANGE.

## Inputs and reproducibility anchors

- 21 original S34 ZIPs v0.35–v0.55, with v0.55 **Integrated SourceOnly**, excluding ReviewOnly.
- Local read-only inspector: `EngineYT_Darts_P1_Architecture_Branch_Audit_2026-10-24.py`, SHA-256 `69ecc1875df8d53119c6f17fc0836a86f2c55ecbf93070a7014cf6365289831a`.
- Full machine-readable results: `EngineYT_Darts_P1_Architecture_Branch_Audit_2026-10-24.json`, SHA-256 `885e6e3b0ec292b88f4fc9f26520fe9a101dd00fb4718072876faaf8a0b78537`.
- Full human-readable report: `EngineYT_Darts_P1_Architecture_Branch_Report_2026-10-24.md`, SHA-256 `da1e3b390cfb009c6420fbc672fea7eebabf5140f92937a3ff979c5226621328`.
- Method: Python stdlib `zipfile`, `hashlib`, and regex parsing of the first nonblank line of root `README.md`; exact SHA-256 intersection of all uncompressed members in adjacent ZIPs. No imports from the ZIPs, no tests, workers, renderers, media or network.

## DOC-README-01 — Stale root README in seven archives

Root `README.md` in **v0.37, v0.38, v0.39, v0.40, v0.41, v0.42 and v0.43** is byte-identical to root `README.md` in v0.36 and retains its v0.36 heading. SHA-256 of each of those eight identical root files: `e34b1696a8f5` (prefix; use the full audit JSON for the 64-character digest).

Each v0.37–v0.43 ZIP contains its own `README_V037.md` through `README_V043.md` as appropriate. This is a navigation/documentation discrepancy, not evidence that those version-specific READMEs are inaccurate.

**Remediation (PROPOSED):** create a non-destructive index pointing to the version-specific README, without rewriting or repacking any historical ZIP. If a future package is made, use a root README identifying the actual version.

## P1-LINEAGE-02 — Separate archive research lines

**Research line v0.35–v0.43:** mailbox spike, public wire contract, offline signatures, durable replay, dual-ledger rollback, authenticated admission, terminal cleanup and nested SQLite cleanup. README_V043 explicitly describes source-only, not integrated research.

**Public consumer line v0.44–v0.55:** authentic parity, public HUD/camera/audio interfaces, frame fanout, detached call sites, episode sessions, signed subprocess transport and bounded stdout queue.

The exact SHA-256 content overlap across all uncompressed members of **v0.43 vs v0.44 is 0**. Zero overlap also occurs for adjacent v0.44→v0.45, v0.45→v0.46 and v0.46→v0.47. These are **content intersection observations**, not proof that concepts, algorithms, original S31 sources or design were never shared. Do not claim a byte-preserving ZIP inclusion chain through the v0.43→v0.44 transition.

In contrast, v0.49→v0.55 has separately verified nested byte-preserving baselines (22, 33, 43, 55, 66, 76 matching members respectively); these are ZIP containment, not Git commit ancestry.

## Action register

- [x] Audit root README version headings across v0.35–v0.55.
- [x] Confirm the v0.36 root README is retained unchanged through v0.43.
- [x] Identify per-version README files for v0.37–v0.43.
- [x] Compare SHA-256 content intersections of 20 adjacent archive pairs.
- [ ] Create a detailed dependency matrix against the exact S31 and v0.34 inputs.
- [ ] Verify any claimed reuse between lines by specific source paths/lines, not by version number.
- [ ] Link full audit outputs to an independent archival location without committing sensitive source ZIPs.
- [ ] Review/approve any documentation-only change to main separately.

**Unchanged gates:** E5B4D_NO-GO, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO. No main merge.
