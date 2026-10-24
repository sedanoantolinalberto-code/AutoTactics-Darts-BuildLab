# GATE-13 — Evidence acceptance contract for Darts v0.55

**State:** PROPOSED_ACCEPTANCE_CRITERIA / NO GATE APPROVED  
**Date:** 2026-10-24  
**Applies to:** v0.55 Integrated SourceOnly SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`  
**Authority:** documentary criteria only; cannot authorize execution, merge, rendering or publication.

## 1. Evidence classes and promotion

| Level | Name | Required evidence | Cannot claim |
|---|---|---|---|
| E0 | PROPOSED | Specification, model and assumptions | Implementation or test result |
| E1 | STATIC_REPRODUCED | Exact source SHA, inspector SHA, method, raw results, repeatable input | Runtime success |
| E2 | FUNCTIONAL_OBSERVED | Executed test, environment inventory, raw stdout/stderr, exit observations, independent reproducer | Universal guarantee |
| E3 | ENVIRONMENT_BOUND | E2 plus independent enforcement evidence and explicit failure model | Guarantee under model M unless proved |
| E4 | FORMAL_GUARANTEE | Reviewed model and proof of every stated invariant under all allowed failures | Any unstated failure mode |
| E5 | HUMAN_GATE_APPROVED | Separate signed/attributable human decision referencing evidence, scope and residual risks | Approval of unrelated gates |

E5 is a governance decision, not a substitute for E4. For the frozen model M, E4 has not been established and E5B4D is NO-GO.

## 2. ACK-02: choose the trust contract before implementation

### Contract A — trusted child, same-boundary receipt

- **Meaning:** ACK means *the trusted worker reports* that `consume` returned; COMMITTED means *the trusted worker reports* that `finish` returned.
- **Minimum evidence:** document worker executable provenance, filesystem/launch control, exact response predicates, code path, process identity check, and explicitly scoped trust assumptions.
- **Negative tests to design:** wrong episode, wrong frame, wrong digest, wrong PID, replay, out-of-order response, correct-looking ACK from a synthetic child that intentionally does not apply state.
- **Prohibited conclusion:** independent attestation, durable storage proof or evidence of externally visible effect.
- **Decision:** Contract A is a viable *description* only if reviewers formally accept the trusted-child assumption; it is **not** a security fix.

### Contract B — untrusted child, independently evidenced effect

- **Meaning:** ACK/COMMITTED are advisory until a separate trust anchor proves the specific claimed effect.
- **Proof obligation:** specify effect, external observer, isolation from child control, freshness, anti-replay binding, immutable evidence and failure handling.
- **Adversarial design:** a compromised child knows signed plaintext and its own PID and can emit correct-looking unsigned responses without applying state. Merely signing those responses with a key held by that same child is insufficient.
- **Decision:** no independent anchor has been verified; **NOT_SATISFIED**.

**Selection required:** a human-reviewed, explicit trust model. Until then ACK-02 remains OPEN; no implicit promotion of the historical 9/9 fake-worker tests.

## 3. Lifecycle and strict Policy B: measurable acceptance predicates

Let `t0` be the start of the operation; let `P` be **all relevant processes**, including descendants; `emitted_s(p,t)` and `accepted_s(p,t)` be lifetime byte totals for stream `s` (stdout or stderr).

Under the frozen model, acceptance requires a reviewed proof that for every allowed execution, **there exists an observation before `t0 + 120s` confirming each relevant process has terminated**; and for each stream the lifetime emitted and accepted totals remain <=1,048,576 bytes, including data generated before an abort, after a limit crossing, and during cleanup. Clarify the accounting domain across parent/child/descendants; do not silently assume only one child or one pipe.

Evidence must distinguish:
- `ABORT_REQUESTED` from `SIGNAL_DELIVERED`, `EXIT_OBSERVED`, and `REAP_CONFIRMED`;
- output **emitted**, **accepted by OS/pipe**, **read**, and **retained**;
- wall-clock deadline from per-read timeout, blocking stdin writes, or worker-reported completion;
- nominal-case observation from all-case guarantee under arbitrary OS suspension.

**Counterexample to ordinary timeout approach:** model M permits suspending all relevant scheduling and observation before the deadline. Therefore a parent-side `wait(timeout=...)`, watchdog, bounded queue, or `kill()` request alone cannot establish the stated universal predicate. E5B4D remains NO-GO; no finite battery of passing synthetic tests changes that result.

## 4. Negative-case evidence packet (future, NOT_RUN)

Each test record must contain `case_id`, `source_sha256`, `harness_sha256`, `os_build`, `python_parent`, `python_child`, `cryptography_version`, `failure_model`, `start_monotonic`, `deadline`, `parent_pid`, `child_pid`, `descendant_pids`, `exit_observed`, `reap_confirmed`, `stdout_emitted`, `stdout_accepted`, `stderr_emitted`, `stderr_accepted`, `capture_truncated`, `raw_log_sha256`, `cleanup_observation`, `verdict`, and `verdict_scope`. Unknown measurements must be null, not guessed from captured bytes.

No tests may be executed under the current frozen governance. This schema is an **evidence specification**, not an executable harness or claim that OS-level emitted-byte counters already exist.

## 5. Traceability / decision ownership

| Gate | Current status | Required decision or evidence | Owner of decision |
|---|---|---|---|
| ACK-02 | OPEN | Select trusted/untrusted child contract; provide matching proof | Human security/governance review |
| HELLO-01 | PROPOSED_NOT_APPLIED | Review PID consistency patch; test under permitted model | Code reviewer |
| TEST-ENV-01 | PROPOSED_NOT_APPLIED | Review exception-safe restore; test under permitted model | Test reviewer |
| TERM-01 / STDIN-01 | OPEN | Physical lifecycle, blocking-write and cleanup evidence | Runtime/security reviewer |
| STDOUT/STDERR | OPEN | Separate emitted/accepted lifetime ceilings, enforcement | Runtime/security reviewer |
| SEC-02 Windows | NOT_RUN | Explicitly approved isolated synthetic experiment; OS boundary proof | Security reviewer |
| E5B4D | FROZEN_NO_GO | Formal proof under M or separately authorized changed model | Governance owner |
| RENDER / PUBLISH | NO_GO | Independent higher-gate approval, rights and quality | Human owner |

## 6. Stop rule

Further documentary research should be prioritized only if it produces new, falsifiable evidence or resolves a specific open proof obligation. Repackaging the same findings into more files is not progress. No status upgrade or production action may follow from this document alone.

**Cross-references:** `P0-ACK-12-TRUST-BOUNDARY.md`, `P0-TERM-06-LIFECYCLE-PROOF-OBLIGATIONS.md`, `P0-TEST-11-INDEPENDENT-COVERAGE.md`, `ADR-P0-001-MODEL-M.md`.
