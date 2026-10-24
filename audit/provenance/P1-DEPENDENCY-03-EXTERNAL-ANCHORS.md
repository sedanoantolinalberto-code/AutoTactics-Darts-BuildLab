# P1-DEPENDENCY-03 — External source ZIP anchors and README references

**Date:** 2026-10-24  
**Class:** STATIC_REPRODUCED (local read-only SHA-256 and README scan)  
**Execution:** no Darts modules, tests, renderer or subprocess executed.

## External source ZIPs actually present in the audit workspace

| Artifact | Bytes | Computed SHA-256 | Expected | Result |
|---|---:|---|---|---|
| `EngineYT_Darts_Sprint31_TriProxy_TruthSafeHUD_v0.1_COMPLETO(1).zip` | 107181797 | `90b6c76ed795f38a1a9a808b83234fedb9fbe5e179c36c445266c07c7bd52b16` | same | PASS |
| `EngineYT_Darts_S34_v034_FrameBoundary_SourceOnly_PRIVATE.zip` | 344650 | `96bd0262526a64ff791ebfcb40fe65e07a40bf7e2ac990e59011837effe5c127` | same | PASS |

These are **external package anchors**, not evidence that any downstream test or media pipeline was run. The S31 ZIP is ~103 MiB; it was streamed in chunks for SHA-256 without extraction or execution.

## README reference inventory, v0.35–v0.55

- 21 archives scanned; use `README_Vxxx.md` where present (v0.37–v0.43), otherwise `README.md`.
- **21/21** selected READMEs mention S31.
- **19/21** selected READMEs mention v0.34 or v034.
- **8/21** selected READMEs reproduce the full expected S31 SHA-256.
- **6/21** selected READMEs reproduce the full expected v0.34 SHA-256.

This is a **textual reference audit**, not a complete code dependency graph. A README lacking an explicit hash is not proof of an absent dependency. Explicit package labels `SOURCE ONLY` and `NOT INTEGRATED` are documentation claims, not executable guarantees.

## Reproduction artifacts

- Script `EngineYT_Darts_P1_External_Anchors_2026-10-24.py`, SHA-256 `54d85999c1ada27783edb2eb8bf384e44b33f8b8487943bd030a910b643b86ce`.
- Full JSON `EngineYT_Darts_P1_External_Anchors_2026-10-24.json`, SHA-256 `e162de535edee5680ca402d50064d125dc3e3778c6eafc66cac14789c69260f1`.

## Remaining evidence requirements

- [ ] Construct a source-level import/call dependency graph for each line without executing modules.
- [ ] Link precise source paths and lines for any claim of shared code between research v0.35–v0.43 and public consumer v0.44–v0.55.
- [ ] Preserve full JSON and script in controlled archive for independent review.
- [ ] Keep the original S31 and v0.34 ZIPs outside Git until sensitivity and licensing review.

**NO-GO unchanged:** E5B4D, render, publication. SEC-02 Windows functional reproduction NOT_RUN.
