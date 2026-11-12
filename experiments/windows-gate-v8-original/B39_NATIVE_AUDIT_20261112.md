# Engine YT — Original Windows Gate V8: B38 vs B39 (REVIEW ONLY)

**Date:** 2026-11-12. **NO MERGE / NO RELEASE / NO PRODUCTION GO.**

## Provenance

Original user-supplied package: `EngineYT_B23_B25_ReaderLaunch_GateV8_ReviewOnly_20261111.zip`.
Package SHA-256: `97f9be37e506d5343f0d6d779803a9f5560a3cf2be8a97a2fb73589410ace56d`.
Independent local ZIP CRC + manifest verification: **50/50 files PASS**.
Unmodified package on Linux/Python 3.13: **162/162 PASS**; Windows launcher
is intentionally blocked on non-Windows. The original **11 runtime source files**
were reconstructed in CI only after an XZ payload SHA-256 and all 11 per-file
SHA-256 hashes matched the supplied package.

## B38 — Original unmodified launcher: NO-GO (verified native)

- GitHub Actions: run **43221816576**.
- Windows Server 2022 and 2025; Python **3.12.10**.
- Original Gate V8: **6 PASS / 2 FAIL / 9 ERROR** on EACH host.
- Root cause reproduced on both: `windows_joblist_launcher._handle_value`
  calls `int(None)` when `HANDLE().value` is null in cleanup.
- B25 evidence checker correctly **rejected** both non-PASS reports.

## B39 — Minimal one-function repair: PASS LIMITED

Source changes made only to a verified, isolated runtime copy; B38 original
bytes remain untouched. Exact preimage SHA-256
`b0ebd62ea68821dd93560ea39cc0ca91841f1c50eb4dc279f85b2f26a6a66237`
becomes
`51885aa5b2417b877affdc0a440c6431a0d155063aa5a2f0c15f5e747c964f6c`.

```diff
-        return int(h.value if hasattr(h, 'value') else h or 0)
+        value=h.value if hasattr(h, 'value') else h
+        return int(value or 0)
```

- Original Linux regressions after this change: **162/162 PASS**.
- First native patched run `43222272500`: **17/17 PASS** on both hosts,
  B25 rejected because executing the script directly labelled cases
  `__main__.WindowsGateV8`.
- Final patched run **43222548271** uses `import windows_gate_v8;sys.exit(windows_gate_v8.main())`
  to retain canonical `windows_gate_v8.WindowsGateV8` case identities.
  The underlying 17 tests and B25 verifier source were **not modified**.
- Windows Server 2022, job `131197444089`: **17/17 PASS, 0 FAIL/ERROR/SKIP,
  NTFS, Python 3.12.10**, Gate exit 0, B25 exit 0.
- Windows Server 2025, job `131197444391`: **17/17 PASS, 0 FAIL/ERROR/SKIP,
  NTFS, Python 3.12.10**, Gate exit 0, B25 exit 0.
- B25 final verdict, both hosts:
  `SELF_REPORTED_WIN_V8_CONSISTENT_NOT_ATTESTED`.
- Native evidence ZIPs: artifacts `13947045090` (2022) and
  `13947160008` (2025).
- The ZIPs were downloaded, CRC-checked, and their JSON files reverified
  independently against the locally patched source with the unmodified
  B25 implementation. **2 real reports accepted; 2 test-ID-forged copies rejected.**

## Boundaries

**Not attested:** B25 validates internal report/source consistency, not the
identity of the independent executing host. Windows Server 2022/2025 is not
equivalent to a qualified Windows 11 desktop/NTFS environment. This test does
not prove custody under sudden supervisor crash, simultaneous failures,
host power loss, PID reuse outside the tested scenarios, or full Linux cgroup
v2 delegated containment. All production changes remain absent.

**Status:** `PASS_LIMITED_WINDOWS_SERVER_NATIVE_B39`. The **original B38
unmodified launcher remains NO-GO**, and R17/E5B4D **NO-GO**, TB09/G3
**BLOCKED**, descendant containment **BLOCKED**, render/publishing false.

## References

- B38 original draft PR: https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/pull/17
- B39 review-only draft PR: https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/pull/18
- Final native run: https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/actions/runs/43222548271
