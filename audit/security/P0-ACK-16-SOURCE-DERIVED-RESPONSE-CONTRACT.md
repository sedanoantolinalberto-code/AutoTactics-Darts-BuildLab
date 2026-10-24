# P0-ACK-16 — Source-derived strict response contract (proposal)

**Date:** 2026-10-24. **Evidence:** STATIC_REPRODUCED for source extraction; PROPOSED_NOT_APPLIED for validation rules.  
**Exact source ZIP:** `EngineYT_Darts_S34_v055_BoundedStdout_Integrated_SourceOnly_PRIVATE.zip` SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.  
**No project code executed.**

## Independent extraction and results

Read-only inspector `EngineYT_Darts_P0_ACK16_Contract_Extractor_20261024.py` SHA-256 `e452508812ee77318575332db7e95e7ee9444261f5305113f10bab7718ba79bc`, using `zipfile` and `ast.parse` on eight source files.

- JSON inventory `EngineYT_Darts_P0_ACK16_Contract_Inventory_20261024.json` SHA-256 `32b8f1b05274067e5bac6526bd53165e436b4c59074b6c8fa8197d12c8eb9cfe`.
- Full report `EngineYT_Darts_P0_ACK16_Contract_Report_20261024.md` SHA-256 `f3dbe4716e42d11f7fe7bad766865274cf7867c2fdfa7cdb53502c597f20b745`.
- ZIP `EngineYT_Darts_P0_ACK16_Source_Derived_Contract_20261024.zip` SHA-256 `7e12cdfa0317023ac5836277807d7bb7a03e260c52ac6c9466355a9066fff8e2`, ZIP CRC and all member SHA-256 checks PASS.

## Candidate field-level schema — grounded, not applied

| Field | Source-derived permitted values / shape | Grounding |
|---|---|---|
| `camera_role` | `AIM_LOCK`, `CONTEXT_WIDE`, `ESTABLISH`, `IMPACT_CUT`, `IMPACT_HOLD`, `RETURN_WIDE` | `public_camera_overlay_verified_v049.py:12–18,77–89` |
| `overlay_phase` | `END`, `EXPLAIN`, `HOOK`, `IMPACT PENDING`, `NEW_VISIT`, `OBSERVED IMPACT`, `REPLAN` | same module, lines 12–18 and 77–89 |
| `cue` | null or `SOFT_IMPACT`, `BUST_IMPACT`, `CHECKOUT_IMPACT` | `public_audio_metadata_verified_v049.py:13,94–112`; `public_audio_intent_collector_v052.py:11,76–85` |
| `subtitle` | string, and editorial equality to current-frame template when relevant | `PublicHUDSnapshot.subtitle: str`; `public_hud_verified_v049.py:85–95` |
| `remaining` | exact integer; equality to trusted public state when available | `PublicHUDSnapshot.remaining: int`; `public_episode_session_v053.py:144–147` |
| `intent_count` | exact integer in [0, frames], and equality to independently known manifest count when available | `public_audio_intent_collector_v052.py:86–106`; `test_v055.py:115–117` |

Episode frame counts are D-15=480, D-16=432 (`public_episode_session_v053.py:21`).

**Important:** dataclass annotations are not runtime type checks; exact enumerations alone do not establish semantic correctness; no ungrounded range for `remaining` or string-length limit for `subtitle` is imposed. `PublicChild.send` references five of ten ACK fields and `finish` five of six COMMITTED fields; both return the complete response. Historical `test_v055.py:105–117` checks presentation fields against a reference session, but those checks are **outside the client** and were not executed in this review.

## Two separate proof obligations

1. **Schema-level validation:** exact key sets, exact types, allowed enumerations, and defensible limits. This can reject malformed child messages but cannot prove state application.
2. **Semantic independent validation:** verify the six response fields against a trusted reference or independent observer. This requires a separate trust-model decision (ACK-02) and cannot be obtained by simply trusting the child to attest to itself.

## Twelve negative-case designs (ALL NOT_RUN)

ACK16-01 unknown camera role; ACK16-02 unknown overlay phase; ACK16-03 arbitrary cue; ACK16-04 non-string subtitle; ACK16-05 boolean remaining; ACK16-06 string remaining; ACK16-07 negative intent count; ACK16-08 intent count greater than frame count; ACK16-09 missing presentation field; ACK16-10 extra key; ACK16-11 syntactically valid but semantically wrong field; ACK16-12 well-formed ACK without applying `session.consume`.

The first ten concern schema; ACK16-11 requires an independent semantic reference; ACK16-12 remains ACK-02 and is not fixed by a schema.

**Status:** all candidate changes NOT_APPLIED; all tests NOT_RUN; E5B4D_NO-GO, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO; main and original ZIPs unchanged.
