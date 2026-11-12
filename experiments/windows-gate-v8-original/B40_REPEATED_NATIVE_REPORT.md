# Engine YT — B40: original V8 repeated native campaign (REVIEW ONLY)

**2026-11-12. NO MERGE / NO RELEASE / NO PRODUCTION GO.**

This is a stability campaign of **the original 17 B23–B25 Gate V8 scenarios**,
executed with the **exact minimal B39 Win32 null-HANDLE fix**. It does not
replace the Python supervisor or the B23 source.

## Provenance and test identity

Original archive: `EngineYT_B23_B25_ReaderLaunch_GateV8_ReviewOnly_20261111.zip`;
SHA-256 `97f9be37e506d5343f0d6d779803a9f5560a3cf2be8a97a2fb73589410ace56d`.
Verified locally: 50/50 manifest files; original Linux regression 162/162 PASS.
The CI workflow reconstructs and SHA-verifies all original 11 Python runtime modules,
then applies the exact known B39 one-function patch only to
`windows_joblist_launcher._handle_value` (preimage
`b0ebd62ea68821dd93560ea39cc0ca91841f1c50eb4dc279f85b2f26a6a66237`,
postimage `51885aa5b2417b877affdc0a440c6431a0d155063aa5a2f0c15f5e747c964f6c`).

## GitHub Actions evidence

Run: **43226320336**, Python **3.12.10**, Windows Server 2022/2025,
NTFS. The workflow executes all 17 cases **three times per OS**, and invokes
unmodified B25 against each JSON report.

| OS | Job ID | Repetitions | Unique scenarios | Total executions | Gate exit | B25 exit |
|---|---:|---:|---:|---:|---:|---:|
| Windows Server 2022 | 131210317526 | 3 | 17 | 51 PASS | 0 / 0 / 0 | 0 / 0 / 0 |
| Windows Server 2025 | 131210317904 | 3 | 17 | 51 PASS | 0 / 0 / 0 | 0 / 0 / 0 |

Both GitHub jobs: **SUCCESS**. Full stdout was inspected, with six
`Ran 17 tests` blocks, six `B40_REPETITION_RESULT` receipts and
`B40_RESULT THREE_REPEATS_SEVENTEEN_PER_HOST_PASS_LIMITED`.
**102 case executions passed; 17 distinct test scenarios**. The repeated
iterations must not be misrepresented as 102 unique test cases.
Full report JSONs and runner logs are stored as GitHub Actions
artifacts with 30-day retention.

## Boundaries

- Original unmodified launcher B38 was **NO-GO** on both Windows runners
  (6 PASS, 2 FAIL, 9 ERROR). B39 patch is **mandatory**.
- B25 establishes consistency of claimed results with supplied sources,
  not independent identity/provenance of the runner.
- No Windows 11 desktop or user Windows 10/11 execution, power-loss
  resilience, full descendant containment, external custodian or
  production supervisor qualification.
- R17/E5B4D remains **NO-GO**; TB09/G3 **BLOCKED**;
  full containment **BLOCKED**; rendering and publishing disabled.

Links:
- B40 PR: https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/pull/20
- CI: https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/actions/runs/43226320336
- Exact minimal fix B39: https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/pull/18
