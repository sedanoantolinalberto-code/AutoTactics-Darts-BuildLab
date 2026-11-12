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
