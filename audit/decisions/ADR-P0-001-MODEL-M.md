# ADR-P0-001 — Security model M versus executable validation

**State:** PROPOSED / NO CHANGE TO EXISTING POLICY  
**Date:** 2026-10-24  
**Owner approval:** not a substitute for satisfying technical guarantees.

## Decision context

The project has a frozen E5B4D decision: `STRICT_GUARANTEES_INCOMPATIBLE_UNDER_STATED_MODEL`. Under failure model M (arbitrary operating-system suspension), the strict Policy B guarantees cannot be derived from ordinary process timeouts, `kill()`, `wait()`, bounded capture queues, Windows ACLs, or AppContainer alone.

Policy B requires **all relevant processes** terminated and termination **confirmed strictly before 120 seconds**, and independent lifetime stdout/stderr budgets of **1,048,576 bytes emitted and accepted per stream**.

## Options (none accepted by this ADR)

**A — Retain M and strict Policy B:** Keep executable testing NO-GO; continue documentary/static audits only. This is the current frozen posture.

**B — Define a separate, weaker operational model:** Requires explicit, separate governance approval and precise scope. Must never be represented as passing the original model M.

**C — Develop a different trusted execution/monitoring architecture:** Must demonstrate formal guarantees under a clearly stated model, including behavior during suspension and confirmation. Merely moving to another OS or sandbox is insufficient.

**D — Run tests on a dedicated synthetic-only host as an exploratory exception:** Requires an explicitly approved, separately scoped safety exception. Results would be experimental observations, not proof of strict Policy B under M. No such exception is approved by this ADR.

## Immediate decision

- Choose **A for now**, as the only option consistent with frozen constraints.
- SEC-02 functional Windows matrix remains **NOT_RUN**.
- Prepare test plans and isolate static evidence; no renderer, publication, project child processes or main merge.
- Do not convert `FAILED_TERMINAL`, ACK/COMMITTED, or a timeout into proof of process exit or application.
- Human gate required for any change of safety model or production status.

## What would change this decision?

A separately reviewed governance artifact that explicitly states the new failure model, guarantees, residual risks, exact scope and authorizing party; or a demonstrated architecture that satisfies the original model. Until then, all higher gates stay closed.
