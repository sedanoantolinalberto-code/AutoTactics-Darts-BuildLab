# P0-ACK-12 — Trust-boundary proof for ACK/COMMITTED

**Date:** 2026-10-24  
**Evidence:** STATIC_REASONING_ONLY. No worker or Darts code executed; no exploit reproduced.  
**Input:** v0.55 Integrated SourceOnly ZIP, SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.  
**Detailed standalone analysis:** `EngineYT_Darts_P0_ACK02_Trust_Boundary_Proof_2026-10-24.md`, SHA-256 `c91bb5beb1ea96d54b45ab093877b26a30ba55c79a4b41c858b73e65b179e5ea`.

## Trust boundaries grounded in source

- `public_process_client_v055.py:27–34`: parent passes its public key to a launched child, communicating over stdin/stdout.
- `public_process_client_v055.py:108–115`: parent signs each outbound body; reads an unsigned child response.
- `baseline_v054/process_wire_v054.py:47–61`: `digest(body)` is deterministic SHA-256 of canonical JSON; `seal` signs parent-to-child data, `open_seal` verifies it.
- `baseline_v054/isolated_public_worker_v054.py:41–67`: shipped worker verifies incoming messages and emits ACK after `session.consume`, COMMITTED after `session.finish`.
- `public_process_client_v055.py:125–131,134–149`: parent validates response type, episode, frame/count, digest and claimed child PID; FINISH also checks child exit code zero.

## Conditional counterexample (no code executed)

**Assume** an adversary controls the child process and its stdout, can read the incoming signed message's plaintext body, and knows its own PID. For FRAME body `B`, the child can construct an ACK with:

```
type = ACK
episode = B.episode
frame = B.frame
head = SHA256(canonical_JSON(B))
pid = actual_child_pid
```

Those fields satisfy the parent's observable ACK predicate without independently proving that `session.consume` ran. For FINISH body `C`, a similarly controlled child can emit `COMMITTED` with `frames=C.frame`, `head=digest(C)`, `pid=actual_child_pid`, then exit zero without externally proving `session.finish`.

**Scope:** this is a protocol trust-model counterexample under a *compromised child* assumption. It does not establish an attacker can actually replace the shipped worker, that the shipped worker is malicious, or that any forgery has occurred. Parent-to-child Ed25519 signatures do not make child-to-parent responses independently attested.

## Design decisions pending

1. If the child is trusted, label ACK/COMMITTED as same-boundary confirmation only.
2. If the child is untrusted, require externally verifiable evidence of application or an independently protected trust anchor; merely having the same child sign its own response is insufficient.
3. Review executable provenance and filesystem protection; cryptographic file hashes alone do not establish authorship.
4. Proposed negative test: synthetic child emits structurally correct ACK/COMMITTED without applying state. **NOT_RUN**; no test permission inferred.
5. E5B4D remains NO-GO regardless of ACK-02 remediation.

**Gates unchanged:** E5B4D_NO-GO; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO; no main merge.
