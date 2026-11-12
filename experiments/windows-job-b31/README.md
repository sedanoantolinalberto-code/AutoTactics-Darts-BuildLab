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
