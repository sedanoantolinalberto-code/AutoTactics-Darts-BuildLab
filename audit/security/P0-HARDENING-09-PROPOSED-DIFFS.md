# P0-HARDENING-09 — Unapplied v0.55 hardening patch candidates

**Status:** PROPOSED_NOT_APPLIED / NOT_RUN.  
**Date:** 2026-10-24.  
**Source ZIP SHA-256:** `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## Reproducibility

- Generator `EngineYT_Darts_P0_Hardening_Patch_Proposal_2026-10-24.py`: SHA-256 `f0b426ed5afed9e7a5b97ae1c226d42aed7a804d4f183b0e397d84f0bbf0c7d9`.
- Proposed unified diff `EngineYT_Darts_P0_Hardening_Patch_Proposal_2026-10-24.diff`: SHA-256 `4d28a8931a090ac1ea7abbdb38f8c0ac70c7a0e3be9395802d97cf64eae2be49`.
- Metadata `EngineYT_Darts_P0_Hardening_Patch_Proposal_2026-10-24.json`: SHA-256 `aed6c857dde5cc64b2904b1ee297530adb559ce52a303bcd25d5e36a3898f53e`.
- Generator requires each original snippet to occur exactly once and calls `ast.parse` on both source and candidate. **Both candidate files parsed successfully.** No Darts module imported or executed.

## Candidate A — HELLO-01

`public_process_client_v055.py:76`, add a local PID consistency condition:

```diff
-                type(hello.get('pid')) is not int or hello['pid']==os.getpid() or
+                type(hello.get('pid')) is not int or hello['pid']==os.getpid() or hello['pid']!=self.p.pid or
```

This rejects a HELLO whose claimed PID differs from the process object created by `Popen`. It is **not** cryptographic process attestation or a sandbox.

## Candidate B — TEST-ENV-01

In `test_transport_v055.py`, preserve the preexisting synthetic probe variable before the `try` and restore it inside the existing `finally`:

```diff
         old_mode=os.environ.get('DARTS_V055_FAKE_MODE')
+        old_probe=os.environ.get('DARTS_V055_PROBE_PATH')
         client.ROOT=root
@@
-            os.environ.pop('DARTS_V055_PROBE_PATH',None)
             os.environ['DARTS_V055_FAKE_MODE']='slow_hello'
@@
         finally:
             client.ROOT=original_root
+            if old_probe is None:os.environ.pop('DARTS_V055_PROBE_PATH',None)
+            else:os.environ['DARTS_V055_PROBE_PATH']=old_probe
             if old_mode is None:os.environ.pop('DARTS_V055_FAKE_MODE',None)
```

This avoids environment leakage after an exception and restores any original value. It changes only synthetic test-harness hygiene.

## Evidence and acceptance gates

| Control | Status |
|---|---|
| Exact original snippets found once | PASS (static) |
| Candidate AST syntax | 2/2 PASS (static) |
| Source code patched in ZIP or Git | NO |
| Fake-worker negative tests run | NOT_RUN |
| Windows functional tests | NOT_RUN |
| E5B4D / Policy B | NO-GO |
| Renderer / publication | NO-GO |

**Required before implementation:** explicit review of the two source diffs; preserve historical ZIP immutability; only execute negative tests if separate governance gates permit. No claim of functional success, security certification, or approval to merge.
