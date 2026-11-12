# ENGINE YT — R11 / PR #16 F3 Cross-Audit (REVIEW ONLY)

**2026-11-12** · No merge · No release · No qualification.

## Claude T21-R11 (user-supplied report; **not independently verified**)

- Local HEAD abbreviated `eb0e122`, branch `work/t21-r11-codex-reconciliation`.
- 14/14 original Codex tests reported PASS only with **explicit** `codex-r09/1` compatibility view. Default output reported: 8 PASS / 2 FAIL / 4 ERROR. Persisted record format remains canonical v2.
- Matrix reported: root 821 PASS / 5 FAIL; uid65534 816 PASS / 5 FAIL / 5 SKIP; five R08 failures remain.
- `inspect_run` reportedly uses `validate_record` for all records; WAL retained Claude's independently hardened read/inode validation. 
- Claude reports bundle verification, CRC and 82 hashes, but did **not** reconstruct bundle tree. These checks remain independent-review pending.
- `EngineYT_T21_R11_ReviewOnly.zip` was reported as existing in Claude's `/mnt/user-data/outputs`, but **was not attached to this chat or published in GitHub**. This document cannot certify its contents.
- No GitHub push is recommended until independent ZIP validation, correct remote identity, branch isolation and secret/permissions review.

## F3: two independent defect classes in the old PR #16

1. A modified case ID such as `official:FORGED17` or one from the wrong suite was accepted if unique, counts and SHA-256 matched.
2. A reused log path or digest was not explicitly classified as duplicate; depending on expected counts it failed later for other reasons, not with unambiguous duplicate-reference validation.

### Before correction: native CI RED reproduced

- GitHub Actions `43227459936`: **4 FAIL** of exactly the four F3 tests, with no need to modify the code under test or trust a claim.
- Two false acceptances produced `None != LOG_CASE_SET_MISMATCH`.
- Two duplicate-reference cases produced different rejection classes, rather than `DUPLICATE_LOG_REFERENCE`.

### After correction: native CI GREEN

- File: `experiments/r09-linux-closure/matrix_policy.py`.
- Receipt contract moves from `engineyt-r09-suite-receipts/0.2` to `0.3`.
- The **synthetic reference-only** suite IDs are pinned as `{suite}:{0000..count-1}`, compared as a complete set, not trusted because of unique syntax.
- Duplicate log paths or digests are rejected before reading.
- Original four F3 regression tests preserved byte-for-byte after RED.
- GitHub Actions run `43227649204`, job `131214902877`: **61/61 PASS** for each of runner UID1001, root UID0 and UID65534, plus **four explicitly selected kernel semantics tests**, **187/187 PASS**. 0 FAIL/SKIP.
- Specific F3 tests observed PASS in runner log.

### Boundary: cannot authenticate native T21 cases

The pinned synthetic IDs are lab fixtures only, **not** real authoritative T21 test IDs. A malicious producer who can generate both log and receipt can fabricate an internally consistent fixture; no cryptographic signing or trustworthy, independently pinned producer identity exists here. Native `OBSERVED_NATIVE` receipts remain `BLOCKED_UNATTESTED_NATIVE_PROVENANCE`.

To qualify real R11, obtain the complete R11 ZIP; verify CRC, signed or external digest if available, git bundle/tree and logs; inspect the exact v2/codex-r09/1 adapter code, and run 14 Codex tests with explicit view and default view against an isolated reconstructed R11. Compare all original R08 5 FAIL, and separately inspect env-var precedence/contamination.

## Unchanged gates

`R17/E5B4D = NO-GO`; `TB09/G3 = BLOCKED`; full descendant containment `BLOCKED`; rendering and publication disabled. No merge or production action permitted.
