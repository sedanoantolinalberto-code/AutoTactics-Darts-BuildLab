# Engine YT — B41: custody safety review (STATIC-ONLY / NO EXECUTION)

**Status:** REVIEW ONLY · NO MERGE · NO RELEASE · NOT ATTESTED · 2026-11-13.

This branch contains an AST-only source screen and its own synthetic tests.
**No Claude B10-4 WIP bytes are in this public repository**, and this
work neither runs nor modifies any of Claude's Python launchers.

## Trigger incident / evidence classification

According to the user's relayed Claude report, B10-4 WIP accepted
\`custody_flags = 1 << 40\`. Passing these unchecked values through
\`ctypes\` to a C 32-bit integer may truncate to zero; the following
\`unshare(0)\` can succeed without creating a new PID namespace. The
init then executed \`kill(-1, SIGKILL)\` while still in the environment's
existing PID namespace, affecting processes outside its intended test
scope and causing a restart.

This is a **reported reproduced incident**, not directly reproduced or
verified from WIP bytes here. **Never attempt to recreate it on a shared
host, ordinary CI runner or production instance.** The full incident
analysis and remediation belong in an independently reviewed private
candidate.

## Architectural safety findings

- \`unshare(CLONE_NEWPID)\` changes the PID namespace for **subsequently
  created children**, not the calling process. The first child becomes
  the new namespace's PID 1. A successful return from \`unshare\` or
  \`getpid() == 1\` alone is **not a custody proof**.
- The kernel sends SIGKILL to remaining members when the init (PID 1) of
  a PID namespace terminates. This is preferable to manually sending
  \`kill(-1)\`, but only if the namespace identity and external
  containment are independently established.
- A parent/creator PID, an expected namespace identity, \`/proc\`
  semantics, PID reuse and descendants with \`setsid\` require testing
  from **outside** the candidate under test. Self-reported receipt data
  are not external attestation.

Kernel references:
https://man7.org/linux/man-pages/man7/pid_namespaces.7.html
https://man7.org/linux/man-pages/man2/unshare.2.html
https://man7.org/linux/man-pages/man2/kill.2.html

## Failing-closed acceptance criteria for any later native experiment

| ID | Requirement | Current status |
|---|---|---|
| B41-C01 | No mass-signal primitive such as kill(-1) reachable; guard source plus independent review | UNVERIFIED |
| B41-C02 | Independent outer PID + mount namespace in disposable VM/isolated runner, created and checked **before** WIP starts | UNVERIFIED |
| B41-C03 | Externally pinned identity of intended inner namespace; distinguish creator's \`pid_for_children\` from current \`pid\` | UNVERIFIED |
| B41-C04 | Non-coercing exact CLONE_NEWPID flag check, no int32 overflow, no \`unshare(0)\` fallthrough | REPORTED BY CLAUDE, NOT AUDITED |
| B41-C05 | Fail closed before \`ready\` unless child is PID 1 of **that exact** namespace | UNVERIFIED |
| B41-C06 | Independent control process confirms it remains alive and unaffected after candidate failure | UNVERIFIED |
| B41-C07 | Demonstrate daemon actually ran, creates descendant outside session, and is killed or held as BLOCKED | UNVERIFIED |
| B41-C08 | Test sender identity, PID namespace lifetime, thread-death race, PDEATHSIG loss after privilege change | UNVERIFIED |
| B41-C09 | No mutation test or native destructive test outside externally verified isolation; test-id provenance and full logs archived | UNVERIFIED |
| B41-C10 | Unknown capability, mount, proc or namespace => BLOCKED; cannot turn SKIP/ERROR into PASS | REQUIRED |

No item is automatically marked PASS merely by passing B41 scanner.

## What B41 scanner does and doesn't do

The \`b10_static_screen.py\` script statically parses source text. It flags
literals \`kill(-1)\`, \`kill(0)\`, \`killpg(-1/0)\`, \`unshare(0)\`,
flags outside 32-bit range, suspect \`ctypes.c_int\`/\`c_uint\`
narrowing and dynamic \`unshare(flags)\` for review. It refuses symlinks,
nonregular files, and oversized source files.

It **cannot** prove these properties under runtime conditions, resolve
arbitrary ctypes indirect calls, verify that an inner namespace is real,
or authenticate the producer. A report with zero findings must always be
called \`STATIC_SCREEN_NO_FINDINGS_NOT_QUALIFIED\`; it is **not** a go
signal for native tests. The workflow executes only synthetic unit
fixtures: no WIP modules are imported, no root privileges, no
\`unshare\`, no \`fork\`, no signal probes.

Safe offline command on source **in a restricted, read-only environment**:

\`\`\`shell
python3 b10_static_screen.py /path/to/disposable/source-tree
\`\`\`

Do NOT run the candidate with this command. It only reads candidate
source bytes, and is not a substitute for human review.

## Additional independent work while Claude finishes B10-4

1. Review observed full source/commit differences and controls once a
   verified B10-4 package exists; do not copy unverified WIP into this
   public repository.
2. Keep B39/B40 original Windows Gate V8 evidence independent: Windows
   Server 2022/2025 **102/102 executions of 17 original scenarios**
   were PASS LIMITED; Windows 11 desktop remains unqualified.
3. PR #16 synthetic reference F1/F2/F3 cross-audit ended with
   **187/187** lab checks; real T21 provenance and full descendant
   containment remain BLOCKED.
4. Preserve R08 five FAIL per user-reported R11/B10 matrices; keep
   \`BLOCKED_EXIT_STATUS\` and inspect any new schema consumer failures.
5. Move to independently authenticated custody and provenance only
   after static review, external isolation and a non-destructive
   threat model. Do not invent attestations.

**Gates unchanged:** R17/E5B4D=NO-GO; TB09/G3=BLOCKED;
integral descendant containment=BLOCKED; render/publish disabled.
