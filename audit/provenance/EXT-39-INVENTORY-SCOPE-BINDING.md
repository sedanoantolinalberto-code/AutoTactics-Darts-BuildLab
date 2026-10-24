# EXT-39 — Seven-version inventory scope binding and 30-case consolidated regression

**Date:** 2026-10-24. **Status:** PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Two confirmed false-acceptance cases in EXT-38

1. A seven-entry inventory containing **seven references to the same v040 ZIP** returned `PASS_LIMITED`, reporting seven archives and **686 member checks** despite representing one unique historical version.
2. Relabeling v040 as `version: 999` returned `PASS_LIMITED`, reporting a nonexistent version 999 and 653 member checks.

A third test substituting a cross-version target script was **already rejected by EXT-38** and is retained as a control, not a new defect. These are **scope/reporting integrity defects**, not a demonstrated SHA-256 collision, forgery or execution vulnerability.

## EXT-39 isolated candidate

Validates before verification: seven unique integer versions **40, 41, 42, 43, 50, 52, 53**; seven unique archive basenames; consistent `vNNN` token across each archive, target script and embedded manifest name. No historical ZIP or original manifest is changed. Structural consistency cannot authenticate attacker-supplied hashes or custody.

## Reproducible observed results

| Candidate | Passed | Total | Explanation |
| --- | ---: | ---: | --- |
| EXT-38 | 28 | 30 | False acceptance: repeated v040 and fictitious version 999 |
| EXT-39 | **30** | **30** | All previous and new cases |
| EXT-39 with `python -O` | **30** | **30** | Harness now propagates `-O` to verifier subprocesses |

Historical baseline **7/7 original ZIPs, 653/653 manifest member SHA-256 matches PASS_LIMITED**. No Darts modules imported or executed; independent verifier and synthetic inputs only.

## Evidence

`EngineYT_Darts_EXT39_Inventory_Scope_Evidence_20261024.zip` SHA-256 **`467575ce04a59bb7defe53d8161b161f0e439f49d42403ea1d132b82141eaad6`**; eight files; ZIP CRC and package member SHA-256 checks PASS.

Candidate SHA-256 **`668b209da2ea22342335320d3e158010821c25080d24b3c112fba4d971b19d94`**. Consolidated harness SHA-256 **`8068b82a891955423bbb3d2351c41f645945b9458c0703c36201786d64c99a75`**. Historical ZIPs not redistributed in the package.

## Open gates

Independent provenance anchors absent; POSIX-specific; Windows SEC-02 NOT_RUN. No physical OS process termination guarantee under arbitrary suspension model M. **E5B4D_NO-GO, ACK-02 OPEN, RENDER_NO-GO, PUBLISH_NO-GO**. No main merge or production integration; candidate NOT_APPLIED.
