# GATE-14 — Minimal evidence requests and reviewer handoff

**Date:** 2026-10-24  
**State:** READY_FOR_DOCUMENTARY_REVIEW / NO-GO UNCHANGED  
**Scope:** Darts v0.55 Integrated SourceOnly SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.  
**Inputs reviewed:** `ADR-P0-001-MODEL-M.md`, `GATE-13-EVIDENCE-ACCEPTANCE-CONTRACT.md`, `open-findings.v0.1.json`, `P0-ACK-12-TRUST-BOUNDARY.md`, `P0-TERM-06-LIFECYCLE-PROOF-OBLIGATIONS.md`.

## Minimal reviewer questions, in dependency order

### RQ-01 — Failure model (blocking; no execution)

**Question:** Is the project's original Policy B under arbitrary OS suspension model M still the required safety property?  
**Current binding answer:** **YES**. No alternative model, experimental exception, or revised guarantee is approved.  
**Evidence needed for a change:** attributable governance decision stating the revised model, exact guarantees, scope, residual risks and authority.  
**Until then:** E5B4D=NO-GO; no Darts functional execution, worker launches, renderer, release or publication.

### RQ-02 — ACK-02 trust semantics (reviewable without execution)

**Question:** Does an ACK mean a *trusted child's self-report* or independently attested state application?  
**Current state:** UNDECIDED.  
**Minimum answer:** select Contract A or B in GATE-13, define precise state transition and adversary control; document which claims are excluded.  
**Current safe interpretation:** ACK and COMMITTED are protocol-consistency signals from the worker; independent effect attestation NOT_PROVEN.  
**Do not treat** an Ed25519 signature on parent messages as independent authentication of child output.

### RQ-03 — Process termination and output budgets (blocking)

**Question:** What component, outside an arbitrarily suspended parent/worker, can guarantee and confirm exit of every relevant process strictly before t0+120s? What enforces and measures emitted AND accepted bytes independently for stdout/stderr over lifetime?  
**Current answer:** NONE VERIFIED.  
**Evidence needed:** a formal mechanism/proof under model M; exact process domain, accounting semantics, adversarial schedule, observer liveness and confirmation path.  
**Stop rule:** timeout/kill/wait/bounded Queue/buffer are not acceptable substitutes.

### RQ-04 — Windows SEC-02 OS boundary (not yet executable)

**Question:** What token, ACL, job object, sandbox and filesystem policy confines the worker to the intended resources?  
**Current answer:** NOT VERIFIED; synthetic marker access is a historical test-design observation, not an independently reproduced Windows outcome.  
**Evidence needed:** static OS launch/permission design first, then separately approved Windows experiment only if RQ-01 permits it.

### RQ-05 — Two low-scope hardening diffs

**Question:** Do code reviewers accept (a) comparing HELLO PID with `self.p.pid`, and (b) restoring the preexisting `DARTS_V055_PROBE_PATH` in `finally`?  
**Current state:** PROPOSED_NOT_APPLIED; candidate Python AST syntax checked; no functional tests.  
**Acceptance needed:** source review, change ownership and future permitted test protocol; no silent edits to historical ZIPs or main.

## Evidence request template

For each control, reviewers should return one record:

```json
{
  "control_id": "ACK-02",
  "decision": "UNDECIDED",
  "evidence_class": "E0",
  "source_sha256": "3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105",
  "evidence_refs": [],
  "reviewer_identity": null,
  "review_timestamp_utc": null,
  "assumptions": [],
  "scope": "Darts v0.55",
  "residual_risks": [],
  "gate_effect": "NONE"
}
```

The example is a **schema illustration**, not a real reviewer approval. Unknown values must remain null. Evidence levels and gates are separate; a reviewer signature does not manufacture missing E4 guarantees.

## Recommended sequencing

1. Preserve model M and existing NO-GO.
2. Request a scoped human review of ACK-02 semantics; no implementation required to decide terminology.
3. Have runtime/security reviewer assess the impossibility result and whether a *new, separately approved* model is ever warranted; do not assume such a change.
4. Have code reviewer assess two small hardening diffs, still NOT_APPLIED.
5. Only after explicit gate changes, define permitted functional test environments; do not run now.
6. Keep main, historical ZIPs, renderers and publication untouched.

**This handoff requests decisions; it does not make them.**
