# SEC-02 — Windows synthetic reproduction protocol (DESIGN ONLY)

**Execution status:** NOT_RUN. **Approval to execute:** NOT IMPLIED by this document.

## Objective

Determine whether the synthetic worker in the integrated Darts v0.55 artifact can read a known synthetic file outside its declared project root when launched with the client's actual permissions. Compare against an OS-enforced restriction. Do not inspect real private data or run the audiovisual pipeline.

## Preflight, before any child process

1. Verify SHA-256 of the exact integrated ZIP against `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.
2. Statically inspect the exact Python entrypoints, imports, process creation, environment inheritance, side effects and test fixtures.
3. Record Windows edition/build, PowerShell, Python interpreter path/version, ACLs, process token and directory layout. Redact user-identifying paths from shared logs.
4. Use a dedicated disposable test root and synthetic target, never a personal or project-sensitive file.
5. Establish an **execution environment compatible with the frozen governance gates**. If no such environment can be established, stop at design-only and record NOT_RUN.
6. Predeclare a failure cleanup procedure, and record whether child termination was *actually confirmed*. A timeout, logical FAILED_TERMINAL state or kill request alone is insufficient.

## Test matrix (conditional; no test authorized under incompatible model M)

| Case | Setup | Expected evidence | Conclusion limit |
|---|---|---|---|
| SEC02-01 | Baseline worker under same Windows token; synthetic file outside declared root | Read success or explicit denial; raw process identity and ACL context | One-case permission behavior, not general exploit |
| SEC02-02 | OS-enforced restricted token / sandbox with a separately verified ACL boundary | Access-denied result; child exits and termination confirmed | One-case mitigation, not Policy B compliance |
| SEC02-03 | Restricted environment; relative traversal, environment-controlled path, and symlink/reparse-point variants using synthetic files only | Every attempt and reason for rejection; safe, bounded diagnostics | No proof against all path evasions |

## Independent observations to collect

- Parent PID and real child PID; process token and permissions.
- Exact synthetic fixture SHA-256; relative and absolute fixture placement (redacted in publication).
- Child stdout and stderr **bytes emitted** separately from bytes captured; note that a bounded client queue does not measure emitted bytes.
- Start/finish clock, evidence of child process exit, any survivors and cleanup.
- Full raw test logs and tool versions, with sensitive values redacted.
- Reproduction count and whether the original v0.54 or integrated v0.55 implementation was used.

## Explicit non-claims

- Python `-I`, `cwd`, and environment filtering do not constitute OS filesystem confinement.
- A single Access Denied does not prove comprehensive sandbox safety.
- An ACK/COMMITTED from the worker does not independently prove rendering or state application.
- Process kill request or `wait(timeout=3)` does not establish strict Policy B under arbitrary OS suspension.
- Previously reported 912 frames / 29 tests are not independently reproduced by this protocol.

## Next documentary tasks

- [ ] Map call sites and compare v0.54/v0.55 code with line-anchored evidence.
- [ ] Decide whether a dedicated isolated host is required for safe experimental work.
- [ ] Formally resolve model M vs operational model without silently relaxing Policy B.
- [ ] Run tests only after applicable gates are genuinely satisfied; otherwise retain NOT_RUN.

**Frozen:** E5B4D_NO-GO, RENDER_NO-GO, PUBLISH_NO-GO.
