# EXT-46 — ZIP local/central metadata consistency and data-descriptor profile

**Date:** 2026-10-24. **Status:** SYNTHETIC_REPRODUCED / PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Seven reproducible false acceptances in EXT-45's declared strict profile

EXT-45 verifies ZIP local/central filenames and ZIP64/extra-field metadata but fails to compare six local-header fields against their central-directory equivalents. Python's `zipfile` uses central-directory metadata and accepts a local mismatch. Six separate, temporary synthetic v040 copies, each changing one local field while updating only the *synthetic outer ZIP SHA-256 anchor*, all returned `PASS` under EXT-45:

1. Local CRC-32 mismatch.
2. Local compressed-size mismatch.
3. Local uncompressed-size mismatch.
4. Local compression-method mismatch.
5. Local general-purpose flags mismatch (including spurious encryption bit).
6. Local version-needed mismatch.

A seventh ZIP created with standard-library non-seekable output uses streaming **data descriptors** (general-purpose bit 3) and also passed EXT-45. Such ZIPs are valid generally but **outside this verifier's narrow canonical historical ZIP profile**. Rejecting them is an explicit policy choice, not a claim they are malicious.

## Isolated EXT-46 correction

Before invoking `zipfile.ZipFile`, use the already bounded immutable snapshot to compare local/central version-needed, flags, compression method, CRC-32, compressed and uncompressed sizes. Mismatch returns `ZIP_LOCAL_HEADER_MISMATCH`. General-purpose bit 3 returns `ZIP_DATA_DESCRIPTOR_UNSUPPORTED`. Keep prior ZIP64/extra-field, EOCD, entry count, JSON, symlink, inventory and all-member hash checks.

| Run | Passed | Total |
| --- | ---: | ---: |
| EXT-45 on expanded battery | **51** | 58 |
| EXT-46 | **58** | 58 |
| EXT-46 with `python -O`, including verifier subprocesses | **58** | 58 |
| Seven immutable original ZIPs | **7/7 PASS_LIMITED** | **653/653 member hashes** |

Original seven ZIPs have matching local/central fields and no streaming descriptors in this observed set. No originals modified.

## Evidence

`EngineYT_Darts_EXT46_Local_Central_Header_Evidence_20261024.zip` SHA-256 **`f4cc3cca62814c06b0df92560cd4b715a97266ce3fbae496206ed9b2d4a58fdf`**, 10 members, ZIP CRC and per-member manifest SHA-256 PASS. Includes candidate verifier SHA-256 `244213499d3f39f2e23bff25798a0696fdd4b31aa9f60c173946fd5f593e7bad`, 58-case harness SHA-256 `0a4de93a35cf3a5b027f3b5dab221efe37ac316034448d9d8dfa9c77fc520650`, original inventory, pre-fix/normal/optimized/historical outputs, differential report, review and package manifest. The seven historical ZIPs and temporary synthetic mutated copies are **not redistributed**.

## Remaining proof obligations

Independent historical archive authenticity is still unproven (issue #12). ZIP resource/parser independent review remains open (issue #13). A strict canonical single-disk non-ZIP64 no-data-descriptor profile is not a general ZIP validator; 58 tests do not prove worst-case bounds. Windows SEC-02 NOT_RUN; Policy B under arbitrary OS suspension model M still NO-GO.

No Darts modules, workers, project tests, main merge, render, publication or integration. **E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**