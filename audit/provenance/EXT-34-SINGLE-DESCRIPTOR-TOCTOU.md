# EXT-34 — Single-descriptor ZIP verification (TOCTOU)

**Date:** 2026-10-24. **Evidence:** SYNTHETIC_DIFFERENTIAL_REPRODUCED. **Status:** PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Confirmed EXT-33 flaw

EXT-33 hashes a ZIP using `path.open('rb')`, closes the handle, and then separately reopens `zipfile.ZipFile(path, 'r')`. A directory-entry swap between those operations allows it to report the SHA-256 of ZIP A while verifying the contents and embedded manifest of ZIP B. This is an **outer-hash/content TOCTOU mismatch**, not evidence that historical archives were compromised.

## Controlled reproduction

An isolated harness constructs two individually consistent synthetic ZIPs, A and B. B contains an altered non-target member and a corresponding updated embedded manifest. The harness atomically replaces the path with B when the verifier reaches `ZipFile`.

- **EXT-33:** PASS, outer SHA-256 of A, embedded manifest SHA-256 of B.
- **EXT-34:** PASS, outer SHA-256 and embedded manifest SHA-256 both from A.
- **Historical baseline:** seven of seven immutable ZIPs PASS_LIMITED; **653/653** non-manifest member hashes matched.
- **Darts runtime:** no modules imported or executed; no worker launched.

## Candidate correction

Open the archive once; use `os.fstat(fh.fileno())` to check size; hash the same file descriptor; `fh.seek(0)`; then `zipfile.ZipFile(fh, 'r')` while retaining the descriptor until all members are checked. This removes the **path-reopen** window, but not concurrent in-place writes to an already opened inode.

## Deliverable

`EngineYT_Darts_EXT34_Single_Descriptor_Evidence_20261024.zip`, SHA-256 `c81e70ed9db50e9cb9a89dcd8b2a15844d27d7acb951349d8b3747aa98229773`. Five members: isolated candidate, synthetic builder/harness, JSON results, review, SHA-256 manifest. CRC and manifest member hashes PASS. Candidate Python AST parse PASS.

## Residual proof obligations

1. Independent code review of descriptor lifetime and error handling.
2. Decide if immutable trusted storage or snapshot-copy is required to prevent **same-inode in-place mutation**.
3. Do not promote supplied ZIP hashes to externally authenticated provenance.
4. Do not claim physical OS deadlines or Policy B under model M.
5. Keep the candidate unapplied until a separate integration decision.

**E5B4D_NO-GO, ACK-02 OPEN, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO.** No main merge, project execution, media render or publication.
