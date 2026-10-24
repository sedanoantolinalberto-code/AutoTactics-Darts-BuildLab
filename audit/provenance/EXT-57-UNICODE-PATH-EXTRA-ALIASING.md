# EXT-57 — Unicode Path extra-field (0x7075) aliases and NUL truncation

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | ISOLATED_CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Concrete EXT-56 false acceptance

EXT-56's bounded ZIP preflight checks that local/central **raw** filename bytes agree and rejects NUL in those raw names. It permits well-formed extra TLVs other than ZIP64 without inspecting their semantics. The Info-ZIP **Unicode Path** extra field `0x7075` is not semantically inert: Python 3.13.5's `ZipInfo._decodeExtra` recognizes a version-1 field with a CRC32 matching the raw filename, selects its alternate UTF-8 name and sanitizes it at NUL.

On temporary synthetic v040-like ZIPs with unchanged synthetic payload bytes, self-consistent member-manifest hashes and **synthetically** recalculated outer ZIP SHA-256 anchors, EXT-56 returned **PASS** for:
- Raw `VERIFY_V040.py` plus `0x7075` alternate `VERIFY_V040.py\0TAIL`.
- Raw `MANIFEST_V040_SHA256.json` plus `0x7075` alternate `MANIFEST_V040_SHA256.json\0TAIL`.
- Raw `VERIFY_V040.py` plus alternate `VERIFY_V040.py\0../OUTSIDE`.
- Two Unicode Path extra fields, with the final alternate carrying the same NUL alias.

Here `\0` denotes an actual embedded NUL in the *alternate* filename's UTF-8 bytes; the raw header name contains no NUL. This is **strict canonical-name profile ambiguity**, not SHA-256 collision, historical archive modification, extraction path traversal or Darts-code exploitation.

## Isolated candidate and differential outcomes

The EXT-57 source-only candidate introduces a single fail-closed check inside the bounded central/local extra TLV parser: reject tag **`0x7075`** as **`ZIP_UNICODE_PATH_EXTRA_UNSUPPORTED`**, before `ZipInfo` creation or independent compressed-stream scanning. ZIP64 and malformed TLV protections, full-stream checks and previous validations remain unchanged.

The no-field canonical ZIP, benign unrelated Unicode-comment tag `0x6375`, and well-formed unknown tag `0x9999` remain accepted. Even a *legitimate and unambiguous* `0x7075` alternate matching the raw name is rejected deliberately: the historical strict profile disallows alternate name sources rather than attempting cross-parser compatibility.

| Scope | Python 3.13.5 Linux | Python `-O` |
| --- | ---: | ---: |
| Original EXT-56 85-case suite, unmodified verifier | **85/85** | **85/85** |
| EXT-57 85 earlier + 12 new synthetic cases | **97/97** | **97/97** |
| EXT-57 clean extraction and rerun | **97/97** | **97/97** |

All 12 cases compare the actual EXT-56 and EXT-57 verdicts, plus separately instrument whether DEFLATE stream scanning is reached; 9 additional `0x7075` cases (including four direct false-PASS examples) reject before scanning. The three benign ZIP/TLV controls continue to scan and return PASS. No Darts code or original historical archives were used.

## Evidence

`EngineYT_Darts_EXT57_Unicode_Path_Aliasing_Evidence_20261025.zip`:
- **SHA-256 `de8a547a3628dcabfac76a41eecb3669152bd73f615c6d2fb5900d256322e8bb`**, **22 files**; ZIP CRC and per-member SHA-256 inventory verified.
- Candidate verifier SHA-256 **`6e01a2877c0c092a037601075810aeaedac9d59d66d0a91c252ad450e8c2d42e`**.
- 97-case regression SHA-256 **`a32636e8235b558f266c3907dc23727b70645bf7eff348ebe01d07557fe9192e`**.
- Normal replay SHA-256 **`d2bc6be811a436e8a0366135fb0653c0d073d7923433b1492519abcbd66eeffd`**; optimized replay SHA-256 **`39dd37a4ea5c1627a0579c2e7c69e16bb54eddf59a380253ddcea26323f6be85`**.
- Includes candidate, prior independent baselines, original and extended synthetic suites, replayed JSON results, minimal diff-build scripts, review and package manifest. Historical ZIPs are **not redistributed**.

Reference: [Info-ZIP Unicode Path field specification (tag 0x7075)](https://sources.debian.org/src/zip/3.0-6/proginfo/extrafld.txt/) and [Python ZIP handling](https://github.com/python/cpython/blob/3.13/Lib/zipfile/__init__.py).

## Limitations / gates unchanged

**Seven immutable historical ZIP originals v040/v041/v042/v043/v050/v052/v053 NOT_RUN** against EXT-57; 653 historical member hashes and historical-dependent full regression **NOT_RUN** with this candidate. Earlier 7/7 historical PASS_LIMITED does not transfer. Before integration this new strict policy requires archive-compatibility review; no general ZIP interoperability or Windows parity is asserted. Independent anchor provenance (#12), ZIP resource/parser review (#13), decompression resource review (#14), formal RAM/CPU bounds and the 120-second Policy B under OS suspension model M remain OPEN/UNPROVEN.

**CANDIDATE_NOT_APPLIED. E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** No Darts project workers, tests, renderer, publishing, production integration or main merge.
