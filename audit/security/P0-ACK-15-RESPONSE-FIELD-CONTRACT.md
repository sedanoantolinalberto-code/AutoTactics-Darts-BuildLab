# P0-ACK-15 — Worker response-field validation matrix

**Date:** 2026-10-24  
**Status:** STATIC_REPRODUCED / NOT_RUN. New field-level finding distinct from ACK-02.  
**Source:** immutable `EngineYT_Darts_S34_v055_BoundedStdout_Integrated_SourceOnly_PRIVATE.zip`, SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## Exact source evidence

The worker emits:
- `baseline_v054/isolated_public_worker_v054.py:36`: HELLO has `type,v,nonce,episode,pid`.
- `baseline_v054/isolated_public_worker_v054.py:56–60`: ACK has `type,episode,frame,remaining,camera_role,overlay_phase,subtitle,cue,head,pid`.
- `baseline_v054/isolated_public_worker_v054.py:65–66`: COMMITTED has `type,episode,frames,intent_count,head,pid`.

The parent checks:
- `public_process_client_v055.py:74–79`: HELLO's five field names are referenced (this does **not** mean exact schema/type validation; e.g. `v == 1` is an equality check).
- `public_process_client_v055.py:125–132`: ACK's `type,episode,frame,head,pid`; it returns the complete response dictionary to caller.
- `public_process_client_v055.py:134–149`: COMMITTED's `type,episode,frames,head,pid`; it returns the complete response dictionary to caller.
- `baseline_v054/process_wire_v054.py:36–45`: `decode` checks canonical JSON and that the result is a dictionary; it does **not** enforce a message-specific field schema.

## Newly confirmed gap: ACK-03

| Message | Worker-emitted fields | Parent-referenced fields | Fields not specifically checked |
|---|---:|---:|---|
| HELLO | 5 | 5 | None by name; exact schema still unverified |
| ACK | 10 | 5 | `remaining`, `camera_role`, `overlay_phase`, `subtitle`, `cue` |
| COMMITTED | 6 | 5 | `intent_count` |

The parent does not enforce exact response key sets; a syntactically valid response may include additional keys. For ACK, five presentation fields are returned to the caller without specific value/type validation in `send()`. For COMMITTED, `intent_count` is not specifically checked in `finish()`.

**Security interpretation:** under a compromised-child assumption, a structurally acceptable ACK can carry arbitrary extra/presentation fields; whether downstream consumers use them unsafely is **NOT VERIFIED**. Under a trusted-child assumption, the omission is still a contract robustness gap. This does not prove a production exploit or establish that shipped worker outputs invalid data.

## Reproducibility anchors

- Read-only Python AST inspector: `EngineYT_Darts_P0_ACK_Response_Field_Inventory_2026-10-24.py` SHA-256 `816f5a045297217f868ccc0bc5261171de03dff07fc1e015bd1225b8adb0e2c9`.
- Full JSON output: `EngineYT_Darts_P0_ACK_Response_Field_Inventory_2026-10-24.json` SHA-256 `72ea890ee8980d92333c3726eb1b659ce7f2d7cf2b6cc8e59e6b57708d528279`.
- Inspector reads two Python members with `zipfile`, parses them using `ast`, enumerates emitted literal dictionary keys and `response.get(...)` / `response[...]` references. It does **not** execute project code. Field reference is a conservative proxy for inspection, **not** proof of semantic validation.

## Proposed acceptance criteria (NOT IMPLEMENTED)

1. Specify exact allowed keys for HELLO/ACK/COMMITTED and reject unknown or missing keys.
2. Specify strict types, string length and allowed enumerations/ranges for `remaining`, `camera_role`, `overlay_phase`, `subtitle`, `cue` and `intent_count`; validate cross-field consistency against the known public episode state.
3. Distinguish *schema acceptance* from *independent evidence of application*; fixing ACK-03 does not fix ACK-02.
4. Draft individual negative cases for each unvalidated field, extra keys, missing keys, wrong types, noncanonical nonce and `HELLO.v=True`; tests remain **NOT_RUN** under frozen governance.
5. Review any proposed implementation separately, preserve original ZIPs and main.

**Gates unchanged:** E5B4D_NO-GO, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO. No production code modified.
