# P0-TIMEOUT-25 — NaN bypasses v0.55 read deadline

**Date:** 2026-10-24. **Evidence:** STATIC_REPRODUCED_AND_STDLIB_SEMANTICS_ONLY. **Darts execution:** NOT_RUN.  
**Source ZIP SHA-256:** `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## Confirmed source-level defect

`public_process_client_v055.py:23` rejects a `timeout` only when `timeout <= 0 or timeout > 30`. For `float('nan')`, both comparisons are false, so the constructor can proceed to `Popen`.

In `PublicChild._read()`, `deadline=time.monotonic()+self._timeout` (line 92) and `remaining=deadline-time.monotonic()` (line 99) stay NaN. `remaining<=0` (line 100) never becomes true, while `min(0.025,remaining)` (line 101) returns 0.025 on the inspected CPython interpreter.

**Conditional outcome:** if the child stays alive and silent and neither EOF nor reader failure occurs, the parent may poll indefinitely instead of raising `CHILD_TIMEOUT`. This is **not** a runtime reproduction of a hung Darts worker. It is a static control-flow finding plus six independently evaluated Python standard-library float expressions.

The same constructor guard and read-deadline structure occur in six **unapplied** proposals ACK-18 through ACK-23. All seven source versions were AST-parsed and checked against exact line locations. Source ZIP and all candidate source SHA-256 values are in the JSON evidence.

## Reproducible evidence package

- `EngineYT_Darts_P0_TIMEOUT25_Static_Inspector_20261024.py` SHA-256 `e33f277f5a83cf2d6d5ee68a6b502c70ba94eb85abab2271313cf27c924dbd9b`.
- `EngineYT_Darts_P0_TIMEOUT25_Static_Evidence_20261024.json` SHA-256 `2fecd09e1d7af3fd9ebdab757527c573321bbd2b6a80eb0495d0da18039540df`.
- `EngineYT_Darts_P0_TIMEOUT25_Review_20261024.md` SHA-256 `fb231af38b7c442a87a51399a756391f32daa42c3cb3d9c306add785b8f67ca1`.
- `EngineYT_Darts_P0_TIMEOUT25_Static_Evidence_Package_20261024.zip` SHA-256 `2cc5008afd87f2e7c92442c6d6acd9fc2b9b01acb48ecd3b4ea1e1a9d197f72e`, 4 files, ZIP CRC and member SHA-256 checks PASS.

The inspector **does not import or execute project code**, start a child, or run project tests. Its only executable semantic checks use ordinary `float`, `math.isnan`, comparisons and `min`.

## Narrow mitigation (NOT_APPLIED)

Validate the numeric type and finite positive range **before** `Popen`. Example (type policy requires compatibility review):

```python
import math
if (type(timeout) not in (int, float)
        or not (0 < timeout <= 30)
        or not math.isfinite(timeout)):
    raise ProcessRejected('INVALID_EPISODE_OR_TIMEOUT')
```

This example rejects bool and non-builtin numeric types; a reviewer must decide whether that is compatible with supported callers. The essential invariant is finite, positive and <=30.

## Negative-case plan (NOT_RUN)

NaN; positive and negative infinity; zero, negative and >30; bool/nonnumeric per approved type contract; valid finite 0.15/8/30; alive-silent worker only after separate execution authorization.

**No governance change:** E5B4D_NO-GO, SEC-02 Windows NOT_RUN, ACK-02 OPEN, RENDER_NO-GO, PUBLISH_NO-GO. Fixing NaN does not establish strict Policy B under arbitrary OS suspension or lifetime emitted/accepted byte limits. No runtime patch or merge to main.
