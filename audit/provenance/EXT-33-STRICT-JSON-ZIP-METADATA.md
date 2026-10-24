# EXT-33 — Strict external archive verifier: duplicate JSON keys and Unix special members

**Date:** 2026-10-24. **Evidence:** INDEPENDENT_VERIFIER_SYNTHETIC_REGRESSION. **Darts runtime:** NOT_RUN. **Status:** PASS_LIMITED / CANDIDATE_NOT_APPLIED.

## Two classes of independently reproduced EXT-32 acceptance gaps

1. **Ambiguous JSON mapping:** EXT-32's ordinary `json.loads` silently accepted duplicate `files` keys at the root of the embedded manifest and duplicate digest keys within the mapping. The same applies to the external inventory's root `files` key. Synthetic ZIPs with updated *synthetic* outer ZIP anchors were accepted (`PASS`), and the duplicate-inventory variant returned `PASS_LIMITED`. Identical duplicate values were used to isolate parser ambiguity, not digest forgery.
2. **Unix special file metadata:** EXT-32 accepted ZIP members marked as POSIX symlinks or FIFOs via `ZipInfo.create_system==3` and `external_attr`. It does not extract files, so this is an interoperability/metadata ambiguity, not demonstrated code execution or traversal.

## EXT-33 isolated candidate

- Strict JSON decoding with `object_pairs_hook` rejects duplicate keys at all nesting levels, in both inventory and embedded manifest. Embedded duplicate keys return `MANIFEST_DUPLICATE_JSON_KEY`.
- For POSIX ZIP entries, reject nonregular types `stat.S_IFMT(external_attr >> 16)` except type 0 (missing legacy metadata), preserving compatibility with original v052/v053 archives. Failure code `UNSAFE_UNIX_FILE_TYPE`.
- Candidate `EngineYT_Darts_EXT33_Strict_Archive_Verifier_20261024.py` SHA-256 `cbabad4d2282a1df4cb23a9c985323dbf7fa6d05eb24ae604af194e6cb45fba3`.

## Observed regression

- Original immutable ZIPs: **7/7 PASS_LIMITED**, **653/653** nonmanifest member hashes match, original hashes/archives unchanged.
- New differential synthetic regression: **7/7 PASS** (baseline, duplicate root mapping, duplicate nested digest, symlink, FIFO, regular-file control, duplicate inventory root).
- Original EXT-32 negative cases against EXT-33: **8/8 PASS**.
- No Darts modules imported, no worker or project tests run. Synthetic ZIP creation and standalone external verifier execution only.

**Package:** `EngineYT_Darts_EXT33_Strict_External_Verifier_Evidence_20261024.zip` SHA-256 `93e0919274da10c2ca9c25a110ffad77aa2a562283ac988c071cc6053aa6da43`; nine members; CRC and manifest hashes PASS. Includes verifier, both harnesses/results, 7-ZIP results, OPT-30 inventory, review and package manifest.

## Limits and remaining gates

External input SHA-256 anchors still lack an independently authenticated custody/signing source. The POSIX metadata policy and legacy missing-type allowance require explicit review. ZIP parser robustness and resource bounds are not formally proved; no strict physical process deadline guarantee under arbitrary OS suspension.

**E5B4D_NO-GO, ACK-02 OPEN, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO.** No production code integration or merge to main.
