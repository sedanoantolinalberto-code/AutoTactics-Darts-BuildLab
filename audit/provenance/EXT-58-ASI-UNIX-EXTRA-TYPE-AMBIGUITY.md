# EXT-58 — ASi Unix ZIP extra-field file-type ambiguity

**2026-10-25 | SYNTHETIC_REPRODUCED | PASS_LIMITED_SYNTHETIC | ISOLATED_CANDIDATE_NOT_APPLIED | HISTORICAL_NOT_RUN | DARTS_NOT_RUN**

## Falsifiable EXT-57 strict-profile false acceptance

EXT-57's external ZIP verifier rejects Unix symlinks, devices and other unsafe file types when the **central creator-system is 3** and `external_attr` encodes a special Unix mode. It nevertheless permits well-formed extra fields other than ZIP64, Unicode Path 0x7075 and malformed TLVs, including **ASi Unix `0x756E`**. This particular extra field is **not inert**: it contains a CRC-32 and Unix `st_mode` describing permissions, symlinks and special files (plus an optional link target). ZIP tools may interpret that alternative metadata even when Python 3.13.5 `zipfile.ZipInfo` uses the central creator-system/external attributes instead.

Five synthetic v040-like archives with **ordinary regular-file central attributes** (creator-system 0) and **valid ASi Unix extra-field CRC** contained alternate Unix modes for symlink (target `../../outside`), directory, character device, block device, and FIFO. All **five returned PASS in EXT-57**, which trusts the central attributes, although ASi Unix metadata contradicts the file type asserted by the strict audit profile. The source-only verifier **never extracts** those samples; this is a metadata/cross-parser ambiguity, not a demonstrated filesystem escape. ZIP/member/manifest SHA-256 anchors were **synthetically** recomputed and do not establish historical authenticity.

## Isolated correction

EXT-58 adds one fail-closed rule to EXT-57's **bounded local/central extra-field TLV preflight**: reject tag `0x756E` as `ZIP_ASI_UNIX_EXTRA_UNSUPPORTED` **before** invoking `ZipInfo` or independent compressed-stream scans. The rule conservatively rejects even an ASi field describing a regular file (intentional narrow-profile policy). Canonical archives with no ASi extra and unrelated unknown tag `0x9999` remain accepted. All EXT-57 Unicode Path 0x7075 and other safeguards remain.

| Synthetic run | Normal | `python -O` |
| --- | ---: | ---: |
| EXT-57 original suite (preserved within EXT-58) | **97/97** | **97/97** |
| EXT-58 97 previous + 9 new cases | **106/106** | **106/106** |
| EXT-58 clean extraction and identical replay | **106/106** | **106/106** |

Nine targeted cases: five unsafe alternate Unix modes; one otherwise harmless regular-file ASi field (rejected intentionally); one ASi field with invalid CRC (also rejected on tag); and two positive controls. Actual EXT-57/58 `verify_one` verdicts were compared alongside separately instrumented DEFLATE stream-entry probes. Synthetic source-only tests ran under **Python 3.13.5 Linux**, with no Darts imports/workers or original archive bytes.

## Reproducible package and exact hashes

`EngineYT_Darts_EXT58_ASi_Unix_Extra_Evidence_20261025.zip`: **SHA-256 `6b99221ad5a0f894613f52f2c0a1938896af308192b69e80babc13877bc07687`**, **30 flat members**, ZIP CRC and SHA-256 per-member evidence manifest confirmed.

- EXT-58 standalone candidate SHA-256 `208003cbf539afadcd26394a1e332a3d7f93cd65cba3e2eb948e3a1f63336985`.
- EXT-58 synthetic harness SHA-256 `9260e187bdcabe1972a8d14c5a2886fe1bbc1185bb95eb56fb7fad38c6086430`.
- Captured normal and optimized 106-case JSON replayed byte-for-byte identically after independent clean extraction.
- Package includes earlier external-verifier baselines, EXT-57/58 candidates, source-generation scripts, synthetic regressions, normal/-O JSON results, reviews and SHA-256 manifest. No seven historical ZIPs are redistributed.

References: [ASi Unix metadata layout](https://sources.debian.org/src/zip/3.0-6/proginfo/extrafld.txt/) and [Apache Commons Compress AsiExtraField implementation](https://commons.apache.org/proper/commons-compress/apidocs/src-html/org/apache/commons/compress/archivers/zip/AsiExtraField.html).

## Non-transferable limits and gates

The **seven immutable historical ZIPs v040/v041/v042/v043/v050/v052/v053 and 653 member hashes are NOT_RUN with EXT-58**; prior historical results cannot transfer. Valid ZIPs using legitimate ASi Unix fields are **outside** the proposed narrow profile, and historical compatibility is unverified. No independent historical custody anchors (#12), complete ZIP/parser resource review (#13), worst-case decompression/OS limits (#14), Windows parity, model-M Policy B deadline guarantee, worker tests, rendering or publishing.

**Candidate NOT_APPLIED; E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** No Darts runtime, project tests, integration or `main` merge.
