# P1-IMPORT-08 — Exact static worker import closure in v0.55

**Status:** STATIC_REPRODUCED, no Darts code executed.  
**Date:** 2026-10-24.  
**Source:** `EngineYT_Darts_S34_v055_BoundedStdout_Integrated_SourceOnly_PRIVATE.zip` SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## Reproduction anchors

- Script `EngineYT_Darts_P1_Worker_Reachability_Static_2026-10-24.py` SHA-256 `e6dc2b9e559dad4bd6d676bc6290d8e0314b5d57d3277322dc3f3fcf3e6989de`.
- JSON `EngineYT_Darts_P1_Worker_Reachability_Static_2026-10-24.json` SHA-256 `2004f9c36e3964981cfaa6d8694b373c41076e65074670a3e0cb0cac1bfe2fa7`.
- Markdown report `EngineYT_Darts_P1_Worker_Reachability_Report_2026-10-24.md` SHA-256 `fd5422720e4071e25f9844f60e0619fcce89f4b9e5434e7dc20cbce5b53b5443`.
- Method: `zipfile` and `ast.parse` over exact ZIP bytes; simulate `sys.path.insert(0, p)` precedence and follow literal Python imports from `baseline_v054/isolated_public_worker_v054.py`. No source extraction, imports, child processes or renderer.

## Results

| Observation | Result |
|---|---:|
| Reachable worker modules in static import closure | 8 |
| Internal import edges | 11 |
| External import edges | 16 |
| Name collisions in the six worker search directories | 0 |
| Python AST parse errors | 0 |
| Direct calls matching the inspector's `eval/exec/__import__/subprocess/socket/os.system/importlib.import_module` list | 0 |
| Detached historical renderer copies in the archive | 5 |
| Detached renderer present in worker's static import closure | No |
| Top-level `process_wire_v054.py` identical to worker's `baseline_v054/process_wire_v054.py` | Yes |

Protocol copy SHA-256: `0a96762fda7003f997d1e6f11757d3064873de57e38b24451b671f77d8a12fe5`.

## Worker static import closure

1. `baseline_v054/isolated_public_worker_v054.py`
2. `baseline_v054/process_wire_v054.py`
3. `baseline_v054/baseline_v053/public_episode_session_v053.py`
4. `baseline_v054/public_receiver.py`
5. `baseline_v054/baseline_v053/baseline_v052/baseline_v051/baseline_v050/baseline_v049/public_hud_verified_v049.py`
6. `baseline_v054/baseline_v053/baseline_v052/baseline_v051/baseline_v050/baseline_v049/public_camera_overlay_verified_v049.py`
7. `baseline_v054/baseline_v053/baseline_v052/baseline_v051/baseline_v050/baseline_v049/public_audio_metadata_verified_v049.py`
8. `baseline_v054/baseline_v053/baseline_v052/public_audio_intent_collector_v052.py`

## Interpretation

The five `detached_src/render_safehud_s31safe.py` files are present in the **source ZIP** but not found in the worker's **static import closure**. They contain historical renderer logic; their presence is a packaging/review consideration, not evidence of execution. This is a narrow positive finding for the intended worker entrypoint, **not** proof of sandbox confinement or no possible dynamic side effects.

The worker explicitly changes `sys.path`; the reverse of the literal insertion list determines lookup priority. No filename collisions were found in those six directories. Third-party dependencies, runtime import hooks, nonliteral imports, and other entrypoints are outside this model.

The byte-identical protocol copies reduce one potential source of divergence but do not authenticate worker ACKs independently. The strict E5B4D and Policy B incompatibility is unaffected.

## Follow-up

- [x] Resolve lexical import graph under worker `sys.path` ordering.
- [x] Check module-name collisions and protocol byte equality.
- [x] Separate historical renderer presence from worker import reachability.
- [ ] Review third-party dependency provenance and runtime behavior without claiming execution.
- [ ] Decide whether detached renderer code should be distributed in future isolated consumer packages; do not alter historical ZIPs.
- [ ] Require separate governance approval before any functional execution, rendering, publication or merge to main.

**Gates:** E5B4D_NO-GO, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO.
