# OPT-30 — Minimal source-preserving hardening and manifest coupling

**Date:** 2026-10-24. **Evidence:** STATIC_AST_AND_COMPILE_PASS. **Status:** PROPOSED_NOT_APPLIED / NOT_RUN.

## Why OPT-30

[OPT-29](P1-OPT-29-UNAPPLIED-ASSERT-HARDENING.md) replaced 51 asserts across seven historical Python scripts, but AST unparse introduced substantial unrelated formatting churn. OPT-30 produces a minimal, source-preserving textual replacement for the **same 51 assertions**, preserving comments and docstrings and making review tractable.

A second, previously unregistered integration hazard was independently verified: **all seven original scripts are listed with exact SHA-256 values in their own historical version manifests**. A direct edit would invalidate those manifests. Rewriting historical manifests would change their bytes and potentially invalidate later ancestry claims. Historical ZIPs and manifests must remain immutable; a separately versioned revision and reviewed provenance chain would be needed.

## Seven exact source-to-manifest bindings

| Version | Original script | Manifest key | Assert replacements |
|---|---|---|---:|
| v040 | `VERIFY_V040.py` | `MANIFEST_V040_SHA256.json.files` | 2 |
| v041 | `VERIFY_V041.py` | `MANIFEST_V041_SHA256.json.files` | 3 |
| v042 | `VERIFY_V042.py` | `MANIFEST_V042_SHA256.json.files` | 3 |
| v043 | `VERIFY_V043.py` | `MANIFEST_V043_SHA256.json.files` | 3 |
| v052 | `VERIFY_V052.py` | `MANIFEST_SHA256_V052.json.sha256` | 3 |
| v053 | `VERIFY_V053.py` | `MANIFEST_SHA256_V053.json.sha256` | 4 |
| v050 | `test_v050.py` | `MANIFEST_SHA256_V050.json.source_sha256` | 33 |

Each original ZIP hash and manifest entry was compared to its actual member bytes before drafting. Total 51 transformations. v050's ineffective `assert __debug__, 'PYTHON_OPTIMIZATION_NOT_ALLOWED'` is replaced by unconditional `if not __debug__: raise RuntimeError('PYTHON_OPTIMIZATION_NOT_ALLOWED')`. Its one-line `with ...: assert` and semicolon-separated `assert ...; negative.append(...)` were expanded with preserved outer-suite semantics.

## Static checks and exact package

- Diff: **219 lines** of per-file unified diff content, compared with the 507 lines reported for OPT-29; no unrelated whole-file AST unparse.
- For each candidate: `ast.dump(candidate, include_attributes=False)` exactly matches the expected AST after only the specified assert-to-if transformation.
- Every candidate has zero AST `assert` nodes, compiles in memory at `optimize=0` and `optimize=1`, and preserves original comment tokens.
- Seven original source-manifest SHA-256 bindings PASS. ZIP CRC and member SHA-256 checks PASS.
- Package `EngineYT_Darts_OPT30_Minimal_Source_Preserving_Package_20261024.zip`, SHA-256 `a71fb26945178e8ed82d5cfa80c82cbc0f29a439fe1c071db3783667e0eb2f75`, **12 files**: seven candidate sources, offline source-only builder, unified diff, JSON inventory, technical review and manifest.
- Technical review `EngineYT_Darts_OPT30_Minimal_Diff_Review_20261024.md`, SHA-256 `17ce847387987e1f0cd5e8f7c0da1067735882d22e3da0f1464ec462a07d2b80`.

## Remaining acceptance gates

1. Independently review semantic intent, Python compatibility and each diff. AST structural equivalence does not prove runtime equivalence.
2. Decide whether to issue a separately versioned, explicitly new provenance chain; **do not overwrite old manifests or historical ZIPs**.
3. Review possible use of an external trusted verifier against immutable old ZIPs as a less intrusive alternative to modifying historical source.
4. Any functional execution requires separate governance clearance. No Darts code was imported or executed in this audit.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** No changes to main or production sources.
