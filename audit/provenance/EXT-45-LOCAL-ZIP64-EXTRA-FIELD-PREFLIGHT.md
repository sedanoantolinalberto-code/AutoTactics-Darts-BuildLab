# EXT-45 — Local ZIP64 and extra-field preflight regression

**2026-10-24 | SYNTHETIC_REPRODUCED | PASS_LIMITED | ISOLATED_CANDIDATE_NOT_APPLIED | DARTS_NOT_RUN**

## New falsifiable EXT-44 defects

EXT-44 preflights the EOCD and central directory to bound ZipInfo allocation but claimed a strict **non-ZIP64** profile without inspecting referenced local file headers or extra-field TLVs. Three temporary synthetic v040 repacks, with **unchanged member payloads** and updated *synthetic* outer SHA-256 anchors, passed EXT-44 `verify_one`:

1. **Local-only forced ZIP64:** `ZipFile.open(..., force_zip64=True)` writes a ZIP64 local header even though EOCD/central sizes are ordinary. EXT-44 `PASS`; EXT-45 `ZIP64_UNSUPPORTED`.
2. **Unused ZIP64 extra TLV:** Tag `0x0001`, zero payload, accepted by EXT-44; EXT-45 `ZIP64_UNSUPPORTED`.
3. **Malformed local extra TLV:** Tag `0x9999` claims 65,535 bytes while only four bytes exist. EXT-44 `PASS`; EXT-45 `ZIP_EXTRA_FIELD_INVALID`.

A well-formed unknown `0x9999` zero-length extra field is still accepted by EXT-45. These are structural/profile-conformance failures, **not** a SHA-256 collision, original archive modification, or Darts execution.

## Isolated correction

Within the already captured immutable ZIP bytes, **before Python ZipFile parses the central directory**, walk each bounded central record, inspect its referenced local file header, verify central/local raw filenames, reject ZIP64 sentinel sizes/offsets and ZIP64 tag `0x0001` in both extra-field locations, and reject malformed TLV boundaries. The strict canonical single-disk non-ZIP64 profile is intentional and not a general ZIP compatibility guarantee.

| Candidate | Passed | Total |
| --- | ---: | ---: |
| EXT-44 with four new tests | **48** | 51 |
| EXT-45 | **51** | 51 |
| EXT-45 under `python -O` (also propagated to subprocesses) | **51** | 51 |
| Seven original immutable ZIPs | **7/7 PASS_LIMITED** | **653/653 hashes** |

All seven historical archive bytes still match their existing local inventory SHA-256 values; these anchors remain **independently unauthenticated**.

## Evidence and gates

`EngineYT_Darts_EXT45_Local_ZIP64_Evidence_20261024.zip` SHA-256 **`7e113c51832e057fa437c2af22f337bc8c90f89fb7b35b3cee7cbe589d43ba41`**, **10 members**, ZIP CRC and per-member SHA-256 PASS. Includes candidate (SHA-256 `66e47b49e259410f256369f54819868b1392c47c9b18cbd34a26c8e54da72202`), 51-case harness (SHA-256 `a121e000437e528fdd519a6f7e923c5deb2efafc534c9c82c73271bf7f34d799`), inventory, pre-fix/normal/optimized results, historical result, differential JSON, review and package manifest. Original seven ZIPs are **not** redistributed.

**Open:** issue #13 (independent ZIP preflight/resource review) and issue #12 (independent provenance anchors). Tests are not a worst-case memory bound, formal parser proof, or Windows parity. No Darts modules, workers, project tests, main merge, render, publication or production integration.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**