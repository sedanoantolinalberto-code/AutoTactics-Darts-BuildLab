# Engine YT — B31 Native Windows Job Object Probe

**REVIEW ONLY / NO MERGE / NO RELEASE / NO PRODUCTION.**

This is a **new complementary native probe**, *not* the original B23–B25 Windows Gate V8.
The B23–B25 ZIP was not accessible in the local runtime; do not count the 17 V8 cases as executed.

Four tests:
1. Configure only KILL_ON_JOB_CLOSE, no breakaway flags; verify Job handle is not inheritable.
2. Create a disposable Windows PowerShell child with CreateProcessW and PROC_THREAD_ATTRIBUTE_JOB_LIST; inspect association while suspended; resume; close final job handle; verify child termination.
3. Duplicate the Job handle, close first handle, confirm child still alive; close final handle, confirm termination.
4. Use a nonexistent executable path; ensure CreateProcessW fails without leaving a process.

All test children are owned by the runner and are terminated in finally. The runner has no publishing secrets, writes no release output and has read-only GitHub permissions.
This does not establish full descendant containment, crash survivability, filesystem durability, platform compatibility or Engine YT Gate V8 acceptance.

Require GitHub Actions logs, commit and outcomes before reporting any PASS.
Gates R17/E5B4D NO-GO, TB09/G3 BLOCKED, rendering/publication disabled.

## B32 — native results verified

The B31 prototype was extended with three new adversarial Windows scenarios:

- `suspended-child-killed-before-resume`: confirm Job closure terminates a child never resumed.
- `descendant-after-parent-exit-killed-by-job`: grandchild stays in Job after its parent exits, then terminates when Job is closed.
- `abrupt-custodian-death-kills-owned-child`: terminate the isolated custodian without cleanup; its owned child terminates as the last Job handle is closed.

**Verified CI: Windows Server 2022 / x64 / .NET 8**

- Baseline B31 run: `43136560568`, job `130913203266`: **4/4 PASS**.
- Expanded B32 run: `43136982647`, job `130914574856`: **7/7 PASS**.
- Commit under test for expanded run: `3b40d22a822662c092c19307d3868dff0cd04854`.
- Logs inspected directly, including final `B31_RESULT pass=7 fail=0 total=7`. No skipped or synthetic cases represented as native tests.

**Scope limitation:** This is not B23–B25 Gate V8, not a qualification of all 17 V8 cases, and not evidence about Linux or supervisor code in T21-R09. There is no automatic promotion and no release authority.

To reproduce from this branch:

```powershell
dotnet run --project experiments/windows-job-b31/WindowsJobProbe.csproj --configuration Release
```

Use disposable Windows environment (CI or an isolated machine); the program starts and terminates only its own child processes. Avoid manual production deployment.

## B33 — native continuation, 2026-11-12

Complementary Windows reference test cases:

- `explicit-breakaway-denied-by-job-policy`: inside the configured Job, a child requests `CREATE_BREAKAWAY_FROM_JOB`. The test requires a denial and a recorded Win32 error, not a successfully detached process.
- `twenty-atomic-creation-close-repetitions`: 20 serial iterations with atomic Job association, `ResumeThread`, last-handle close and termination of the owned process.

Verified GitHub Actions: run `43141038835`, job `130927798701`, test commit `b9a86f45771ccfb4c8307500ae96672637476bf4`. Windows Server 2022 native job completed **SUCCESS**, log reports `B31_RESULT pass=9 fail=0 total=9 scope=native-windows-probe-not-gate-v8`.

Evidence interpretation: **9/9 independent reference scenarios**, including 20 repetitions within one scenario, **not 29 separate test scenarios**. The 17 original B23–B25 Gate V8 scenarios remain **0/17 executed** and the original supervisor is not qualified by these reference tests.

No code changes outside this review-only branch; no release, render or publish permission.


## B34–B36 — identity and handle hardening, 12 November 2026

All changes are limited to this disposable Windows reference experiment.

- **B34**: a Job handle deliberately marked inheritable does not cross
  \`CreateProcessW\` when \`bInheritHandles=false\`. An invalid Job handle
  causes launch rejection, not successful unsupervised execution.
- **B35**: a PID read from a marker file is **not authorization to terminate
  the process**. The verifier opens the intended Job and requires
  \`IsProcessInJob(candidate, expectedJob)\` before keeping a
  termination-capable process handle. A separate test supplies the PID of an
  unrelated, directly owned control process; the verifier rejects it without
  killing the control. The verifier's extra Job handle is closed **before**
  the custodian is killed, so it cannot mask \`KILL_ON_JOB_CLOSE\` behavior.
- **B36**: a named Job that already exists causes a fail-closed rejection.
  The test deliberately reuses a newly generated name and requires denial.
- A matrix now runs the entire suite on **windows-2022** and
  **windows-2025**, both with x64 and .NET 8.

### Evidence

- 11-scenario baseline B34 on both versions: GitHub Actions
  \`43147146817\`, **11/11 PASS** in each job.
- Final B36 source commit: \`d1483edab01c8e373d1cd85d4cc772bf6fe18ac8\`.
- GitHub Actions run \`43147759478\`: Windows 2022 job
  \`130949476989\`, **13/13 PASS**; Windows 2025 job \`130949477333\`,
  **13/13 PASS**. Both completed SUCCESS with 0 FAIL.
- **13 distinct scenarios**, executed once on each platform
  (**26 successful scenario executions**). The 20 inner repetitions of one
  scenario do not increase the scenario count.
- Structured receipt: \`B36_NATIVE_EVIDENCE.json\`.

### Qualification boundaries

These tests do **not** establish authenticated or tamper-proof origin of a
marker in production; they reject a PID outside a named Job in this test
harness. Named Job security descriptors, other principals, nested Jobs,
simultaneous custodian failures, distributed recovery and real Engine YT
supervisor code require additional testing.

The **original 17-scenario Windows Gate V8 remains 0/17 executed** here
because its B23–B25 source package is not present in the accessible GitHub
repository/session. No gate, publication or release status changes.

## B37 — six simultaneous independent Jobs, final reference result

- New native scenario: `six-concurrent-independent-jobs`. It constructs six
  independent Jobs and checks isolated child lifetime behavior under
  overlapping execution. It is **one scenario**, not six new unique tests.
- Verified GitHub Actions run `43148437966`, exact test source commit
  `843a2cfbdb92d1446db9742519f0b6522c741846`.
- Windows Server 2022 job `130951681601`: **14/14 PASS**,
  stdout `B31_RESULT pass=14 fail=0 total=14 scope=native-windows-probe-not-gate-v8`.
- Windows Server 2025 job `130951681923`: **14/14 PASS**,
  same bounded receipt. **28 reference scenario executions** over
  **14 distinct scenarios**, zero recorded FAIL.
- Structured receipt: `B37_NATIVE_EVIDENCE.json`.

**Chronological clarification:** The original B23–B25 Gate V8 package
was absent when B31–B37 were developed. It was independently recovered
and exercised **later**, with the precise B39 null-HANDLE fix, in the
separate review-only PR #18 and repeated in PR #20: **17 original cases
three times per Windows 2022/2025 runner = 102 native case executions
PASS LIMITED**. This is a *different codebase and test suite* and is
**not** evidence that B31–B37 executed those original V8 cases.

No change to R17/E5B4D NO-GO, TB09/G3 BLOCKED or full descendant
custody BLOCKED. No production integration, merge, release or publishing.
