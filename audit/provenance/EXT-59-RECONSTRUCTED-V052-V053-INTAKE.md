# EXT-59 — Owner-supplied reconstructed v052/v053 intake and EXT-58 compatibility

**2026-10-25 | STATIC_REPRODUCED_RECONSTRUCTION | PASS_LIMITED_RECONSTRUCTED | HISTORICAL_IDENTITY_NOT_ATTESTED | HISTORICAL_ORIGINALS_NOT_RUN | DARTS_NOT_RUN | NOT_APPLIED**

## Inputs provided by owner

Three newly supplied standalone ZIP files, inspected read-only without importing/executing any Darts project modules:

| Uploaded artifact | Size (B) | SHA-256 | ZIP entries | ZIP CRC |
| --- | ---: | --- | ---: | --- |
| `v052_reconstructed_for_test.zip` | 100346 | `08ea80ebe9652fadd587d458aa1dda100ed7391bd4a24ca94b4b4b8ae2fbfb61` | 55 | PASS |
| `EngineYT_Darts_S34_v053_RECONSTRUIDA_DESDE_v054_SOURCE_ONLY.zip` | 123765 | `e5a243bf2b506cb18ea2eb15ff5bcb71574bfe425f7513b65575dd3c99392f55` | 66 | PASS |
| `EngineYT_S34_v053_RECONSTRUIDA_ENTREGA.zip` | 212230 | `020496d8b2645edced41d8a5c215e26213327cd6cac51b227a4fdc562e231b02` | 11 | PASS |

The delivery ZIP embeds **byte-for-byte identical copies** of both separate reconstructed ZIPs; its `SHA256SUMS.txt` matches all ten other delivery members.

## Byte-level and manifest observations

- Reconstructed v052's `MANIFEST_SHA256_V052.json.sha256` covers **all 54** non-manifest members; **54/54 actual decompressed content SHA-256 values match**.
- Reconstructed v053's `MANIFEST_SHA256_V053.json.sha256` covers **all 65** non-manifest members; **65/65 actual SHA-256 values match**.
- **Every one of the 55 bytestring members** of reconstructed v052 appears **byte-for-byte identically**, with `baseline_v052/` path prefix, inside reconstructed v053. No difference in member payloads found.
- Both outer reconstructed ZIPs use DEFLATE exclusively, all general-purpose flags 0, no extra fields, and matching DOS timestamps (2026-10-23 00:00:00) for their local listings.
- These are **reconstructed container bytes**; no direct access to original v054 was provided to independently verify the delivery report's claim that the v053 member payloads were copied from an authentic v054 ZIP.

## Independent external verifier proof

Using the previously documented isolated `EXT58_ASi_Unix_Extra_Candidate.py` **SHA-256 `208003cbf539afadcd26394a1e332a3d7f93cd65cba3e2eb948e3a1f63336985`**, invoked only as an independent archive-verifier module, with actual reconstructed ZIP SHA-256 and the target-script SHA-256 bound to each reconstructed version's embedded manifest:

| Version | Independent `verify_one` | Members checked | Manifest bytes SHA-256 |
| --- | --- | ---: | --- |
| reconstructed 052 | PASS | **54/54** | `5920e48b634c0ee3dd9163859feaa107f2e1bec364144864648b7f62969f9919` |
| reconstructed 053 | PASS | **65/65** | `abf1291c933ad538b0b855c987d2bea5558c8983c7b4a3465f662994d2d5e7bf` |

**Total reconstructed files checked: 119/119.** The strict local/central, resources, bounded full-stream, ZIP metadata and internal SHA-256 checks of isolated EXT-58 passed for both. A two-archive diagnostic run of `verify_one` is **not** the seven-version `verify()` scope test, and cannot be reported as 2/7 authenticated historical originals.

## Historical anchors are different

Original registered v052 SHA-256: `f446f961f8f93730a7d431e86ebb0533cf02fe99582808cd332d9dc8a31063f9`.

Original registered v053 SHA-256: `05684c26768e19ed46b771be992672704dfc5886b23df476487003f344f50145`.

While each reconstruction happens to match its original outer **size and number of ZIP entries**, the computed outer SHA-256 differs, so neither reconstruction is a byte-identical original. Do not overwrite the registered historic hashes. Five other historical originals v040/041/042/043/050 and both exact originals v052/053 remain **NOT_RUN** against EXT-58.

## Separate owner-provided documentary claims

The reconstructed delivery contains `PROVENIENCIA.json`, `INFORME.md`, `REGRESION_RECONSTRUIDA.json`, `REGRESION_INICIAL_FAIL.json`, and `REPRODUCCION_LIMPIA.json`. They report deriving the 66 v053 files from v054 (registered SHA `c1877e86179cb1d3e6ef5d69df62e0518b38aac04853742bac72d1c875bd9f5d`) and a clean **912-frame/40-additional-check** limited replay after a Windows CRLF/LF patch adaptation. This claim is **DOCUMENTARY_REPORTED**, not a newly independently rerun functional or transport test; the initial FAIL remains preserved. The purported original v054 byte stream was not provided in this intake. No Darts execution is inferred.

## Governance

- **PASS_LIMITED_RECONSTRUCTED** means verified *internal coherence of the owner-supplied reconstructed bytes*, not external custody or original-archive identity.
- Do not add reconstructed archives or package data to the Git repository without separate sensitive-data/licensing review. This commit registers only hashes and non-sensitive audit observations.
- Source authentication remains issue #12; independent ZIP preflight/resource review issue #13; decompression resource issue #14 remain **OPEN**.
- **E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO** unchanged.
- No original archive modified, no Darts module imported/executed, no project functional tests, no rendering, publishing, production integration or `main` merge.
