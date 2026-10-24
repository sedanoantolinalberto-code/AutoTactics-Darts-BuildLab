# P1-GRAPH-04 — Static AST import and function-signature analysis

**Date:** 2026-10-24  
**Evidence:** STATIC_REPRODUCED (local Python `zipfile` + `ast.parse`, no Darts modules imported or executed).  
**Input:** 21 S34 source ZIPs v0.35–v0.55 (integrated v0.55, not ReviewOnly).

## Reproduction anchors

- Script: `EngineYT_Darts_P1_Static_Dependency_Graph_2026-10-24.py`, SHA-256 `5f7e464482434805d5f000a3c7ba29b9ba342a38f393f9c61db5ca02e1a7e7a0`.
- Complete JSON: `EngineYT_Darts_P1_Static_Dependency_Graph_2026-10-24.json`, SHA-256 `2b14f6982f3ac9b4b35a036d6f3a82d2ea87b43ad074b56fec9dd4f76ea61963`.
- Human-readable report: `EngineYT_Darts_P1_Static_Dependency_Report_2026-10-24.md`, SHA-256 `5d8807aa881fc1fa71094612c32a843b5501da59c42aebf968802f8e55d22812`.
- The full source ZIPs and complete JSON are retained externally to this branch; this file is an anchored summary.

## Results

| Metric | Value |
|---|---:|
| Source ZIPs | 21 |
| Python members outside `baseline_`/`upstream_` prefixes | 166 |
| Python members in historical folders | 244 |
| Import statements matching active modules in same ZIP | 293 |
| Import statements matching modules only in historical folders | 286 |
| Total heuristic internal-name matches | 579 |
| Function/method definitions examined, with version repeats | 2324 |
| Python AST parse errors | 0 |
| Exact cross-line function AST signatures | 2 |
| Exact cross-line nontrivial signatures (>=12 AST nodes) | 0 |

The two shared signatures are generic methods `__enter__` (6 AST nodes) and `__exit__` (10 AST nodes), seen in `source_only/s34_v038_durable_verifier.py` and `public_process_client_v054.py` / `public_process_client_v055.py`. These matches do not establish code lineage or a shared runtime dependency.

## Source-anchored architecture observations

- **Research v0.35–v0.43:** `source_only/` imports both sibling S34 research modules and module names present in `upstream_v031/`. In v0.43, `source_only/s34_v043_nested_cleanup.py` imports `s34_v040_source_chain_probe`, `s34_v041_terminal_session` and `s34_v042_exhaustive_terminal`.
- **Public consumer v0.44–v0.55:** v0.49 `public_frame_fanout.py` imports verified HUD/camera/audio modules; v0.53 `public_episode_session_v053.py` references baseline public modules; v0.54 adds `process_wire_v054.py` and `public_process_client_v054.py`; v0.55 uses `public_process_client_v055.py`.
- **Important caveat:** v0.55's worker is launched by `subprocess.Popen` from `baseline_v054/`, not imported by the parent client. The worker modifies `sys.path` explicitly to reach nested baseline modules. A simple import graph is incomplete without process/path edges.

## Limitations and required next control

These are **name-based candidate import edges**, not verified runtime resolution. Dynamic import, `sys.path` manipulation, subprocess and local package structure can alter the actual graph. A zero exact-function match beyond trivial functions does not rule out conceptual reuse, renamed implementations or transformed code.

Next control: capture the `Popen` path, worker `sys.path` setup and process lifecycle as an explicit static process-edge trace. Do not execute source code.

**Gates unchanged:** E5B4D_NO-GO, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO. No merge to main.
